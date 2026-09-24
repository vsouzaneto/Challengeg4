"""Job ``score``: gold features/history at ``--as-of`` + ``models/<version>`` -> ``gold/scores``.

Reads only the ``as_of=T`` partitions (point-in-time by construction), applies the rules layer
(``scoring.score_frame``), runs the layer-2 model in shadow mode (its probability is logged in
the manifest and blended only with the weight the ``train`` job decided), validates every row
against ``ScoredDeal`` and writes ``data/gold/scores/as_of=T/`` (parquet + ``_manifest.json``).
Idempotent: a rerun overwrites the partition with identical rows.

Run: ``uv run python -m lead_scorer.jobs score --as-of 2017-12-31 --model models/latest``
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from lead_scorer.config import GOLD_DIR, MODELS_DIR
from lead_scorer.contracts import ScoredDeal
from lead_scorer.data.gold import (
    DIM_HAZARD14,
    FEATURES_TABLE,
    HISTORY_TABLE,
    MANIFEST_NAME,
    git_sha,
)
from lead_scorer.jobs import artifacts
from lead_scorer.ml import drift
from lead_scorer.ml.evaluate import spearman
from lead_scorer.ml.features import FEATURES, ID_COL, add_ml_features
from lead_scorer.ml.pipeline import PROB_COL, ShadowModel
from lead_scorer.scoring.score import SCORED_DEAL_COLUMNS, score_frame
from lead_scorer.scoring.weights import DEFAULT_WEIGHTS, Weights
from lead_scorer.spark import get_spark


class ContractViolationError(ValueError):
    """A scored row does not satisfy ``ScoredDeal``."""


@dataclass(frozen=True)
class ScoreSummary:
    as_of: date
    model_version: str
    output_dir: Path
    manifest: dict[str, Any] = field(default_factory=dict)

    def lines(self) -> list[str]:
        c = self.manifest["counts"]
        v = self.manifest["values"]
        out = [
            f"[score] as_of={self.as_of.isoformat()} model={self.model_version} "
            f"blend_model_weight={self.manifest['blend_model_weight']}",
            f"  rows={c['rows']} engaging={c['engaging']} prospecting={c['prospecting']} "
            f"zombies={c['zombies']} account_known={c['account_known']} "
            f"({c['account_known_rate']:.1%})",
            "  tiers: " + ", ".join(f"{k}={v_}" for k, v_ in sorted(c["tiers"].items())),
            "  confidence: " + ", ".join(f"{k}={v_}" for k, v_ in c["confidence"].items()),
            f"  expected_value_total=R$ {v['expected_value_total']:,.0f} "
            f"zombie_nominal_value=R$ {v['zombie_nominal_value']:,.0f} "
            f"alive_nominal_value=R$ {v['alive_nominal_value']:,.0f}",
            f"  spearman(score, price)={self.manifest['spearman_score_price']:.3f} "
            f"psi_alerts={self.manifest['psi_alerts'] or 'none'}",
            f"  wrote {self.output_dir} ({self.manifest['duration_seconds']}s, "
            f"git_sha={self.manifest['git_sha']}, manifest={MANIFEST_NAME})",
        ]
        return out


# --- summaries shared with ``train`` --------------------------------------------------------------


def batch_summary(scored: pd.DataFrame, weights: Weights = DEFAULT_WEIGHTS) -> dict[str, Any]:
    """Counts and money of a scored batch (pandas). ``scored`` must carry ``sales_price``."""
    zombie = scored["days_in_engaging"].notna() & (scored["days_in_engaging"] > weights.zombie_days)
    prospecting = scored["days_in_engaging"].isna()
    p_win = scored["p_win"].replace(0, np.nan)
    ev_gross = (scored["expected_value"] / p_win).fillna(0.0)
    counts = {
        "rows": int(len(scored)),
        "engaging": int((~prospecting).sum()),
        "prospecting": int(prospecting.sum()),
        "zombies": int(zombie.sum()),
        "alive": int((~prospecting & ~zombie).sum()),
        "account_known": int(scored["account"].notna().sum()),
        "account_known_rate": round(float(scored["account"].notna().mean()), 4),
        "tiers": {str(k): int(v) for k, v in scored["tier"].value_counts().sort_index().items()},
        "confidence": {
            k: int(scored["confidence"].eq(k).sum()) for k in ("alta", "media", "baixa")
        },
    }
    price = scored["sales_price"].fillna(0.0)
    values = {
        "expected_value_total": round(float(scored["expected_value"].sum()), 2),
        "expected_value_alive": round(
            float(scored.loc[~prospecting & ~zombie, "expected_value"].sum()), 2
        ),
        "expected_value_zombies": round(float(scored.loc[zombie, "expected_value"].sum()), 2),
        # nominal = sum of list prices (same definition as the API's pipeline summary)
        "zombie_nominal_value": round(float(price[zombie].sum()), 2),
        "alive_nominal_value": round(float(price[~prospecting & ~zombie].sum()), 2),
        "prospecting_nominal_value": round(float(price[prospecting].sum()), 2),
        # list price x historical close_value/price ratio of the product (previous definition)
        "zombie_nominal_value_ratio_adjusted": round(float(ev_gross[zombie].sum()), 2),
        "alive_nominal_value_ratio_adjusted": round(
            float(ev_gross[~prospecting & ~zombie].sum()), 2
        ),
    }
    rho = spearman(scored["priority_score"].to_numpy(), scored["sales_price"].to_numpy())
    return {"counts": counts, "values": values, "spearman_score_price": round(rho, 4)}


def validate_rows(pdf: pd.DataFrame) -> int:
    """Validate every row against ``ScoredDeal``; raise on the first invalid row."""
    extra = set(pdf.columns) - set(SCORED_DEAL_COLUMNS)
    missing = set(SCORED_DEAL_COLUMNS) - set(pdf.columns)
    if extra or missing:
        raise ContractViolationError(
            f"columns differ from ScoredDeal: extra={extra} missing={missing}"
        )
    records = pdf.astype(object).where(pdf.notna(), None).to_dict(orient="records")
    for i, rec in enumerate(records):
        try:
            ScoredDeal.model_validate(rec)
        except Exception as exc:  # pydantic.ValidationError, re-raised with the row
            raise ContractViolationError(f"row {i} ({rec.get('opportunity_id')}): {exc}") from exc
    return len(records)


def _require_hazard(history: DataFrame, as_of: date) -> None:
    if history.filter(F.col("dimension") == DIM_HAZARD14).limit(1).count() == 0:
        raise artifacts.MissingArtifactError(
            f"history_stats/as_of={as_of.isoformat()} has no '{DIM_HAZARD14}' rows (built by an "
            "older version); " + artifacts.BUILD_FEATURES_HINT.format(as_of=as_of.isoformat())
        )


def shadow_predictions(model_dir: Path, features: DataFrame) -> DataFrame | None:
    """``(opportunity_id, p_model)`` from the saved layer-2 model, or None when it is absent."""
    pipeline_dir = model_dir / artifacts.PIPELINE_MODEL_DIR
    if not (pipeline_dir / "lr").is_dir():
        return None
    shadow = ShadowModel.load(pipeline_dir)
    return shadow.predict(add_ml_features(features)).select(ID_COL, PROB_COL)


def run(
    as_of: date,
    *,
    model: str | Path = artifacts.LATEST_POINTER,
    spark: SparkSession | None = None,
    gold_dir: Path = GOLD_DIR,
    models_dir: Path = MODELS_DIR,
    weights: Weights | None = None,
) -> ScoreSummary:
    started = time.perf_counter()  # duration only
    session = spark or get_spark("lead-scorer-score")

    model_dir = artifacts.resolve_model_dir(model, models_dir)
    training = artifacts.read_json(model_dir / artifacts.TRAINING_MANIFEST_FILE)
    model_version = str(training["model_version"])
    blend = float(training.get("blend_model_weight", 0.0))
    w = weights or Weights(**{**DEFAULT_WEIGHTS.as_dict(), "blend_model_weight": blend})

    features = artifacts.read_gold(session, FEATURES_TABLE, as_of, gold_dir).cache()
    history = artifacts.read_gold(session, HISTORY_TABLE, as_of, gold_dir)
    _require_hazard(history, as_of)

    p_model = shadow_predictions(model_dir, features)
    scored = score_frame(
        features, history, as_of=as_of, model_version=model_version, weights=w, p_model=p_model
    )

    target = artifacts.gold_partition(artifacts.SCORES_TABLE, as_of, gold_dir)
    scored.coalesce(1).write.mode("overwrite").parquet(str(target))

    # Validate what the API will read, not what Spark had in memory.
    written = pd.read_parquet(target)
    n_valid = validate_rows(written)
    n_open = features.count()
    if n_valid != n_open:
        raise ContractViolationError(f"{n_valid} scored rows for {n_open} open deals at {as_of}")

    summary = batch_summary(written, w)

    ml_batch = add_ml_features(features).select(*FEATURES).toPandas()
    psi = drift.psi_report(training.get("feature_distributions", {}), ml_batch)
    alerts = drift.psi_alerts(psi)
    for name in alerts:
        print(f"[score] WARNING: PSI({name}) = {psi[name]:.3f} > {drift.PSI_ALERT} (drift)")

    shadow_stats: dict[str, Any] | None = None
    if p_model is not None:
        pm = p_model.toPandas().set_index(ID_COL)[PROB_COL]
        aligned = written[ID_COL].map(pm).to_numpy(dtype=float)
        shadow_stats = {
            "mean_p_model": round(float(np.nanmean(aligned)), 4),
            "mean_p_win": round(float(written["p_win"].mean()), 4),
            "spearman_p_model_p_win": round(spearman(aligned, written["p_win"].to_numpy()), 4),
            "mode": "blended" if blend > 0 else "shadow (logged only)",
        }

    gold_manifest = artifacts.read_gold_manifest(FEATURES_TABLE, as_of, gold_dir)
    manifest: dict[str, Any] = {
        "job": "score",
        "as_of": as_of.isoformat(),
        "model_version": model_version,
        "model_dir": str(model_dir),
        "blend_model_weight": blend,
        "git_sha": git_sha(),
        "spark_version": session.version,
        "params": w.as_dict(),
        "raw_checksums": gold_manifest.get("raw_checksums", {}),
        "gold_manifest_git_sha": gold_manifest.get("git_sha"),
        **summary,
        "psi": psi,
        "psi_alerts": alerts,
        "shadow_model": shadow_stats,
        "columns": list(SCORED_DEAL_COLUMNS),
        "duration_seconds": round(time.perf_counter() - started, 2),
        "generated_at": datetime.now(UTC).isoformat(
            timespec="seconds"
        ),  # leakage-ok: audit timestamp
    }
    artifacts.write_json(target / MANIFEST_NAME, manifest)
    features.unpersist()
    return ScoreSummary(
        as_of=as_of, model_version=model_version, output_dir=target, manifest=manifest
    )


if __name__ == "__main__":  # pragma: no cover - thin wrapper around the typer CLI
    from lead_scorer.jobs.cli import app

    app(["score"] + __import__("sys").argv[1:])
