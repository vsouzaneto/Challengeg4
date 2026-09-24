"""Job ``train``: temporal backtest of the rules + shadow LR, model registry entry, model card.

For ``--as-of T``:

1. for every backtest cut ``c < T`` (default 2017-06-30, 2017-09-30): build the temporal
   training frame (month ends < c), fit the shadow model, score the deals open at ``c`` with the
   rules **and** the shadow model, and evaluate both against ``labels/as_of=c`` (walk-forward,
   bootstrap CIs, mandatory baselines);
2. decide promotion (blend weight) from those cuts;
3. fit the final shadow model on the frame ending at ``T - 1 month`` and save it under
   ``models/<version>/pipeline_model/`` together with ``metrics.json``, ``model_card.md``,
   ``feature_list.json`` and ``training_manifest.json``; update ``models/latest``.

Gold tables for the cuts and frame months are rebuilt in memory from silver (single leakage
gate: ``gold.compute_history``), so the job depends only on ``build-features`` having run.
Fails (exit != 0, pointer untouched) when a section-7 acceptance threshold is not met.

Run: ``uv run python -m lead_scorer.jobs train --as-of 2017-12-31``
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from lead_scorer.config import BACKTEST_CUTS, GOLD_DIR, MODELS_DIR, SILVER_DIR, SNAPSHOT_DATE
from lead_scorer.data.gold import FEATURES_TABLE, GoldBuild, git_sha
from lead_scorer.jobs import artifacts
from lead_scorer.jobs.score import batch_summary
from lead_scorer.ml import drift, evaluate, promotion
from lead_scorer.ml.features import FEATURES, FORBIDDEN, ID_COL, add_ml_features
from lead_scorer.ml.frame import FRAME_START, GoldCache, TrainingFrame, build_training_frame
from lead_scorer.ml.model_card import render_model_card
from lead_scorer.ml.pipeline import (
    LR_PARAMS,
    PROB_COL,
    RAW_PROB_COL,
    SEED,
    ShadowModel,
    fit_shadow_model,
)
from lead_scorer.scoring.score import score_frame
from lead_scorer.scoring.weights import DEFAULT_WEIGHTS, Weights
from lead_scorer.spark import get_spark


@dataclass(frozen=True)
class TrainSummary:
    as_of: date
    model_version: str
    model_dir: Path
    promoted: bool
    metrics: dict[str, Any] = field(default_factory=dict)
    manifest: dict[str, Any] = field(default_factory=dict)

    def lines(self) -> list[str]:
        out = [
            f"[train] as_of={self.as_of.isoformat()} version={self.model_version} "
            f"promoted={self.promoted} blend={self.metrics['promotion']['blend_model_weight']}"
        ]
        for cut, b in self.metrics["backtest"].items():
            rnd = self.metrics["baselines"]["random"][cut]
            price = self.metrics["baselines"]["price"][cut]
            shadow = (self.metrics.get("shadow_model") or {}).get(cut) or {}
            out.append(
                f"  {cut}: n_open={b['n_open']} labeled={b['n_labeled']} brier={b['brier']:.3f} "
                f"auc_pr={b['auc_pr']:.3f} {b['auc_pr_ci']} (random {rnd['auc_pr']:.3f}) "
                f"p@10={b['precision_at_10']:.3f} (random {rnd['precision_at_10']:.3f}) "
                f"revenue_top20={b['revenue_capture_top20']:.3f} (random "
                f"{rnd['revenue_capture_top20']:.3f}, price {price['revenue_capture_top20']:.3f}) "
                f"zombies_closed_after={b['zombies_closed_after']}"
                + (
                    f" | shadow auc_pr={shadow['auc_pr']:.3f} brier={shadow['brier']:.3f}"
                    if shadow
                    else ""
                )
            )
        s = self.metrics["summary"]
        out.append(
            f"  snapshot: coverage={s['coverage']} zombies={s['zombie_count']} "
            f"tiers={s['tier_counts']} confidence={s['confidence_counts']} "
            f"spearman={s['spearman_score_price']:.3f}"
        )
        out.append(
            f"  acceptance={'passed' if self.metrics['acceptance']['passed'] else 'FAILED'} "
            f"wrote {self.model_dir} ({self.manifest['duration_seconds']}s, "
            f"git_sha={self.manifest['git_sha']})"
        )
        return out


# --- evaluation frame for one cut -----------------------------------------------------------------


def _rules_frame(build: GoldBuild, as_of: date, weights: Weights) -> pd.DataFrame:
    """Rules output for the deals open at ``as_of`` + the inputs the evaluator needs."""
    scored = score_frame(
        build.features, build.history, as_of=as_of, model_version="evaluation", weights=weights
    )
    extra = build.features.select(
        ID_COL,
        F.coalesce(F.col("win_rate_product"), F.col("global_win_rate")).alias("product_rate"),
    )
    pdf = scored.join(extra, ID_COL).toPandas()
    return pdf


def _labels_frame(build: GoldBuild) -> pd.DataFrame:
    """Outcome after the cut for evaluation only: label 1/0 and realised value of Won deals."""
    labels = build.labels.select(
        ID_COL,
        F.col("label_won").cast("double").alias("label"),
        F.when(F.col("label_won"), F.col("close_value"))  # leakage-ok: evaluation target
        .otherwise(F.lit(0.0))
        .alias("realized_value"),
        F.col("days_to_close_from_as_of").alias("days_to_close"),  # leakage-ok: evaluation
    )
    return labels.toPandas()


def _evaluation_frame(
    build: GoldBuild, as_of: date, weights: Weights, shadow: ShadowModel | None
) -> pd.DataFrame:
    frame = _rules_frame(build, as_of, weights).merge(_labels_frame(build), on=ID_COL, how="left")
    if shadow is not None:
        preds = shadow.predict(add_ml_features(build.features)).select(
            ID_COL, PROB_COL, RAW_PROB_COL
        )
        frame = frame.merge(preds.toPandas(), on=ID_COL, how="left")
    return frame


def _shadow_details(
    shadow: ShadowModel, frame: TrainingFrame, evaluation: pd.DataFrame
) -> dict[str, Any]:
    raw = evaluation.dropna(subset=["label", RAW_PROB_COL])
    return {
        "n_train": frame.counts.get("train_rows"),
        "n_calibration": frame.counts.get("calibration_rows"),
        "train_positive_rate": round(
            float(frame.counts.get("train_positive_rate", float("nan"))), 4
        ),
        "frame_months": [m.isoformat() for m in frame.months],
        "calibrated": shadow.calibrator is not None,
        "brier_raw": round(evaluate.brier(raw["label"].to_numpy(), raw[RAW_PROB_COL].to_numpy()), 4)
        if len(raw)
        else None,
        "coefficients": {k: round(v, 6) for k, v in shadow.coefficients().items()},
    }


# --- job ------------------------------------------------------------------------------------------


def run(
    as_of: date = SNAPSHOT_DATE,
    *,
    spark: SparkSession | None = None,
    silver_dir: Path = SILVER_DIR,
    gold_dir: Path = GOLD_DIR,
    models_dir: Path = MODELS_DIR,
    cuts: tuple[date, ...] = BACKTEST_CUTS,
    weights: Weights = DEFAULT_WEIGHTS,
    snapshot: date = SNAPSHOT_DATE,
    strict: bool = True,
    frame_start: date = FRAME_START,
) -> TrainSummary:
    started = time.perf_counter()  # duration only
    session = spark or get_spark("lead-scorer-train")
    silver_path = silver_dir / "opportunities"
    if not silver_path.is_dir():
        raise artifacts.MissingArtifactError(
            f"{silver_path} not found; " + artifacts.BUILD_FEATURES_HINT.format(as_of=as_of)
        )
    opportunities: DataFrame = session.read.parquet(str(silver_path)).cache()
    cache = GoldCache(opportunities, snapshot)

    # 1. walk-forward evaluation on every cut before as_of
    evaluations: list[evaluate.CutEvaluation] = []
    shadow_details: dict[str, dict[str, Any]] = {}
    for cut in sorted(c for c in cuts if c < as_of):
        frame = build_training_frame(cache, cut, frame_start)
        shadow = fit_shadow_model(frame.train, frame.calibration)
        build = cache.get(cut)
        ev_frame = _evaluation_frame(build, cut, weights, shadow)
        result = evaluate.evaluate_cut(ev_frame, cut.isoformat(), zombie_days=weights.zombie_days)
        evaluate.acceptance_checks(result)
        evaluations.append(result)
        shadow_details[cut.isoformat()] = _shadow_details(shadow, frame, ev_frame)

    # 2. promotion decision
    decision = promotion.decide(
        {e.cut: e.backtest for e in evaluations},
        {e.cut: e.shadow for e in evaluations if e.shadow is not None} or None,
    )
    version = artifacts.model_version_name(as_of, decision.promoted)
    target = artifacts.model_dir(version, models_dir)

    # 3. final shadow model on the frame ending at as_of - 1 month
    final_frame = build_training_frame(cache, as_of, frame_start)
    final_model = fit_shadow_model(final_frame.train, final_frame.calibration)
    final_model.save(target / artifacts.PIPELINE_MODEL_DIR)
    train_pdf = final_frame.train.select(*FEATURES).toPandas()

    # 4. snapshot summary with the rules (what the seller will see)
    snap_build = cache.get(as_of)
    snap = _rules_frame(snap_build, as_of, weights)
    summary = batch_summary(snap, weights)
    acceptance_by_cut = {e.cut: e.accepted for e in evaluations}
    accepted = all(c["passed"] for checks in acceptance_by_cut.values() for c in checks)

    metrics: dict[str, Any] = {
        "model_version": version,
        "as_of": as_of.isoformat(),
        "cuts": [e.cut for e in evaluations],
        "summary": {
            "blend_model_weight": decision.blend_model_weight,
            "coverage": summary["counts"]["rows"],
            "prospecting_count": summary["counts"]["prospecting"],
            "zombie_count": summary["counts"]["zombies"],
            "account_known_rate": summary["counts"]["account_known_rate"],
            "mean_calibration_error": round(
                float(
                    pd.Series([e.backtest["mean_calibration_error"] for e in evaluations]).mean()
                ),
                4,
            )
            if evaluations
            else None,
            "spearman_score_price": summary["spearman_score_price"],
            "tier_counts": summary["counts"]["tiers"],
            "confidence_counts": summary["counts"]["confidence"],
            "expected_value_total": summary["values"]["expected_value_total"],
            "zombie_nominal_value": summary["values"]["zombie_nominal_value"],
            "zombie_nominal_value_ratio_adjusted": summary["values"][
                "zombie_nominal_value_ratio_adjusted"
            ],
            "alive_nominal_value": summary["values"]["alive_nominal_value"],
            "top5_agent_share_120_138": evaluate.top5_late_share(snap, weights.zombie_days),
        },
        "backtest": {e.cut: e.backtest for e in evaluations},
        "baselines": {
            name: {e.cut: e.baselines[name] for e in evaluations} for name in evaluate.BASELINES
        },
        "by_signal": {
            name: {e.cut: e.by_signal[name] for e in evaluations} for name in evaluate.SIGNALS
        },
        "shadow_model": {e.cut: {**(e.shadow or {}), **shadow_details[e.cut]} for e in evaluations},
        "pessimistic": {e.cut: e.pessimistic for e in evaluations},
        "promotion": decision.as_dict(),
        "acceptance": {"passed": accepted, "by_cut": acceptance_by_cut},
        "weights": weights.as_dict(),
    }

    gold_manifest = artifacts.read_gold_manifest(FEATURES_TABLE, as_of, gold_dir)
    manifest: dict[str, Any] = {
        "job": "train",
        "model_version": version,
        "as_of": as_of.isoformat(),
        "snapshot_date": snapshot.isoformat(),
        "git_sha": git_sha(),
        "spark_version": session.version,
        "seed": SEED,
        "lr_params": LR_PARAMS,
        "blend_model_weight": decision.blend_model_weight,
        "promoted": decision.promoted,
        "weights": weights.as_dict(),
        "features": list(FEATURES),
        "forbidden_features": sorted(FORBIDDEN),
        "frame": {
            "start": frame_start.isoformat(),
            "months": [m.isoformat() for m in final_frame.months],
            "calibration_month": final_frame.calibration_month.isoformat(),
            "counts": final_frame.counts,
        },
        "coefficients": {k: round(v, 6) for k, v in final_model.coefficients().items()},
        "calibrated": final_model.calibrator is not None,
        "feature_distributions": drift.feature_distribution(train_pdf),
        "raw_checksums": gold_manifest.get("raw_checksums", {}),
        "cuts": [c.isoformat() for c in cuts if c < as_of],
        "duration_seconds": round(time.perf_counter() - started, 2),
        "generated_at": datetime.now(UTC).isoformat(
            timespec="seconds"
        ),  # leakage-ok: audit timestamp
    }

    artifacts.write_json(target / artifacts.METRICS_FILE, metrics)
    artifacts.write_json(target / artifacts.TRAINING_MANIFEST_FILE, manifest)
    artifacts.write_json(target / artifacts.FEATURE_LIST_FILE, list(FEATURES))
    (target / artifacts.MODEL_CARD_FILE).write_text(
        render_model_card(metrics, manifest), encoding="utf-8"
    )

    if strict and evaluations:
        evaluate.assert_accepted(evaluations)  # raises before the pointer moves
    artifacts.write_latest_pointer(version, models_dir)
    opportunities.unpersist()
    return TrainSummary(
        as_of=as_of,
        model_version=version,
        model_dir=target,
        promoted=decision.promoted,
        metrics=metrics,
        manifest=manifest,
    )


if __name__ == "__main__":  # pragma: no cover - thin wrapper around the typer CLI
    from lead_scorer.jobs.cli import app

    app(["train"] + __import__("sys").argv[1:])
