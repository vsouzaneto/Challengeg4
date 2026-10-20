"""Motor de score heurístico, independente da interface Streamlit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY_PATH = PROJECT_ROOT / "config" / "scoring_policy.json"
OPEN_STAGES = {"Engaging", "Prospecting"}
OUTPUT_COLUMNS = [
    "opportunity_id",
    "priority_score",
    "score_factors",
    "warnings",
    "policy_version",
    "reference_date",
    "rank",
]


def load_policy(path: str | Path = DEFAULT_POLICY_PATH) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def _validate_policy(policy: dict[str, Any]) -> None:
    required = {"policy_version", "reference_date", "score_range", "base_points", "stage_points"}
    missing = sorted(required - set(policy))
    if missing:
        raise ValueError(f"Política sem campos obrigatórios: {', '.join(missing)}")
    if set(policy["stage_points"]) != OPEN_STAGES:
        raise ValueError("A política deve definir pontos exatamente para Engaging e Prospecting")
    lower, upper = policy["score_range"]
    if not 0 <= lower <= upper <= 100:
        raise ValueError("score_range deve estar dentro de 0–100")


def _empty_output() -> pd.DataFrame:
    return pd.DataFrame(columns=OUTPUT_COLUMNS)


def score_open_opportunities(
    enriched: pd.DataFrame,
    policy: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """Pontua somente oportunidades abertas e produz explicações serializáveis."""

    policy = load_policy() if policy is None else policy
    _validate_policy(policy)
    required = {"opportunity_id", "deal_stage", "account", "engage_date", "sales_price"}
    missing = sorted(required - set(enriched.columns))
    if missing:
        raise ValueError(f"Tabela sem colunas obrigatórias para scoring: {', '.join(missing)}")

    frame = enriched.loc[enriched["deal_stage"].isin(OPEN_STAGES)].copy()
    if frame.empty:
        return _empty_output()

    lower, upper = policy["score_range"]
    rows: list[dict[str, Any]] = []
    for _, deal in frame.iterrows():
        stage = str(deal["deal_stage"])
        base = int(policy["base_points"])
        stage_points = int(policy["stage_points"][stage])
        raw_score = base + stage_points
        score = max(lower, min(upper, raw_score))
        warnings: list[str] = []
        if pd.isna(deal["account"]):
            warnings.append("account ausente; score não reduzido")
        if pd.isna(deal["engage_date"]):
            warnings.append("engage_date ausente; idade desde engajamento indisponível")
        if pd.isna(deal["sales_price"]):
            warnings.append("preço de catálogo indisponível; desempate por preço não aplicado")
        factors = [
            {"name": "base", "contribution": base, "reason": "base fixa da política"},
            {"name": "deal_stage", "contribution": stage_points, "reason": f"heurística de maturidade para {stage}"},
        ]
        if sum(item["contribution"] for item in factors) != score:
            raise ValueError("Contribuições não reconciliam com o score final")
        rows.append(
            {
                "opportunity_id": deal["opportunity_id"],
                "priority_score": int(score),
                "score_factors": factors,
                "warnings": warnings,
                "policy_version": policy["policy_version"],
                "reference_date": policy["reference_date"],
                "_sales_price_sort": deal["sales_price"] if pd.notna(deal["sales_price"]) else float("-inf"),
            }
        )

    scored = pd.DataFrame(rows)
    scored["_opportunity_id_sort"] = scored["opportunity_id"].astype(str)
    scored = scored.sort_values(
        by=["priority_score", "_sales_price_sort", "_opportunity_id_sort"],
        ascending=[False, False, True],
        kind="mergesort",
    ).reset_index(drop=True)
    scored["rank"] = range(1, len(scored) + 1)
    return scored[OUTPUT_COLUMNS]

