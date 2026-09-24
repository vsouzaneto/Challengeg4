"""Layer-2 contracts: closed feature list, Spark ML pipeline round-trip, evaluation, promotion."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from lead_scorer.ml import evaluate, promotion
from lead_scorer.ml.drift import feature_distribution, psi_alerts, psi_report
from lead_scorer.ml.features import (
    FEATURES,
    FORBIDDEN,
    LABEL_COL,
    NUMERIC_FEATURES,
    add_ml_features,
    is_forbidden,
)
from lead_scorer.ml.frame import frame_months
from lead_scorer.ml.pipeline import PROB_COL, RAW_PROB_COL, ShadowModel, fit_shadow_model

PRODUCTS = ["GTX Pro", "MG Special", "GTK 500", "GTX Plus Basic"]


def _synthetic_gold_features(spark: SparkSession, n: int, seed: int) -> DataFrame:
    """Looks like ``opportunity_features`` (only the columns ``add_ml_features`` reads)."""
    rng = np.random.default_rng(seed)
    days = rng.integers(0, 200, n).astype(float)
    days[: n // 10] = np.nan  # some Prospecting rows
    pdf = pd.DataFrame(
        {
            "opportunity_id": [f"id{i}" for i in range(n)],
            "product": rng.choice(PRODUCTS, n),
            "win_rate_product": rng.uniform(0.55, 0.7, n),
            "global_win_rate": 0.63,
            "days_in_engaging": days,
            "sales_price": rng.choice([55.0, 550.0, 1096.0, 4821.0, 26768.0], n),
            "open_deals_agent": rng.integers(5, 80, n).astype(float),
            "win_rate_survival": np.where(np.isnan(days), np.nan, rng.uniform(0.5, 0.8, n)),
            "account_known": rng.random(n) < 0.3,
        }
    )
    pdf[LABEL_COL] = (rng.random(n) < 0.6).astype(float)
    df = spark.createDataFrame(pdf)
    return df.withColumn("days_in_engaging", F.col("days_in_engaging").cast("int"))


@pytest.fixture(scope="module")
def frames(spark: SparkSession) -> tuple[DataFrame, DataFrame, DataFrame]:
    train = add_ml_features(_synthetic_gold_features(spark, 400, 1)).cache()
    calib = add_ml_features(_synthetic_gold_features(spark, 120, 2)).cache()
    batch = add_ml_features(_synthetic_gold_features(spark, 150, 3)).cache()
    return train, calib, batch


# --- 9. closed feature list -----------------------------------------------------------------------


def test_feature_list_excludes_forbidden_columns() -> None:
    assert set(FEATURES) & FORBIDDEN == set()
    assert not any(is_forbidden(f) for f in FEATURES)
    for banned in ("account_known", "sector", "close_value", "close_date", "label", "engage_month"):
        assert is_forbidden(banned)
    assert ("product", *NUMERIC_FEATURES) == FEATURES


def test_model_vector_has_no_account_or_outcome_slots(
    frames: tuple[DataFrame, DataFrame, DataFrame],
) -> None:
    train, calib, _ = frames
    model = fit_shadow_model(train, calib)
    names = model.feature_names()
    assert len(names) == len(model.lr.coefficients)
    assert not any(
        is_forbidden(n.split("_", 1)[0]) or "account" in n or "close" in n for n in names
    )
    assert any(n.startswith("product") for n in names) and "log_price" in names


# --- pipeline behaviour ---------------------------------------------------------------------------


def test_predict_is_bounded_and_deterministic(
    frames: tuple[DataFrame, DataFrame, DataFrame],
) -> None:
    train, calib, batch = frames
    a = fit_shadow_model(train, calib)
    b = fit_shadow_model(train, calib)
    # Same data, no sampling stage -> same model up to LBFGS floating-point aggregation order.
    ca, cb = a.coefficients(), b.coefficients()
    assert ca.keys() == cb.keys()
    assert all(ca[k] == pytest.approx(cb[k], abs=1e-9) for k in ca)
    pa = a.predict(batch).select("opportunity_id", PROB_COL, RAW_PROB_COL).toPandas()
    pb = b.predict(batch).select("opportunity_id", PROB_COL, RAW_PROB_COL).toPandas()
    pd.testing.assert_frame_equal(
        pa.sort_values("opportunity_id"), pb.sort_values("opportunity_id"), atol=1e-9
    )
    assert pa[PROB_COL].between(0, 1).all() and pa[RAW_PROB_COL].between(0, 1).all()
    assert pa[PROB_COL].notna().all()  # Prospecting rows imputed, never dropped
    assert a.calibrator is not None


def test_save_load_round_trip(
    frames: tuple[DataFrame, DataFrame, DataFrame], tmp_path: Path
) -> None:
    train, calib, batch = frames
    model = fit_shadow_model(train, calib)
    model.save(tmp_path / "pipeline_model")
    loaded = ShadowModel.load(tmp_path / "pipeline_model")
    before = model.predict(batch).select("opportunity_id", PROB_COL).toPandas()
    after = loaded.predict(batch).select("opportunity_id", PROB_COL).toPandas()
    pd.testing.assert_frame_equal(
        before.sort_values("opportunity_id").reset_index(drop=True),
        after.sort_values("opportunity_id").reset_index(drop=True),
    )
    assert loaded.coefficients() == model.coefficients()


def test_unseen_product_is_kept_not_dropped(frames: tuple[DataFrame, DataFrame, DataFrame]) -> None:
    train, calib, batch = frames
    model = fit_shadow_model(train, calib)
    odd = batch.withColumn("product", F.lit("GTK 9000"))
    out = model.predict(odd)
    assert out.count() == batch.count()
    assert out.filter(F.col(PROB_COL).isNull()).count() == 0


# --- frame / drift --------------------------------------------------------------------------------


def test_frame_months_stop_one_month_before_cut() -> None:
    assert frame_months(date(2017, 6, 30)) == [
        date(2017, 3, 31),
        date(2017, 4, 30),
        date(2017, 5, 31),
    ]
    assert frame_months(date(2017, 12, 31))[-1] == date(2017, 11, 30)
    assert len(frame_months(date(2017, 12, 31))) == 9


def test_psi_is_zero_on_itself_and_flags_shift(
    frames: tuple[DataFrame, DataFrame, DataFrame],
) -> None:
    train, _, _ = frames
    pdf = train.select(*FEATURES).toPandas()
    ref = feature_distribution(pdf)
    same = psi_report(ref, pdf)
    assert all(v < 1e-6 for v in same.values())
    shifted = pdf.assign(log_price=pdf["log_price"] + 3.0, product="GTK 500")
    report = psi_report(ref, shifted)
    assert {"log_price", "product"} <= set(psi_alerts(report))


# --- evaluation and promotion ---------------------------------------------------------------------


def _eval_frame(n: int = 400, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    label = rng.random(n) < 0.6
    days = rng.integers(0, 250, n).astype(float)
    return pd.DataFrame(
        {
            "opportunity_id": [f"o{i:04d}" for i in range(n)],
            "sales_agent": rng.choice([f"agent{i}" for i in range(12)], n),
            "sales_price": rng.choice([55.0, 550.0, 4821.0, 26768.0], n),
            "days_in_engaging": days,
            "product_rate": rng.uniform(0.6, 0.66, n),
            "p_win": rng.uniform(0.55, 0.7, n),
            "expected_value": rng.uniform(30, 20000, n),
            "priority_score": rng.uniform(0, 100, n),
            "label": np.where(rng.random(n) < 0.7, label.astype(float), np.nan),
            "realized_value": np.where(label, rng.uniform(50, 20000, n), 0.0),
            "days_to_close": rng.integers(1, 120, n).astype(float),
            "p_model": rng.uniform(0.4, 0.8, n),
        }
    )


def test_evaluate_cut_matches_metrics_json_layout() -> None:
    result = evaluate.evaluate_cut(_eval_frame(), "2017-09-30", n_boot=50)
    b = result.backtest
    assert b["n_open"] == 400 and b["n_labeled"] + b["n_censored"] == 400
    for key in (
        "brier",
        "auc_pr",
        "auc_pr_ci",
        "lift_top_decile",
        "precision_at_10",
        "precision_at_10_ci",
        "precision_at_25",
        "revenue_capture_top20",
        "revenue_capture_top20_ci",
        "calibration_bins",
        "zombies_closed_after",
    ):
        assert key in b, key
    assert b["auc_pr_ci"][0] <= b["auc_pr"] <= b["auc_pr_ci"][1]
    assert set(result.baselines) == set(evaluate.BASELINES)
    assert "price_alive" in result.baselines
    assert "revenue_14d_top20_share" in b and "revenue_30d_top10_agent" in b
    assert 0 <= b["top5_agent_share_120_138"] <= 1
    assert set(result.by_signal) == set(evaluate.SIGNALS)
    assert result.shadow is not None and "brier" in result.shadow
    checks = evaluate.acceptance_checks(result)
    assert {c["check"] for c in checks} >= {"brier_p_win <= 0.245"}


def test_evaluation_is_deterministic() -> None:
    a = evaluate.evaluate_cut(_eval_frame(), "c", n_boot=30)
    b = evaluate.evaluate_cut(_eval_frame(), "c", n_boot=30)
    assert a.backtest == b.backtest and a.baselines == b.baselines


def test_promotion_rule_requires_both_cuts() -> None:
    base = {"c1": {"auc_pr": 0.60, "brier": 0.24}, "c2": {"auc_pr": 0.65, "brier": 0.235}}
    worse = {"c1": {"auc_pr": 0.59, "brier": 0.28}, "c2": {"auc_pr": 0.63, "brier": 0.27}}
    assert promotion.decide(base, worse).promoted is False
    assert promotion.decide(base, worse).blend_model_weight == 0.0
    one_cut_only = {"c1": {"auc_pr": 0.70, "brier": 0.20}, "c2": {"auc_pr": 0.66, "brier": 0.23}}
    assert promotion.decide(base, one_cut_only).promoted is False  # c2 margin < 0.02
    better = {"c1": {"auc_pr": 0.70, "brier": 0.20}, "c2": {"auc_pr": 0.70, "brier": 0.20}}
    decision = promotion.decide(base, better)
    assert decision.promoted is True and decision.blend_model_weight > 0
    assert promotion.decide(base, None).promoted is False
    assert all("passed" in c for c in decision.as_dict()["criteria"])
