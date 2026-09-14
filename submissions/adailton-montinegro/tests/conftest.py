from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pytest


SUBMISSION_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SUBMISSION_ROOT / "solution" / "src"))

from ravenstack.bootstrap import inspect_file  # noqa: E402
from ravenstack.pipeline import BuildConfig, build  # noqa: E402


def _write_csv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


@pytest.fixture()
def built_fixture(tmp_path: Path):
    source = tmp_path / "source"
    source.mkdir()
    _write_csv(
        source / "ravenstack_accounts.csv",
        ["account_id", "account_name", "industry", "country", "signup_date", "referral_source", "plan_tier", "seats", "is_trial", "churn_flag"],
        [
            ["A1", "Alpha", "EdTech", "US", "2024-01-01", "partner", "Basic", 10, "False", "False"],
            ["A2", "Beta", "FinTech", "BR", "2024-02-01", "event", "Pro", 20, "False", "True"],
            ["A3", "Gamma", "EdTech", "BR", "2024-01-15", "organic", "Enterprise", 30, "False", "False"],
        ],
    )
    _write_csv(
        source / "ravenstack_subscriptions.csv",
        ["subscription_id", "account_id", "start_date", "end_date", "plan_tier", "seats", "mrr_amount", "arr_amount", "is_trial", "upgrade_flag", "downgrade_flag", "churn_flag", "billing_frequency", "auto_renew_flag"],
        [
            ["S1", "A1", "2024-01-01", "", "Basic", 10, 100, 1200, "False", "False", "False", "False", "monthly", "True"],
            ["S2", "A1", "2024-03-01", "", "Pro", 10, 50, 600, "False", "True", "False", "False", "monthly", "True"],
            ["S3", "A2", "2024-02-01", "2024-06-01", "Pro", 20, 200, 2400, "False", "False", "False", "True", "annual", "False"],
            ["S4", "A3", "2024-01-15", "", "Enterprise", 30, 300, 3600, "False", "False", "False", "False", "annual", "True"],
        ],
    )
    _write_csv(
        source / "ravenstack_feature_usage.csv",
        ["usage_id", "subscription_id", "usage_date", "feature_name", "usage_count", "usage_duration_secs", "error_count", "is_beta_feature"],
        [
            ["U1", "S1", "2024-04-01", "feature_1", 5, 100, 0, "False"],
            ["U1", "S1", "2024-04-02", "feature_1", 6, 120, 1, "False"],
            ["U2", "S1", "2023-12-01", "feature_2", 2, 20, 0, "False"],
            ["U3", "S2", "2024-05-01", "feature_2", 8, 150, 1, "True"],
            ["U4", "S3", "2024-03-01", "feature_1", 4, 80, 0, "False"],
            ["U5", "S4", "2024-05-20", "feature_3", 10, 200, 1, "False"],
        ],
    )
    _write_csv(
        source / "ravenstack_support_tickets.csv",
        ["ticket_id", "account_id", "submitted_at", "closed_at", "resolution_time_hours", "priority", "first_response_time_minutes", "satisfaction_score", "escalation_flag"],
        [
            ["T1", "A1", "2023-12-20", "2023-12-21", 24, "high", 60, 3, "False"],
            ["T2", "A2", "2024-05-25", "2024-05-26", 24, "urgent", 120, 2, "True"],
            ["T3", "A1", "2024-05-20", "2024-05-20 06:00:00", 6, "low", 10, 5, "False"],
            ["T4", "A3", "2024-05-22", "2024-05-23", 24, "medium", 30, "", "False"],
        ],
    )
    _write_csv(
        source / "ravenstack_churn_events.csv",
        ["churn_event_id", "account_id", "churn_date", "reason_code", "refund_amount_usd", "preceding_upgrade_flag", "preceding_downgrade_flag", "is_reactivation", "feedback_text"],
        [
            ["C1", "A2", "2024-06-01", "pricing", 10, "False", "False", "False", "too expensive"],
            ["C2", "A1", "2023-12-01", "features", 0, "False", "False", "False", "missing features"],
            ["C3", "A3", "2024-06-01", "support", 0, "False", "False", "False", ""],
        ],
    )

    files = []
    for path in sorted(source.glob("*.csv")):
        item = inspect_file(path)
        files.append({"name": item.name, "bytes": item.bytes, "rows": item.rows, "sha256": item.sha256})
    manifest = {
        "manifest_version": "test-v1",
        "source": {
            "platform": "fixture",
            "dataset_slug": "test/ravenstack",
            "dataset_version": 1,
            "download_handle": "test/ravenstack/versions/1",
            "license": "MIT",
        },
        "files": files,
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    config = BuildConfig(
        submission_root=SUBMISSION_ROOT,
        manifest_path=manifest_path,
        raw_dir=tmp_path / "raw",
        database_path=tmp_path / "warehouse" / "test.duckdb",
        export_dir=tmp_path / "exports",
        source_dir=source,
    )
    result = build(config)
    return result, config

