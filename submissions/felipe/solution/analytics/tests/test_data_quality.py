import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs"
REPORTS = ROOT / "reports"


def test_data_quality_json_exists():
    assert (OUT / "data_quality_summary.json").exists()


def test_data_quality_csv_has_metrics():
    df = pd.read_csv(OUT / "data_quality_summary.csv")
    assert "metrica" in df.columns
    assert len(df) >= 8


def test_data_quality_ceo_report():
    text = (REPORTS / "data_quality_ceo.md").read_text(encoding="utf-8")
    assert "Qualidade de dados" in text
    assert "revolving" in text.lower() or "Reconciliar" in text


def test_flag_without_event_non_negative():
    s = json.loads((OUT / "data_quality_summary.json").read_text(encoding="utf-8"))
    assert s["contas_flag_sem_evento_churn"] >= 0
    assert s["churn_liquido_flag"] >= s["contas_flag_sem_evento_churn"]


def test_usage_before_sub_pct_bounded():
    s = json.loads((OUT / "data_quality_summary.json").read_text(encoding="utf-8"))
    assert 0 <= s["pct_uso_antes_assinatura"] <= 100
