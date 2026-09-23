"""Committed, sanitized audit events; runtime data never belongs in Git.

Optional empty strings become SQL NULL (empty CSV cells); tuple fields become
compact JSON. CSV alone prefixes formula-like text with an apostrophe, retaining
the original sanitized value in SQLite. ExportResult.content is read from the
persisted file. Publish uses link/unlink, the stdlib atomic no-clobber equivalent
of rename: an existing destination is never replaced, even during a race.

Callers own connections and must close them, e.g. with contextlib.closing.
Use idle connections: pending caller transactions are rejected without changing
them. record_decision owns its transaction; UI must reread using a new connection
before announcing success. initialize_store never migrates/resets existing data.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
import re
import sqlite3
import tempfile
import unicodedata
from contextlib import closing
from dataclasses import asdict, dataclass, fields, replace
from datetime import UTC, datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Literal
from uuid import UUID

from support_copilot.data import CUSTOMER_TAXONOMY, IT_TAXONOMY, Domain, sanitize_text


@dataclass(frozen=True, kw_only=True)
class DecisionEvent:
    submission_id: str
    ticket_id: str
    domain: Domain
    data_version: str | None
    model_version: str | None
    rules_version: str | None
    retrieval_version: str | None
    threshold: float | None
    retrieval_threshold: float | None
    prediction_status: Literal["ok", "unsupported", "unavailable", "invalid_input"]
    suggested_label: str | None
    confidence: float | None
    gate_action: Literal["auto_route", "human_review"]
    reason_codes: tuple[str, ...]
    source_ids: tuple[str, ...]
    human_action: Literal["approve", "edit_approve", "reject", "escalate"]
    human_reason: str | None
    suggestion_text: str | None
    final_text: str | None


@dataclass(frozen=True, kw_only=True)
class StoredDecision(DecisionEvent):
    id: int
    created_at: str
    edit_ratio: float | None


@dataclass(frozen=True)
class ExportResult:
    path: Path
    content: bytes
    row_count: int
    sha256: str


EVENT_FIELDS = tuple(field.name for field in fields(DecisionEvent))
CSV_FIELDS = tuple(field.name for field in fields(StoredDecision))
_LIST_FIELDS = {"reason_codes", "source_ids"}
_NUMBER_FIELDS = {"threshold", "retrieval_threshold", "confidence", "edit_ratio"}
_REQUIRED = {"submission_id", "ticket_id", "domain", "prediction_status", "gate_action",
             "reason_codes", "source_ids", "human_action", "created_at"}
_COLUMNS = ", ".join(
    "id INTEGER PRIMARY KEY" if name == "id" else
    f"{name} {'REAL' if name in _NUMBER_FIELDS else 'TEXT'}"
    + (" NOT NULL" if name in _REQUIRED else "")
    + (" UNIQUE" if name == "submission_id" else "")
    for name in CSV_FIELDS
)
_SCHEMA = f"CREATE TABLE decisions ({_COLUMNS})"
_RISK_REASONS = frozenset({
    "empty_or_tokenless_input", "privacy_failed", "artifact_invalid", "domain_mismatch",
    "invalid_prediction", "ood_zero_vector", "ood_check_unavailable", "unknown_priority",
    "risk_detector_unavailable", "invalid_input", "critical_priority", "ambiguous_input",
    "invalid_or_private_input", "model_version_mismatch",
})


def _idle(connection: sqlite3.Connection) -> None:
    if connection.in_transaction:
        raise ValueError("store_transaction_active: finish caller transaction first")


def _schema(connection: sqlite3.Connection) -> None:
    if connection.execute("PRAGMA user_version").fetchone()[0] != 1:
        raise ValueError("store_schema_unknown: preserve database; use compatible application")
    row = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='decisions'"
    ).fetchone()
    if row is None or row[0] != _SCHEMA:
        raise ValueError("store_schema_incompatible: preserve database; inspect schema")


def initialize_store(path: Path) -> None:
    """Create schema v1 only for an empty database, preserving unknown databases."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path, isolation_level=None)) as connection:
        connection.execute("BEGIN IMMEDIATE")
        try:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            existing = connection.execute("SELECT 1 FROM sqlite_master LIMIT 1").fetchone()
            if version == 0 and existing is None:
                connection.execute(_SCHEMA)
                connection.execute("PRAGMA user_version=1")
            _schema(connection)
            connection.execute("COMMIT")
        except BaseException:
            connection.execute("ROLLBACK")
            raise


def _token(value: str | None, field: str, *, optional: bool = False) -> str | None:
    if optional and (value is None or isinstance(value, str) and not value.strip()):
        return None
    if not isinstance(value, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.:-]*", value):
        raise ValueError(f"invalid_snapshot:{field}")
    return value


def _validate(event: DecisionEvent) -> DecisionEvent:
    if not isinstance(event, DecisionEvent):
        raise ValueError("invalid_snapshot:event")
    try:
        submission_id = str(UUID(event.submission_id))
    except (ValueError, TypeError, AttributeError):
        raise ValueError("invalid_snapshot:submission_id") from None
    if event.domain not in ("customer", "it"):
        raise ValueError("invalid_snapshot:domain")
    _token(event.ticket_id, "ticket_id")
    if not event.ticket_id.startswith(f"{event.domain}:"):
        raise ValueError("invalid_snapshot:ticket_domain")
    updates = {field: _token(getattr(event, field), field, optional=True)
               for field in ("data_version", "model_version", "rules_version", "retrieval_version")}
    for field in ("human_reason", "suggestion_text", "final_text"):
        updates[field] = sanitize_text(getattr(event, field)) or None
    if isinstance(event.suggested_label, str) and not event.suggested_label.strip():
        updates["suggested_label"] = None
    event = replace(event, submission_id=submission_id, **updates)
    for field in _LIST_FIELDS:
        values = getattr(event, field)
        if not isinstance(values, tuple):
            raise ValueError(f"invalid_snapshot:{field}")
        for value in values:
            if field == "reason_codes" and isinstance(value, str) and value.startswith("category:"):
                if value.removeprefix("category:") not in (*CUSTOMER_TAXONOMY, *IT_TAXONOMY):
                    raise ValueError("invalid_snapshot:reason_category")
            elif field == "reason_codes" and isinstance(value, str) and value.startswith("text:"):
                if sanitize_text(value) != value or not value.removeprefix("text:"):
                    raise ValueError("invalid_snapshot:reason_text")
            else:
                _token(value, field)
    if len(event.source_ids) > 3 or len(set(event.source_ids)) != len(event.source_ids):
        raise ValueError("invalid_snapshot:source_ids")
    if any(not value.startswith("customer:") for value in event.source_ids):
        raise ValueError("invalid_snapshot:source_domain")
    for field in ("threshold", "retrieval_threshold", "confidence"):
        value = getattr(event, field)
        if value is not None and (isinstance(value, bool) or not isinstance(value, (float, int))
                                  or not math.isfinite(value) or not 0 <= value <= 1):
            raise ValueError(f"invalid_snapshot:{field}")
    if event.prediction_status not in ("ok", "unsupported", "unavailable", "invalid_input"):
        raise ValueError("invalid_snapshot:prediction_status")
    if event.prediction_status == "ok":
        taxonomy = CUSTOMER_TAXONOMY if event.domain == "customer" else IT_TAXONOMY
        if (event.suggested_label not in taxonomy or event.confidence is None
                or event.model_version is None or event.data_version is None):
            raise ValueError("invalid_snapshot:prediction")
    elif event.suggested_label is not None or event.confidence is not None:
        raise ValueError("invalid_snapshot:unavailable_prediction")
    if event.gate_action not in ("auto_route", "human_review"):
        raise ValueError("invalid_snapshot:gate_action")
    risk_blocked = any(reason in _RISK_REASONS or reason.startswith(("category:", "text:"))
                       for reason in event.reason_codes)
    if event.gate_action == "auto_route":
        if (event.prediction_status != "ok" or event.threshold is None
                or event.confidence < event.threshold or event.rules_version is None
                or event.reason_codes != ("validated_threshold",)):
            raise ValueError("invalid_snapshot:auto_route")
    elif not event.reason_codes:
        raise ValueError("invalid_snapshot:missing_reasons")
    elif "validated_threshold" in event.reason_codes:
        raise ValueError("invalid_snapshot:human_review")
    if event.suggestion_text is not None:
        if (event.domain != "customer" or event.prediction_status != "ok"
                or event.retrieval_version is None or event.retrieval_threshold is None
                or event.rules_version is None or not event.source_ids or risk_blocked):
            raise ValueError("invalid_snapshot:draft_provenance")
    if event.human_action in ("approve", "edit_approve"):
        if event.suggestion_text is None or event.final_text is None:
            raise ValueError("invalid_action:draft_and_final_required")
        if event.human_action == "approve" and event.final_text != event.suggestion_text:
            raise ValueError("invalid_action:approve_must_match_draft")
    elif event.human_action in ("reject", "escalate"):
        if event.human_reason is None or event.final_text is not None:
            raise ValueError("invalid_action:reason_required_and_final_must_be_null")
    else:
        raise ValueError("invalid_action:human_action")
    return event


def _row(row) -> StoredDecision:
    values = dict(zip(CSV_FIELDS, row, strict=True))
    for field in _LIST_FIELDS:
        values[field] = tuple(json.loads(values[field]))
    return StoredDecision(**values)


def record_decision(connection: sqlite3.Connection, event: DecisionEvent) -> StoredDecision:
    """Commit one normalized event, or return its existing identical submission."""
    _idle(connection)
    _schema(connection)
    event = _validate(event)
    connection.execute("BEGIN IMMEDIATE")
    try:
        row = connection.execute(
            f"SELECT {', '.join(CSV_FIELDS)} FROM decisions WHERE submission_id=?",
            (event.submission_id,),
        ).fetchone()
        if row is not None:
            stored = _row(row)
            if any(getattr(stored, field) != getattr(event, field) for field in EVENT_FIELDS):
                raise ValueError("submission_conflict: UUID already used for a different event")
        else:
            values = asdict(event)
            for field in _LIST_FIELDS:
                values[field] = json.dumps(values[field], ensure_ascii=False, separators=(",", ":"))
            values["created_at"] = datetime.now(UTC).isoformat()
            values["edit_ratio"] = (
                1 - SequenceMatcher(None, event.suggestion_text, event.final_text).ratio()
                if event.human_action in ("approve", "edit_approve") else None
            )
            cursor = connection.execute(
                f"INSERT INTO decisions ({', '.join(values)}) "
                f"VALUES ({', '.join('?' for _ in values)})", tuple(values.values()),
            )
            stored = _row(connection.execute(
                f"SELECT {', '.join(CSV_FIELDS)} FROM decisions WHERE id=?", (cursor.lastrowid,),
            ).fetchone())
        connection.execute("COMMIT")
        return stored
    except BaseException:
        if connection.in_transaction:
            connection.execute("ROLLBACK")
        raise


def list_decisions(connection: sqlite3.Connection) -> list[StoredDecision]:
    """Read one committed snapshot in ID order; never expose a pending transaction."""
    _idle(connection)
    _schema(connection)
    return [_row(row) for row in connection.execute(
        f"SELECT {', '.join(CSV_FIELDS)} FROM decisions ORDER BY id"
    ).fetchall()]


def _csv_text(value: str) -> str:
    for character in value:
        if character in "\t\r\n=+-@":
            return "'" + value
        if not (character.isspace() or unicodedata.category(character).startswith("C")):
            break
    return value


def export_decisions_csv(connection: sqlite3.Connection, destination: Path) -> ExportResult:
    """Persist all committed fields; refuse to overwrite any existing export."""
    decisions = list_decisions(connection)
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(CSV_FIELDS)
    for decision in decisions:
        values = asdict(decision)
        for field in _LIST_FIELDS:
            values[field] = json.dumps(values[field], ensure_ascii=False, separators=(",", ":"))
        writer.writerow([_csv_text(value) if isinstance(value, str) else value
                         for value in values.values()])
    content = stream.getvalue().encode("utf-8")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".decisions-",
                                         suffix=".tmp", delete=False) as output:
            temporary = Path(output.name)
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        os.link(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    persisted = destination.read_bytes()
    return ExportResult(
        destination, persisted, len(decisions), hashlib.sha256(persisted).hexdigest(),
    )
