"""Deterministic raw -> stage -> gold DuckDB build and reviewable exports."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb

from .bootstrap import VerifiedFile, ensure_raw_data
from .statistics import build_statistical_tests


RAW_TABLES = {
    "accounts": "ravenstack_accounts.csv",
    "subscriptions": "ravenstack_subscriptions.csv",
    "feature_usage": "ravenstack_feature_usage.csv",
    "support_tickets": "ravenstack_support_tickets.csv",
    "churn_events": "ravenstack_churn_events.csv",
}

EXPORTS = {
    "quality_summary.csv": ("gold.quality_summary", "table_name, rule_id"),
    "quality_issues.csv": ("gold.quality_issues", "table_name, source_row_number, rule_id"),
    "analysis_scope.csv": ("gold.analysis_scope", "scope_id"),
    "account_snapshot.csv": ("gold.account_snapshot", "account_id"),
    "monthly_events.csv": ("gold.monthly_events", "month_start"),
    "segment_snapshot.csv": ("gold.segment_snapshot", "dimension_name, segment_value"),
    "churn_reasons.csv": ("gold.churn_reasons", "valid_churn_events DESC, reason_code"),
    "account_triage.csv": ("gold.account_triage", "triage_score DESC, mrr_proxy_additive DESC NULLS LAST, account_id"),
    "metric_catalog.csv": ("gold.metric_catalog", "metric_id"),
    "pre_event_signals.csv": ("gold.pre_event_signals", "window_order"),
    "statistical_tests.csv": ("gold.statistical_tests", "test_id"),
}


@dataclass(frozen=True)
class BuildConfig:
    submission_root: Path
    manifest_path: Path
    raw_dir: Path
    database_path: Path
    export_dir: Path
    source_dir: Path | None = None
    force_download: bool = False
    export_csv: bool = True

    @classmethod
    def defaults(
        cls,
        *,
        source_dir: Path | None = None,
        force_download: bool = False,
        export_csv: bool = True,
    ) -> "BuildConfig":
        root = Path(__file__).resolve().parents[3]
        return cls(
            submission_root=root,
            manifest_path=root / "data" / "manifest.v1.json",
            raw_dir=root / "data" / "raw",
            database_path=root / "data" / "warehouse" / "ravenstack.duckdb",
            export_dir=root / "artifacts" / "data",
            source_dir=source_dir,
            force_download=force_download,
            export_csv=export_csv,
        )


@dataclass(frozen=True)
class BuildResult:
    database_path: Path
    export_dir: Path
    manifest_version: str
    data_cutoff: str
    raw_rows: int
    eligible_rows: int
    quarantined_rows: int


def _read_sql(config: BuildConfig, name: str) -> str:
    path = config.submission_root / "solution" / "sql" / name
    return path.read_text(encoding="utf-8")


def _load_raw_tables(con: Any, raw_dir: Path) -> None:
    for table, filename in RAW_TABLES.items():
        path = raw_dir / filename
        con.execute(
            f"""
            CREATE TABLE raw.{table} AS
            SELECT ROW_NUMBER() OVER ()::BIGINT AS source_row_number, *
            FROM read_csv_auto(
                ?, header = TRUE, all_varchar = TRUE, sample_size = -1,
                nullstr = '__RAVENSTACK_NULL_SENTINEL__'
            )
            """,
            [str(path)],
        )


def _insert_metadata(
    con: Any,
    manifest: dict[str, Any],
    verified: list[VerifiedFile],
    generated_at: datetime,
) -> None:
    source = manifest["source"]
    con.execute(
        "INSERT INTO meta.build_info VALUES (?, ?, ?, ?)",
        [manifest["manifest_version"], source["dataset_slug"], source["dataset_version"], generated_at],
    )
    specs = {item["name"]: item for item in manifest["files"]}
    rows = []
    for item in verified:
        expected = specs[item.name]
        rows.append(
            (
                item.name,
                expected["bytes"],
                item.bytes,
                expected["rows"],
                item.rows,
                expected["sha256"],
                item.sha256,
                True,
            )
        )
    con.executemany("INSERT INTO meta.raw_manifest VALUES (?, ?, ?, ?, ?, ?, ?, ?)", rows)


def validate_contracts(con: Any) -> None:
    failures: list[str] = []
    for table in RAW_TABLES:
        raw_count = con.execute(f"SELECT COUNT(*) FROM raw.{table}").fetchone()[0]
        stage_count = con.execute(f"SELECT COUNT(*) FROM stage.{table}").fetchone()[0]
        eligible, quarantined = con.execute(
            f"""
            SELECT COUNT(*) FILTER (WHERE is_eligible),
                   COUNT(*) FILTER (WHERE NOT is_eligible)
            FROM stage.{table}
            """
        ).fetchone()
        if raw_count != stage_count:
            failures.append(f"{table}: raw={raw_count}, stage={stage_count}")
        if raw_count != eligible + quarantined:
            failures.append(
                f"{table}: raw={raw_count}, eligible={eligible}, quarantine={quarantined}"
            )

    duplicate_accounts = con.execute(
        "SELECT COUNT(*) FROM (SELECT account_id FROM gold.account_snapshot GROUP BY 1 HAVING COUNT(*) > 1)"
    ).fetchone()[0]
    if duplicate_accounts:
        failures.append(f"account_snapshot contém {duplicate_accounts} chaves duplicadas")

    invalid_proxy = con.execute(
        """
        SELECT COUNT(*) FROM gold.account_snapshot
        WHERE mrr_proxy_conservative > mrr_proxy_additive
           OR mrr_proxy_conservative < 0 OR mrr_proxy_additive < 0
        """
    ).fetchone()[0]
    if invalid_proxy:
        failures.append(f"account_snapshot contém {invalid_proxy} intervalos de MRR inválidos")

    monthly_signups = con.execute("SELECT SUM(new_accounts) FROM gold.monthly_events").fetchone()[0]
    eligible_accounts = con.execute("SELECT COUNT(*) FROM stage.accounts WHERE is_eligible").fetchone()[0]
    if monthly_signups != eligible_accounts:
        failures.append(f"signups mensais={monthly_signups}, contas elegíveis={eligible_accounts}")

    monthly_churn = con.execute("SELECT SUM(valid_churn_events) FROM gold.monthly_events").fetchone()[0]
    valid_churn = con.execute("SELECT COUNT(*) FROM stage.churn_events WHERE is_eligible").fetchone()[0]
    if monthly_churn != valid_churn:
        failures.append(f"churn mensal={monthly_churn}, eventos elegíveis={valid_churn}")

    invalid_triage = con.execute(
        """
        SELECT COUNT(*) FROM gold.account_triage
        WHERE snapshot_churn_flag OR triage_score NOT BETWEEN 0 AND 100
           OR evidence_coverage_pct NOT BETWEEN 0 AND 100
        """
    ).fetchone()[0]
    if invalid_triage:
        failures.append(f"account_triage contém {invalid_triage} linhas inválidas")

    invalid_scopes = con.execute(
        """
        SELECT COUNT(*) FROM gold.analysis_scope
        WHERE raw_rows <> eligible_rows + quarantined_rows
           OR coverage_pct < 0 OR coverage_pct > 100
        """
    ).fetchone()[0]
    if invalid_scopes:
        failures.append(f"analysis_scope contém {invalid_scopes} reconciliações inválidas")

    unknown_rules = con.execute(
        """
        SELECT COUNT(*) FROM gold.quality_issues i
        LEFT JOIN gold.quality_rule_catalog r USING (rule_id)
        WHERE r.rule_id IS NULL
        """
    ).fetchone()[0]
    if unknown_rules:
        failures.append(f"quality_issues contém {unknown_rules} regras desconhecidas")

    if failures:
        raise RuntimeError("Falha de reconciliação gold:\n- " + "\n- ".join(failures))


def _query_dicts(con: Any, query: str) -> list[dict[str, Any]]:
    cursor = con.execute(query)
    columns = [item[0] for item in cursor.description]
    return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]


def _report_context(
    con: Any,
    manifest: dict[str, Any],
    generated_at: datetime,
) -> dict[str, Any]:
    source_start, data_cutoff = con.execute(
        "SELECT source_start_date, data_cutoff FROM stage.dataset_bounds"
    ).fetchone()
    total_accounts = con.execute("SELECT COUNT(*) FROM gold.account_snapshot").fetchone()[0]
    snapshot_churned = con.execute(
        "SELECT COUNT(*) FROM gold.account_snapshot WHERE snapshot_churn_flag"
    ).fetchone()[0]
    valid_churn = con.execute(
        "SELECT COUNT(*) FROM stage.churn_events WHERE is_eligible"
    ).fetchone()[0]
    issue_count = con.execute("SELECT COUNT(*) FROM gold.quality_issues").fetchone()[0]
    return {
        "manifest_version": manifest["manifest_version"],
        "dataset_slug": manifest["source"]["dataset_slug"],
        "dataset_version": manifest["source"]["dataset_version"],
        "generated_at": generated_at.isoformat(),
        "data_cutoff": data_cutoff.isoformat(),
        "kpis": {
            "total_accounts": total_accounts,
            "source_table_count": len(RAW_TABLES),
            "valid_churn_events": valid_churn,
            "data_period": f"{source_start.isoformat()} to {data_cutoff.isoformat()}",
            "raw_total_rows": con.execute(
                "SELECT SUM(observed_rows) FROM meta.raw_manifest"
            ).fetchone()[0],
            "snapshot_churned_accounts": snapshot_churned,
            "quality_issue_count": issue_count,
        },
        "analysis_scope": _query_dicts(con, "SELECT * FROM gold.analysis_scope ORDER BY scope_id"),
    }


def _export_reviewable_gold(
    con: Any,
    export_dir: Path,
    manifest: dict[str, Any],
    generated_at: datetime,
) -> None:
    export_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ravenstack-gold-", dir=export_dir.parent) as temp:
        temporary_dir = Path(temp)
        for filename, (table, order_by) in EXPORTS.items():
            target = temporary_dir / filename
            con.execute(
                f"COPY (SELECT * FROM {table} ORDER BY {order_by}) TO ? "
                "(HEADER, DELIMITER ',', QUOTE '\"', ESCAPE '\"', NULL '')",
                [str(target)],
            )
        context = _report_context(con, manifest, generated_at)
        context_path = temporary_dir / "report_context.json"
        context_path.write_text(
            json.dumps(context, indent=2, ensure_ascii=False, default=str) + "\n",
            encoding="utf-8",
        )
        export_dir.mkdir(parents=True, exist_ok=True)
        for source in sorted(temporary_dir.iterdir()):
            os.replace(source, export_dir / source.name)


def build(config: BuildConfig | None = None) -> BuildResult:
    config = config or BuildConfig.defaults()
    generated_at = datetime.now(timezone.utc)
    manifest, verified = ensure_raw_data(
        raw_dir=config.raw_dir,
        manifest_path=config.manifest_path,
        source_dir=config.source_dir,
        force_download=config.force_download,
    )

    config.database_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_db = config.database_path.with_suffix(config.database_path.suffix + ".building")
    if temporary_db.exists():
        temporary_db.unlink()

    con = duckdb.connect(str(temporary_db))
    try:
        con.execute(_read_sql(config, "00_raw.sql"))
        _load_raw_tables(con, config.raw_dir)
        _insert_metadata(con, manifest, verified, generated_at)
        con.execute(_read_sql(config, "10_stage.sql"))
        con.execute(_read_sql(config, "20_gold.sql"))
        build_statistical_tests(con)
        validate_contracts(con)
        if config.export_csv:
            _export_reviewable_gold(con, config.export_dir, manifest, generated_at)

        data_cutoff = con.execute("SELECT data_cutoff FROM stage.dataset_bounds").fetchone()[0]
        raw_rows, eligible_rows, quarantined_rows = con.execute(
            """
            SELECT SUM(raw_rows), SUM(eligible_rows), SUM(quarantined_rows)
            FROM gold.analysis_scope
            WHERE scope_id IN ('accounts_snapshot', 'subscriptions_observed', 'usage_temporal',
                               'support_temporal', 'churn_event_ledger')
            """
        ).fetchone()
        con.execute("CHECKPOINT")
    except Exception:
        con.close()
        if temporary_db.exists():
            temporary_db.unlink()
        raise
    else:
        con.close()

    os.replace(temporary_db, config.database_path)
    return BuildResult(
        database_path=config.database_path,
        export_dir=config.export_dir,
        manifest_version=manifest["manifest_version"],
        data_cutoff=data_cutoff.isoformat(),
        raw_rows=int(raw_rows),
        eligible_rows=int(eligible_rows),
        quarantined_rows=int(quarantined_rows),
    )
