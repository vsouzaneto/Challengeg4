"""Test-only parquet builder derived from ``EXAMPLE_SCORED_DEAL``.

Nothing here is shipped: partitions are written into a pytest temp directory at session start.
Two encodings of ``reasons`` are produced to prove the API accepts both list-of-struct (what
Spark writes for ``array<struct>``) and JSON strings.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq
from lead_scorer_contracts import EXAMPLE_SCORED_DEAL, ScoredDeal

AGENTS: list[tuple[str, str, str]] = [
    ("Darcel Schlecht", "Melvin Marxen", "Central"),
    ("Anna Snelling", "Dustin Brinkmann", "Central"),
    ("Vicki Laflamme", "Cara Losch", "East"),
    ("Kami Bicknell", "Rocco Neubert", "West"),
]
PRODUCTS = ["GTX Pro", "MG Special", "GTX Basic", "GTK 500"]
TIERS = ["A", "B", "C", "D"]
TIER_SCORES = {"A": 85.0, "B": 65.0, "C": 45.0, "D": 20.0}


def build_rows(
    as_of: date, n: int = 24, model_version: str = "test-model-v1"
) -> list[dict[str, Any]]:
    """Deterministic variations: 4 agents x 6 deals, 1 zombie, Prospecting rows, no-account rows."""
    rows: list[dict[str, Any]] = []
    for i in range(n):
        agent, manager, region = AGENTS[i % len(AGENTS)]
        tier = TIERS[i % 4]
        prospecting = i % 6 == 5
        zombie = i == 3  # tier D, > 138 days
        days = None if prospecting else (150 if zombie else 10 + i * 5)
        account_known = i % 3 != 0
        reasons = [dict(r) for r in EXAMPLE_SCORED_DEAL["reasons"]]
        if not account_known:
            reasons.append(
                {
                    "code": "ACCOUNT_UNKNOWN",
                    "direction": "i",
                    "weight": 0.0,
                    "text_pt": "Sem conta cadastrada: estimativa menos confiável.",
                }
            )
        if zombie:
            reasons.append(
                {
                    "code": "ZOMBIE_RISK",
                    "direction": "-",
                    "weight": -0.18,
                    "text_pt": "150 dias em Engaging: acima do ciclo máximo observado (138).",
                }
            )
        if prospecting:
            reasons.append(
                {
                    "code": "PROSPECTING_NO_TIMELINE",
                    "direction": "i",
                    "weight": 0.0,
                    "text_pt": "Prospecting não tem data: urgência desconhecida.",
                }
            )
        rows.append(
            {
                **EXAMPLE_SCORED_DEAL,
                "opportunity_id": f"T{i:04d}",
                "sales_agent": agent,
                "manager": manager,
                "regional_office": region,
                "product": PRODUCTS[i % len(PRODUCTS)],
                "account": f"Account {i}" if account_known else None,
                "deal_stage": "Prospecting" if prospecting else "Engaging",
                "days_in_engaging": days,
                "priority_score": TIER_SCORES[tier] - (i % 4) * 0.5,
                "tier": tier,
                "p_win": round(0.3 + (i % 7) * 0.08, 2),
                "expected_value": round(500.0 + i * 137.5, 2),
                "sales_price": 1000.0 + i * 250.0,
                "urgency": round((i % 5) / 4, 2),
                "confidence": "alta" if account_known else "baixa",
                "reasons": reasons,
                "as_of": as_of.isoformat(),
                "model_version": model_version,
            }
        )
    for row in rows:  # every fixture row must satisfy the contract
        ScoredDeal.model_validate(row)
    return rows


def write_partition(
    scores_dir: Path,
    as_of: date,
    *,
    reasons_as_json: bool = False,
    drop_as_of_column: bool = False,
    drop_columns: tuple[str, ...] = (),
    rows: list[dict[str, Any]] | None = None,
    model_version: str = "test-model-v1",
) -> Path:
    """Write ``scores_dir/as_of=YYYY-MM-DD/part-0.parquet`` and return the partition dir."""
    rows = rows if rows is not None else build_rows(as_of, model_version=model_version)
    out = [dict(r) for r in rows]
    for r in out:
        r["as_of"] = date.fromisoformat(r["as_of"]) if isinstance(r["as_of"], str) else r["as_of"]
        if reasons_as_json:
            r["reasons"] = json.dumps(r["reasons"], ensure_ascii=False)
        if drop_as_of_column:
            del r["as_of"]
        for column in drop_columns:
            r.pop(column, None)
    table = pa.Table.from_pylist(out)
    part = scores_dir / f"as_of={as_of.isoformat()}"
    part.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, str(part / "part-0.parquet"))
    (part / "_SUCCESS").write_text("")  # Spark marker: must be ignored by the reader
    return part


def write_model_dir(models_dir: Path, version: str = "test-model-v1") -> Path:
    """``models/<version>/{metrics.json,feature_list.json,model_card.md}`` + pointer file."""
    model_dir = models_dir / version
    model_dir.mkdir(parents=True, exist_ok=True)
    (model_dir / "metrics.json").write_text(
        json.dumps(
            {
                "model_version": version,
                "backtest": {"2017-09-30": {"precision_at_10": 0.78, "brier": 0.21}},
                "baselines": {"random": {"precision_at_10": 0.63}},
            }
        ),
        encoding="utf-8",
    )
    (model_dir / "feature_list.json").write_text('["product_base_rate", "days_in_engaging"]')
    (model_dir / "model_card.md").write_text("# Model card\n\nFixture.\n", encoding="utf-8")
    (models_dir / "latest").write_text(version + "\n", encoding="utf-8")
    return model_dir
