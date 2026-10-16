"""Testes mínimos — integridade pós-run."""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def test_integration_qa_passes():
    qa = pd.read_csv(OUT / "integration_qa.csv")
    assert qa["pass"].all(), qa.to_string()


def test_account_master_has_five_table_fields():
    acc = pd.read_csv(OUT / "account_master.csv")
    for col in ["mrr_amount", "churn_events", "total_usage", "tickets", "net_churned"]:
        assert col in acc.columns, col
    assert len(acc) >= 400


def test_action_queue_explainability():
    q = pd.read_csv(OUT / "cs_action_queue_top50.csv")
    assert "why_risk" in q.columns
    assert "risk_score" in q.columns
    assert len(q) <= 50


def test_summary_stats_json():
    stats = json.loads((OUT / "summary_stats.json").read_text(encoding="utf-8"))
    assert stats["revolving_active"] > 0
    assert stats["churn_events_total"] > stats["net_churned"]
