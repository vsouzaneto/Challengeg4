from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports"


def test_model_and_limits_mentions_auc():
    t = (REPORTS / "model_and_limits.md").read_text(encoding="utf-8")
    assert "AUC" in t
    assert "causalidade" in t.lower() or "causality" in t.lower()


def test_executive_summary_exists():
    assert (REPORTS / "executive_summary.md").exists()
    assert len((REPORTS / "executive_summary.md").read_text(encoding="utf-8")) > 500


def test_playbook_revolving():
    t = (REPORTS / "playbook_cs_revolving.md").read_text(encoding="utf-8")
    assert "revolving" in t.lower() or "girat" in t.lower()


def test_recommendations_four_rows():
    import pandas as pd

    df = pd.read_csv(ROOT / "outputs" / "recommendations_impact.csv")
    assert len(df) >= 4
