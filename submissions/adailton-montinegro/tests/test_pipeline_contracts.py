from __future__ import annotations

import csv
import json
from pathlib import Path

import duckdb


EXPECTED_EXPORTS = {
    "quality_summary.csv",
    "quality_issues.csv",
    "analysis_scope.csv",
    "account_snapshot.csv",
    "monthly_events.csv",
    "segment_snapshot.csv",
    "churn_reasons.csv",
    "account_triage.csv",
    "metric_catalog.csv",
    "pre_event_signals.csv",
    "statistical_tests.csv",
    "report_context.json",
}


def _header(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8") as handle:
        return next(csv.reader(handle))


def test_raw_stage_reconciliation_and_quarantine(built_fixture):
    result, _ = built_fixture
    con = duckdb.connect(str(result.database_path), read_only=True)
    assert con.execute("SELECT COUNT(*) FROM raw.feature_usage").fetchone()[0] == 6
    assert con.execute("SELECT COUNT(*) FROM stage.feature_usage WHERE is_eligible").fetchone()[0] == 3
    assert con.execute("SELECT COUNT(*) FROM stage.feature_usage WHERE NOT is_eligible").fetchone()[0] == 3
    assert con.execute(
        "SELECT failed_rows FROM gold.quality_summary WHERE rule_id='usage_duplicate_id_conflict'"
    ).fetchone()[0] == 2
    assert con.execute(
        "SELECT failed_rows FROM gold.quality_summary WHERE rule_id='support_before_signup'"
    ).fetchone()[0] == 1
    assert con.execute(
        "SELECT COUNT(*) FROM gold.analysis_scope WHERE raw_rows <> eligible_rows + quarantined_rows"
    ).fetchone()[0] == 0
    con.close()


def test_churn_universes_and_mrr_proxy_remain_separate(built_fixture):
    result, _ = built_fixture
    con = duckdb.connect(str(result.database_path), read_only=True)
    account = con.execute(
        """
        SELECT snapshot_churn_flag, has_valid_churn_event, has_subscription_overlap,
               mrr_proxy_conservative, mrr_proxy_additive, revenue_confidence
        FROM gold.account_snapshot WHERE account_id='A1'
        """
    ).fetchone()
    assert account == (False, False, True, 100.0, 150.0, "Conditional")
    unavailable = dict(
        con.execute(
            "SELECT metric_id, value_status FROM gold.metric_catalog WHERE metric_id IN ('monthly_logo_churn','grr','nrr')"
        ).fetchall()
    )
    assert unavailable == {"monthly_logo_churn": "Unavailable", "grr": "Unavailable", "nrr": "Unavailable"}
    assert con.execute("SELECT SUM(new_accounts) FROM gold.monthly_events").fetchone()[0] == 3
    assert con.execute("SELECT SUM(valid_churn_events) FROM gold.monthly_events").fetchone()[0] == 2
    con.close()


def test_triage_is_non_probabilistic_and_active_only(built_fixture):
    result, _ = built_fixture
    con = duckdb.connect(str(result.database_path), read_only=True)
    columns = [row[1] for row in con.execute("PRAGMA table_info('gold.account_triage')").fetchall()]
    assert "probability" not in " ".join(columns).lower()
    assert "historical_churn_events" not in columns
    assert "refund_amount_usd" not in columns
    assert con.execute("SELECT COUNT(*) FROM gold.account_triage WHERE snapshot_churn_flag").fetchone()[0] == 0
    assert con.execute("SELECT COUNT(*) FROM gold.account_triage").fetchone()[0] == 2
    assert con.execute("SELECT COUNT(*) FROM gold.account_triage WHERE triage_score NOT BETWEEN 0 AND 100").fetchone()[0] == 0
    con.close()


def test_reviewable_exports_and_report_context_contract(built_fixture):
    result, _ = built_fixture
    assert {path.name for path in result.export_dir.iterdir()} == EXPECTED_EXPORTS
    assert _header(result.export_dir / "account_snapshot.csv") == [
        "account_id", "account_name", "industry", "country", "referral_source", "plan_tier",
        "seats", "is_trial", "snapshot_churn_flag", "signup_date", "has_valid_churn_event",
        "valid_churn_event_count", "has_subscription_overlap", "mrr_proxy_conservative",
        "mrr_proxy_additive", "revenue_confidence",
    ]
    assert _header(result.export_dir / "account_triage.csv")[6:13] == [
        "triage_score", "triage_band", "evidence_confidence", "evidence_coverage_pct",
        "signal_1", "signal_2", "signal_3",
    ]
    context = json.loads((result.export_dir / "report_context.json").read_text(encoding="utf-8"))
    assert context["kpis"]["total_accounts"] == 3
    assert context["kpis"]["source_table_count"] == 5
    assert context["kpis"]["valid_churn_events"] == 2
    assert context["kpis"]["raw_total_rows"] == 20
    assert context["kpis"]["data_period"] == "2023-12-01 to 2024-06-01"
