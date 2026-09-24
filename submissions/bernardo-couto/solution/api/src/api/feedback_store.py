"""Append-only store for seller actions: ``data/feedback/actions.parquet``.

Writes are atomic (temp file + ``os.replace``) and serialised by a process-wide lock. The file
is tiny (one row per click), so read-concat-rewrite is the simplest correct strategy; it also
keeps a single parquet file that the pipeline can later join by ``opportunity_id``.
"""

from __future__ import annotations

import os
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from api.schemas import FeedbackCreate, FeedbackRecord, ScoredDeal

_LOCK = threading.Lock()

FEEDBACK_SCHEMA = pa.schema(
    [
        ("id", pa.string()),
        ("opportunity_id", pa.string()),
        ("action", pa.string()),
        ("note", pa.string()),
        ("actor", pa.string()),
        ("recorded_at", pa.timestamp("us", tz="UTC")),
        ("as_of", pa.date32()),
        ("model_version", pa.string()),
        ("priority_score", pa.float64()),
    ]
)


def build_record(payload: FeedbackCreate, deal: ScoredDeal) -> FeedbackRecord:
    return FeedbackRecord(
        id=uuid.uuid4().hex,
        opportunity_id=payload.opportunity_id,
        action=payload.action,
        note=payload.note,
        actor=payload.actor,
        recorded_at=datetime.now(UTC),  # leakage-ok: audit timestamp, never used in scoring
        as_of=deal.as_of,
        model_version=deal.model_version,
        priority_score=deal.priority_score,
    )


def append_record(path: Path, record: FeedbackRecord) -> int:
    """Append one row atomically; returns the number of rows in the file afterwards."""
    with _LOCK:
        path.parent.mkdir(parents=True, exist_ok=True)
        new_table = pa.Table.from_pylist([_to_row(record)], schema=FEEDBACK_SCHEMA)
        if path.is_file():
            existing = pq.read_table(str(path)).cast(FEEDBACK_SCHEMA)
            table = pa.concat_tables([existing, new_table])
        else:
            table = new_table
        tmp = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
        try:
            pq.write_table(table, str(tmp))
            os.replace(tmp, path)
        finally:
            if tmp.exists():
                tmp.unlink()
        return int(table.num_rows)


def read_records(path: Path) -> list[FeedbackRecord]:
    if not path.is_file():
        return []
    rows = pq.read_table(str(path)).to_pylist()
    return [FeedbackRecord.model_validate(r) for r in rows]


def _to_row(record: FeedbackRecord) -> dict[str, object]:
    row = record.model_dump()
    row["action"] = record.action.value
    return row
