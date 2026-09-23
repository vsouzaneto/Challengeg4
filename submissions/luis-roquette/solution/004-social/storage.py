"""Durable, local decision log for the social cockpit."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import date, datetime, timezone, tzinfo
from pathlib import Path
from typing import Any
from collections.abc import Callable

from analysis import METHOD_VERSION


SCHEMA_VERSION = 1


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _source_timezone(scope: dict[str, object]) -> tzinfo | None:
    """Return the source's declared offset, or keep its civil time naive."""
    for key in ("target_start", "target_end_exclusive"):
        value = scope.get(key)
        if value:
            return datetime.fromisoformat(str(value)).tzinfo
    return None


def _civil_date(value: datetime, source_timezone: tzinfo | None) -> date:
    """Project an instant onto the source calendar without inventing an offset."""
    if source_timezone is not None and value.tzinfo is not None:
        value = value.astimezone(source_timezone)
    return value.date()


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    initialize(conn)
    return conn


def initialize(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys=ON")
    with conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS imports (
                source_hash TEXT PRIMARY KEY,
                file_name TEXT NOT NULL,
                byte_count INTEGER NOT NULL CHECK(byte_count >= 0),
                row_count INTEGER NOT NULL CHECK(row_count >= 0),
                columns_json TEXT NOT NULL,
                period_start TEXT NOT NULL,
                period_end TEXT NOT NULL,
                platforms_json TEXT NOT NULL,
                imported_at TEXT NOT NULL,
                method_version TEXT NOT NULL,
                schema_version INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS decisions (
                decision_id TEXT PRIMARY KEY,
                event_id TEXT NOT NULL UNIQUE,
                recommendation_key TEXT NOT NULL,
                revision_of TEXT REFERENCES decisions(decision_id),
                source_hash TEXT NOT NULL REFERENCES imports(source_hash),
                decided_at TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('accepted', 'rejected', 'edited')),
                original_text TEXT NOT NULL,
                edited_text TEXT NOT NULL,
                owner TEXT NOT NULL,
                execution_window TEXT NOT NULL,
                scope_json TEXT NOT NULL,
                baseline_json TEXT NOT NULL,
                method_version TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS outcomes (
                outcome_id TEXT PRIMARY KEY,
                event_id TEXT NOT NULL UNIQUE,
                decision_id TEXT NOT NULL REFERENCES decisions(decision_id),
                source_hash TEXT NOT NULL REFERENCES imports(source_hash),
                recorded_at TEXT NOT NULL,
                execution_status TEXT NOT NULL CHECK(execution_status IN ('yes', 'no', 'unknown')),
                execution_date TEXT,
                observed_json TEXT NOT NULL,
                comparison_json TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('observed', 'pending')),
                reason TEXT NOT NULL,
                method_version TEXT NOT NULL
            );
            """
        )
        rows = conn.execute("SELECT version FROM schema_version").fetchall()
        if not rows:
            conn.execute("INSERT INTO schema_version(version) VALUES (?)", (SCHEMA_VERSION,))
        elif len(rows) != 1 or rows[0][0] != SCHEMA_VERSION:
            raise RuntimeError(f"schema SQLite incompatível: esperado {SCHEMA_VERSION}")


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _decoded(value: str) -> Any:
    return json.loads(value)


def record_import(conn: sqlite3.Connection, metadata: dict[str, object]) -> str:
    source_hash = str(metadata["source_hash"])
    with conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO imports (
                source_hash, file_name, byte_count, row_count, columns_json,
                period_start, period_end, platforms_json, imported_at,
                method_version, schema_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source_hash,
                Path(str(metadata["file_name"])).name,
                int(metadata["byte_count"]),
                int(metadata["row_count"]),
                _json(metadata["columns"]),
                str(metadata["period_start"]),
                str(metadata["period_end"]),
                _json(metadata["platforms"]),
                str(metadata["imported_at"]),
                str(metadata["method_version"]),
                SCHEMA_VERSION,
            ),
        )
    return source_hash


def record_decision(conn: sqlite3.Connection, event: dict[str, object]) -> str:
    existing = conn.execute(
        "SELECT decision_id FROM decisions WHERE event_id = ?", (str(event["event_id"]),)
    ).fetchone()
    if existing:
        return str(existing[0])

    status = str(event["status"])
    edited_text = str(event.get("edited_text", "")).strip() if status == "edited" else ""
    if status == "edited" and not edited_text:
        raise ValueError("Informe o texto editado antes de registrar.")
    baseline = event["baseline"]
    revision_of = event.get("revision_of")
    if revision_of:
        original = conn.execute(
            "SELECT baseline_json FROM decisions WHERE decision_id = ?", (str(revision_of),)
        ).fetchone()
        if original is None:
            raise sqlite3.IntegrityError("revision_of inexistente")
        baseline = _decoded(str(original[0]))

    decision_id = str(uuid.uuid4())
    with conn:
        conn.execute(
            """
            INSERT INTO decisions (
                decision_id, event_id, recommendation_key, revision_of,
                source_hash, decided_at, status, original_text, edited_text,
                owner, execution_window, scope_json, baseline_json, method_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                decision_id,
                str(event["event_id"]),
                str(event["recommendation_key"]),
                str(revision_of) if revision_of else None,
                str(event["source_hash"]),
                str(event["decided_at"]),
                status,
                str(event["original_text"]),
                edited_text,
                str(event["owner"]),
                str(event["execution_window"]),
                _json(event["scope"]),
                _json(baseline),
                str(event["method_version"]),
            ),
        )
    return decision_id


def _outcome_assessment(decision: dict[str, object], event: dict[str, object], now: datetime) -> tuple[str, str, dict[str, object]]:
    baseline = decision["baseline"]
    observed = event["observed"]
    assert isinstance(baseline, dict) and isinstance(observed, dict)
    comparison = {
        "baseline_median": baseline.get("median"),
        "observed_median": observed.get("median"),
        "median_delta": None,
        "baseline_volume_per_day": None,
        "observed_volume_per_day": None,
        "coverage_equal": baseline.get("coverage_days") == observed.get("coverage_days"),
    }
    baseline_days = int(baseline.get("coverage_days", 0) or 0)
    observed_days = int(observed.get("coverage_days", 0) or 0)
    if str(event["source_hash"]) == str(decision["source_hash"]):
        return "pending", "same_source", comparison
    if str(event["method_version"]) != str(decision["method_version"]) or str(decision["method_version"]) != METHOD_VERSION:
        return "pending", "method_mismatch", comparison
    if not baseline.get("contract"):
        return "pending", "baseline_contract_unavailable", comparison
    if baseline["contract"] != observed.get("contract"):
        return "pending", "evidence_contract_mismatch", comparison
    if any(baseline.get(key) != observed.get(key) for key in ("statistic", "unit")):
        return "pending", "statistic_or_unit_mismatch", comparison
    decision_scope = decision["scope"]
    event_scope = event.get("scope", decision_scope)
    assert isinstance(decision_scope, dict) and isinstance(event_scope, dict)
    decision_controls = {
        "filters": decision_scope.get("filters", decision_scope),
        "strict_audience": decision_scope.get("strict_audience", False),
    }
    event_controls = {
        "filters": event_scope.get("filters", event_scope),
        "strict_audience": event_scope.get("strict_audience", False),
    }
    if event_controls != decision_controls:
        return "pending", "incompatible_scope", comparison
    if observed.get("metric") != baseline.get("metric"):
        return "pending", "metric_mismatch", comparison
    if baseline_days:
        comparison["baseline_volume_per_day"] = float(baseline.get("views", 0)) / baseline_days
    if observed_days:
        comparison["observed_volume_per_day"] = float(observed.get("views", 0)) / observed_days
    if baseline.get("median") is not None and observed.get("median") is not None:
        comparison["median_delta"] = float(observed["median"]) - float(baseline["median"])
    if date.fromisoformat(str(observed["period_start"])) <= date.fromisoformat(str(baseline["period_end"])):
        return "pending", "overlapping_window", comparison
    if int(baseline.get("n_rate", 0)) < 30 or int(baseline.get("creators", 0)) < 5 or int(observed.get("n_rate", 0)) < 30 or int(observed.get("creators", 0)) < 5:
        return "pending", "insufficient_sample", comparison
    if baseline_days != observed_days:
        return "pending", "coverage_mismatch", comparison

    execution_status = str(event["execution_status"])
    execution_date = event.get("execution_date")
    source_timezone = _source_timezone(event_scope)
    recorded = datetime.fromisoformat(str(event["recorded_at"]))
    recorded_date = _civil_date(recorded, source_timezone)
    as_of = min(_civil_date(now, source_timezone), recorded_date)
    if execution_date and date.fromisoformat(str(execution_date)) > as_of:
        return "pending", "execution_in_future", comparison
    if date.fromisoformat(str(observed["period_end"])) > as_of:
        return "pending", "observation_in_future", comparison
    decided_at = datetime.fromisoformat(str(decision["decided_at"]))
    decision_date = _civil_date(decided_at, source_timezone)
    observed_start = date.fromisoformat(str(observed["period_start"]))
    if execution_status == "yes" and not execution_date:
        return "pending", "execution_date_unknown", comparison
    if execution_status == "yes" and date.fromisoformat(str(execution_date)) < decision_date:
        return "pending", "execution_before_decision", comparison
    if observed_start <= decision_date:
        return "pending", "observed_before_or_on_decision", comparison
    if execution_status == "yes" and observed_start <= date.fromisoformat(str(execution_date)):
        return "pending", "observed_before_execution", comparison
    if execution_status == "yes":
        return "observed", "comparable_after_declared_execution", comparison
    if execution_status == "no":
        return "observed", "comparable_action_not_executed", comparison
    return "observed", "comparable_execution_unknown", comparison


def record_outcome(conn: sqlite3.Connection, event: dict[str, object], *,
                   clock: Callable[[], datetime] | None = None, simulation: bool = False) -> str:
    existing = conn.execute(
        "SELECT outcome_id FROM outcomes WHERE event_id = ?", (str(event["event_id"]),)
    ).fetchone()
    if existing:
        return str(existing[0])
    row = conn.execute(
        """SELECT decision_id, source_hash, scope_json, baseline_json, method_version, decided_at
           FROM decisions WHERE decision_id = ?""",
        (str(event["decision_id"]),),
    ).fetchone()
    if row is None:
        raise sqlite3.IntegrityError("decision_id inexistente")
    decision = {
        "decision_id": row[0],
        "source_hash": row[1],
        "scope": _decoded(row[2]),
        "baseline": _decoded(row[3]),
        "method_version": row[4],
        "decided_at": row[5],
    }
    status, reason, comparison = _outcome_assessment(decision, event, (clock or utc_now)())
    outcome_id = str(uuid.uuid4())
    with conn:
        conn.execute(
            """
            INSERT INTO outcomes (
                outcome_id, event_id, decision_id, source_hash, recorded_at,
                execution_status, execution_date, observed_json, comparison_json,
                status, reason, method_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                outcome_id,
                str(event["event_id"]),
                str(event["decision_id"]),
                str(event["source_hash"]),
                str(event["recorded_at"]),
                str(event["execution_status"]),
                str(event["execution_date"]) if event.get("execution_date") else None,
                _json({**event["observed"], "scope": event.get("scope", decision["scope"]), "simulation": simulation}),
                _json(comparison),
                status,
                reason,
                str(event["method_version"]),
            ),
        )
    return outcome_id


def list_decisions(conn: sqlite3.Connection) -> list[dict[str, object]]:
    decision_rows = conn.execute(
        """SELECT decision_id, event_id, recommendation_key, revision_of,
                  source_hash, decided_at, status, original_text, edited_text,
                  owner, execution_window, scope_json, baseline_json, method_version
           FROM decisions ORDER BY decided_at, decision_id"""
    ).fetchall()
    items: list[dict[str, object]] = []
    for row in decision_rows:
        item: dict[str, object] = {
            "decision_id": row[0], "event_id": row[1], "recommendation_key": row[2],
            "revision_of": row[3], "source_hash": row[4], "decided_at": row[5],
            "status": row[6], "original_text": row[7], "edited_text": row[8],
            "owner": row[9], "execution_window": row[10], "scope": _decoded(row[11]),
            "baseline": _decoded(row[12]), "method_version": row[13], "outcomes": [],
        }
        outcome_rows = conn.execute(
            """SELECT outcome_id, event_id, source_hash, recorded_at,
                      execution_status, execution_date, observed_json,
                      comparison_json, status, reason, method_version
               FROM outcomes WHERE decision_id = ? ORDER BY recorded_at, outcome_id""",
            (row[0],),
        ).fetchall()
        item["outcomes"] = [
            {
                "outcome_id": outcome[0], "event_id": outcome[1], "source_hash": outcome[2],
                "recorded_at": outcome[3], "execution_status": outcome[4],
                "execution_date": outcome[5], "observed": _decoded(outcome[6]),
                "comparison": _decoded(outcome[7]), "status": outcome[8],
                "reason": outcome[9], "method_version": outcome[10],
                "scope": _decoded(outcome[6]).get("scope"),
            }
            for outcome in outcome_rows
        ]
        items.append(item)
    return items
