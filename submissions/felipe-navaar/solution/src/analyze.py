"""EDA reproduzível do pipeline, sem transformar descrição em scoring."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from .ingest import load_and_prepare


REFERENCE_DATE = date(2017, 12, 31)
OPEN_STAGES = ("Engaging", "Prospecting")
CLOSED_STAGES = ("Won", "Lost")


def _group_count(frame: pd.DataFrame, column: str) -> dict[str, int]:
    return {str(key): int(value) for key, value in frame[column].value_counts(dropna=False).items()}


def _group_mean(frame: pd.DataFrame, group_column: str, value_column: str) -> dict[str, float | None]:
    grouped = frame.groupby(group_column, dropna=False)[value_column].mean()
    return {str(key): (None if pd.isna(value) else float(value)) for key, value in grouped.items()}


def _group_count_and_mean(frame: pd.DataFrame, group_column: str, value_column: str) -> dict[str, dict[str, float | int]]:
    grouped = frame.groupby(group_column, dropna=False)[value_column].agg(["count", "mean"])
    return {
        str(key): {"n": int(row["count"]), "mean": float(row["mean"])}
        for key, row in grouped.iterrows()
        if not pd.isna(row["mean"])
    }


def _age_summary(ages: pd.Series) -> dict[str, Any]:
    known = ages.dropna()
    return {
        "n_known": int(known.size),
        "n_missing": int(ages.isna().sum()),
        "negative_count": int((known < 0).sum()),
        "min_days": None if known.empty else int(known.min()),
        "median_days": None if known.empty else float(known.median()),
        "max_days": None if known.empty else int(known.max()),
    }


def analyze_pipeline(enriched: pd.DataFrame, reference_date: str | date = REFERENCE_DATE) -> dict[str, Any]:
    """Calcula estatísticas descritivas com denominadores explícitos.

    A idade aberta é idade desde ``engage_date`` até o corte; não representa
    inatividade ou tempo desde o último contato. Fechamentos não são usados
    como features operacionais nesta função.
    """

    cutoff = pd.Timestamp(reference_date)
    required = {"opportunity_id", "deal_stage", "product", "engage_date", "close_date", "close_value", "account"}
    missing = sorted(required - set(enriched.columns))
    if missing:
        raise ValueError(f"Tabela enriquecida sem colunas obrigatórias: {', '.join(missing)}")

    frame = enriched.copy()
    frame["engage_date"] = pd.to_datetime(frame["engage_date"], errors="coerce")
    frame["close_date"] = pd.to_datetime(frame["close_date"], errors="coerce")
    frame["close_value"] = pd.to_numeric(frame["close_value"], errors="coerce")
    open_frame = frame[frame["deal_stage"].isin(OPEN_STAGES)].copy()
    closed_frame = frame[frame["deal_stage"].isin(CLOSED_STAGES)].copy()
    won_frame = frame[frame["deal_stage"].eq("Won")].copy()
    open_ages = (cutoff - open_frame["engage_date"]).dt.days
    close_duration = (closed_frame["close_date"] - closed_frame["engage_date"]).dt.days

    duration_known = close_duration.dropna()
    report: dict[str, Any] = {
        "reference_date": cutoff.date().isoformat(),
        "reference_is_official_snapshot": False,
        "rows": int(len(frame)),
        "unique_ids": int(frame["opportunity_id"].nunique()),
        "stage_counts": _group_count(frame, "deal_stage"),
        "open": {"n": int(len(open_frame)), "stages": list(OPEN_STAGES)},
        "closed": {"n": int(len(closed_frame)), "stages": list(CLOSED_STAGES)},
        "missing": {
            "account_by_stage": {
                str(stage): int(frame.loc[frame["deal_stage"].eq(stage), "account"].isna().sum())
                for stage in frame["deal_stage"].dropna().unique()
            },
            "engage_date_by_stage": {
                str(stage): int(frame.loc[frame["deal_stage"].eq(stage), "engage_date"].isna().sum())
                for stage in frame["deal_stage"].dropna().unique()
            },
            "close_date_open": int(open_frame["close_date"].isna().sum()),
            "close_value_open": int(open_frame["close_value"].isna().sum()),
        },
        "won_only": {
            "n": int(len(won_frame)),
            "mean_close_value_by_product": _group_mean(won_frame, "product", "close_value"),
            "by_product": _group_count_and_mean(won_frame, "product", "close_value"),
        },
        "closed_all": {
            "n": int(len(closed_frame)),
            "mean_close_value_by_product": _group_mean(closed_frame, "product", "close_value"),
            "by_product": _group_count_and_mean(closed_frame, "product", "close_value"),
        },
        "win_rate_among_closed": None if len(closed_frame) == 0 else float(len(won_frame) / len(closed_frame)),
        "open_age_since_engage": _age_summary(open_ages),
        "closed_duration_descriptive": {
            "n_known": int(duration_known.size),
            "n_missing": int(close_duration.isna().sum()),
            "negative_count": int((duration_known < 0).sum()),
            "mean_days": None if duration_known.empty else float(duration_known.mean()),
            "median_days": None if duration_known.empty else float(duration_known.median()),
        },
        "interpretation": {
            "observations": [
                "Stage counts and missingness describe this dataset at the declared cutoff.",
                "Won-only close values are separated from averages across all closed rows.",
                "Open age is elapsed time since engage_date when known, not inactivity or last contact.",
            ],
            "commercial_hypotheses": [
                "Engaging may represent greater commercial maturity than Prospecting, but transition history is unavailable.",
                "Product reference price may be useful context, but is not expected revenue.",
            ],
            "unsupported_signals": [
                "Closed duration is not used as open-deal urgency.",
                "Missing account is not treated as poor account quality.",
                "No causal or predictive claim is made from seller, sector, region, or product differences.",
            ],
        },
    }
    return report


def run_analysis(data_dir: str | Path | None = None, output_dir: str | Path | None = None) -> dict[str, Any]:
    """Executa M1 + M2 e grava o relatório derivado em ``outputs``."""

    project_root = Path(__file__).resolve().parents[1]
    destination = Path(output_dir) if output_dir is not None else project_root / "outputs"
    result = load_and_prepare(data_dir)
    report = analyze_pipeline(result.enriched, REFERENCE_DATE)
    report["ingestion_diagnostics"] = result.diagnostics
    destination.mkdir(parents=True, exist_ok=True)
    with (destination / "m2_eda.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")
    return report

