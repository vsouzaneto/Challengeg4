from __future__ import annotations

import os
from pathlib import Path

import duckdb
import pytest

from ravenstack.pipeline import BuildConfig, build


@pytest.mark.skipif(not os.getenv("RAVENSTACK_SOURCE_DIR"), reason="set RAVENSTACK_SOURCE_DIR for full v1 audit")
def test_known_kaggle_v1_anomalies(tmp_path: Path):
    source = Path(os.environ["RAVENSTACK_SOURCE_DIR"])
    submission_root = Path(__file__).resolve().parents[1]
    config = BuildConfig(
        submission_root=submission_root,
        manifest_path=submission_root / "data" / "manifest.v1.json",
        raw_dir=tmp_path / "raw",
        database_path=tmp_path / "warehouse" / "v1.duckdb",
        export_dir=tmp_path / "exports",
        source_dir=source,
    )
    result = build(config)
    con = duckdb.connect(str(result.database_path), read_only=True)
    failures = dict(
        con.execute(
            """
            SELECT rule_id, failed_rows FROM gold.quality_summary
            WHERE rule_id IN ('usage_duplicate_id_conflict', 'usage_before_subscription',
                              'usage_before_signup', 'usage_after_subscription',
                              'support_before_signup', 'support_missing_csat',
                              'subscription_overlap_unresolved')
            """
        ).fetchall()
    )
    assert failures == {
        "usage_duplicate_id_conflict": 42,
        "usage_before_subscription": 19142,
        "usage_before_signup": 13198,
        "usage_after_subscription": 290,
        "support_before_signup": 1077,
        "support_missing_csat": 825,
        "subscription_overlap_unresolved": 4992,
    }
    assert con.execute("SELECT COUNT(*) FROM gold.account_snapshot WHERE has_subscription_overlap").fetchone()[0] == 500
    tests = {
        row[0]: (row[1], row[2])
        for row in con.execute(
            "SELECT test_id, p_value, effect_value FROM gold.statistical_tests"
        ).fetchall()
    }
    assert tests["snapshot_flag_vs_event"][0] == pytest.approx(0.556736, abs=1e-5)
    assert tests["snapshot_flag_vs_event"][1] == pytest.approx(-0.025806, abs=1e-5)
    assert tests["snapshot_churn_by_plan_tier"][0] == pytest.approx(0.999281, abs=1e-5)
    assert tests["snapshot_churn_by_industry"][0] == pytest.approx(0.065675, abs=1e-5)
    assert tests["snapshot_churn_by_referral_source"][0] == pytest.approx(0.079356, abs=1e-5)
    assert tests["churn_reason_vs_feedback"][0] == pytest.approx(0.986358, abs=1e-5)
    assert tests["pre_event_escalation_0_14"][0] == pytest.approx(0.0703, abs=5e-4)
    con.close()

