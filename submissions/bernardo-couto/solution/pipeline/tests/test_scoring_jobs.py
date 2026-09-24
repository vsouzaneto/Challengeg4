"""Rules layer and ``score`` job on the real gold partitions (point-in-time, idempotency).

These tests need ``build-features`` (gold on disk) and ``train`` (``models/latest``) to have
run; they are skipped otherwise so ``pytest`` stays green on a fresh clone.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import date
from pathlib import Path

import pandas as pd
import pytest
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from lead_scorer.config import GOLD_DIR, MODELS_DIR, SILVER_DIR
from lead_scorer.data import gold
from lead_scorer.jobs import artifacts
from lead_scorer.jobs import score as score_job
from lead_scorer.ml.evaluate import spearman
from lead_scorer.scoring.score import SCORED_DEAL_COLUMNS, score_frame

T_SEP = date(2017, 9, 30)
SNAPSHOT = date(2017, 12, 31)

needs_gold = pytest.mark.skipif(
    not artifacts.gold_partition_exists(gold.FEATURES_TABLE, SNAPSHOT, GOLD_DIR)
    or not artifacts.gold_partition_exists(gold.HISTORY_TABLE, T_SEP, GOLD_DIR)
    or not (SILVER_DIR / "opportunities").is_dir(),
    reason="gold/silver not built (run build-features)",
)
needs_model = pytest.mark.skipif(
    not (MODELS_DIR / artifacts.LATEST_POINTER).is_file(),
    reason="models/latest missing (run train)",
)


def _as_dict(reason: object) -> dict[str, object]:
    """Spark ``Row`` (toPandas) or dict (pyarrow read_parquet)."""
    if hasattr(reason, "asDict"):
        return {str(k): v for k, v in reason.asDict().items()}
    return {str(k): v for k, v in dict(reason).items()}  # type: ignore[call-overload]


def _hash_rows(pdf: pd.DataFrame) -> str:
    ordered = pdf.sort_values("opportunity_id").reset_index(drop=True)
    plain = ordered.drop(columns=["reasons"])
    h = hashlib.sha256(pd.util.hash_pandas_object(plain, index=False).to_numpy().tobytes())
    reasons = json.dumps(
        [[_as_dict(r) for r in rs] for rs in ordered["reasons"]], default=str, sort_keys=True
    )
    h.update(reasons.encode())
    return h.hexdigest()


@needs_gold
def test_snapshot_batch_invariants(spark: SparkSession) -> None:
    features = artifacts.read_gold(spark, gold.FEATURES_TABLE, SNAPSHOT, GOLD_DIR)
    history = artifacts.read_gold(spark, gold.HISTORY_TABLE, SNAPSHOT, GOLD_DIR)
    scored = score_frame(features, history, as_of=SNAPSHOT, model_version="t").toPandas()
    assert len(scored) == features.count() == 2_089  # no open deal without a score
    assert list(scored.columns) == list(SCORED_DEAL_COLUMNS)
    for col in ("priority_score", "p_win", "urgency", "expected_value", "tier", "confidence"):
        assert scored[col].notna().all(), col
    assert scored["priority_score"].between(0, 100).all()
    rho = spearman(scored["priority_score"].to_numpy(), scored["sales_price"].to_numpy())
    assert rho < 0.9 and abs(rho - 0.46) < 0.02  # not "sort by price"; matches the prototype
    zombie = scored["days_in_engaging"] > 138
    assert int(zombie.sum()) == 1_291
    assert scored.loc[zombie, "tier"].isin(["C", "D"]).all()
    assert scored.loc[zombie, "priority_score"].max() <= 49.0
    assert scored["tier"].value_counts().to_dict() == {"C": 771, "D": 735, "B": 516, "A": 67}
    parts = pd.DataFrame(list(scored["score_breakdown"].map(lambda b: b.asDict())))
    assert (parts.sum(axis=1) - scored["priority_score"]).abs().max() < 0.01
    assert scored["confidence"].value_counts().to_dict() == {
        "baixa": 1629,
        "media": 372,
        "alta": 88,
    }
    # ordering contract: score desc, then newest zombie first
    diffs = scored["priority_score"].diff().dropna()
    assert (diffs <= 1e-9).all()


@needs_gold
def test_point_in_time_future_close_does_not_change_scores(spark: SparkSession) -> None:
    """Injecting a deal closed after T into the history input leaves score(as_of=T) unchanged."""
    opps = spark.read.parquet(str(SILVER_DIR / "opportunities"))
    features = artifacts.read_gold(spark, gold.FEATURES_TABLE, T_SEP, GOLD_DIR)
    base_hist = gold.compute_history(opps, T_SEP)
    future = (
        opps.filter(F.col("deal_stage") == "Won")
        .limit(50)
        .withColumn("opportunity_id", F.concat(F.lit("FUT"), F.col("opportunity_id")))
        .withColumn("engage_date", F.lit(date(2017, 9, 1)))
        .withColumn("close_date", F.lit(date(2017, 11, 15)))  # leakage-ok: test injects future
        .withColumn("close_value", F.lit(999_999.0))  # leakage-ok: test injects future
    )
    injected_hist = gold.compute_history(opps.unionByName(future), T_SEP)
    a = score_frame(features, base_hist, as_of=T_SEP, model_version="t").toPandas()
    b = score_frame(features, injected_hist, as_of=T_SEP, model_version="t").toPandas()
    assert _hash_rows(a) == _hash_rows(b)


@needs_gold
@needs_model
def test_score_job_is_idempotent_and_validates_contract(
    spark: SparkSession, tmp_path: Path
) -> None:
    gold_dir = tmp_path / "gold"
    for table in (gold.FEATURES_TABLE, gold.HISTORY_TABLE):
        shutil.copytree(
            artifacts.gold_partition(table, T_SEP, GOLD_DIR),
            artifacts.gold_partition(table, T_SEP, gold_dir),
        )
    first = score_job.run(T_SEP, spark=spark, gold_dir=gold_dir, models_dir=MODELS_DIR)
    h1 = _hash_rows(pd.read_parquet(first.output_dir))
    second = score_job.run(T_SEP, spark=spark, gold_dir=gold_dir, models_dir=MODELS_DIR)
    h2 = _hash_rows(pd.read_parquet(second.output_dir))
    assert h1 == h2
    written = pd.read_parquet(second.output_dir)
    assert len(written) == 2_409  # overwrote, did not append
    assert score_job.validate_rows(written) == 2_409
    manifest = json.loads((second.output_dir / gold.MANIFEST_NAME).read_text())
    assert manifest["counts"]["rows"] == 2_409 and manifest["counts"]["zombies"] == 530
    zombie = written["days_in_engaging"] > 138
    assert manifest["values"]["zombie_nominal_value"] == pytest.approx(
        written.loc[zombie, "sales_price"].sum(), abs=0.01
    )
    assert set(manifest["psi"]) >= {"log_days", "log_price", "product"}
    assert manifest["model_version"] == first.model_version
    assert manifest["blend_model_weight"] == 0.0
    assert set(manifest["raw_checksums"]) >= {"sales_pipeline.csv"}


@needs_model
def test_metrics_json_follows_spec_layout() -> None:
    model_dir = artifacts.resolve_model_dir(artifacts.LATEST_POINTER, MODELS_DIR)
    metrics = artifacts.read_json(model_dir / artifacts.METRICS_FILE)
    assert {
        "model_version",
        "as_of",
        "cuts",
        "summary",
        "backtest",
        "baselines",
        "promotion",
    } <= set(metrics)
    for key in (
        "coverage",
        "prospecting_count",
        "zombie_count",
        "account_known_rate",
        "mean_calibration_error",
        "spearman_score_price",
        "blend_model_weight",
    ):
        assert key in metrics["summary"], key
    for cut in metrics["cuts"]:
        b = metrics["backtest"][cut]
        for key in (
            "n_open",
            "n_labeled",
            "n_censored",
            "base_rate",
            "brier",
            "auc_pr",
            "auc_pr_ci",
            "auc_roc",
            "lift_top_decile",
            "precision_at_10",
            "precision_at_10_ci",
            "precision_at_25",
            "revenue_capture_top20",
            "revenue_capture_top20_ci",
            "calibration_bins",
        ):
            assert key in b, key
        assert len(b["calibration_bins"]) == 5
        assert b["zombies_closed_after"] == 0
        assert "revenue_14d_top20" in b and "revenue_30d_top10_agent_share" in b
        assert 0 <= b["top5_agent_share_120_138"] <= 1
        for name in ("random", "price", "price_alive", "newest", "oldest", "base_rate"):
            row = metrics["baselines"][name][cut]
            assert {
                "precision_at_10",
                "precision_at_10_ci",
                "auc_pr",
                "revenue_capture_top20",
            } <= set(row)
    assert metrics["promotion"]["blend_model_weight"] == metrics["summary"]["blend_model_weight"]
    assert metrics["acceptance"]["passed"] is True
    for name in (
        artifacts.MODEL_CARD_FILE,
        artifacts.FEATURE_LIST_FILE,
        artifacts.TRAINING_MANIFEST_FILE,
    ):
        assert (model_dir / name).is_file()
    assert "account_known" not in json.loads((model_dir / artifacts.FEATURE_LIST_FILE).read_text())
