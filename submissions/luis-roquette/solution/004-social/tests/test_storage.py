from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone

from analysis import METHOD_VERSION

from storage import initialize, list_decisions, record_decision, record_import, record_outcome


def import_event(source_hash: str = "source-a") -> dict[str, object]:
    return {
        "source_hash": source_hash,
        "file_name": "social.csv",
        "byte_count": 1234,
        "row_count": 60,
        "columns": ["id", "platform"],
        "period_start": "2025-01-01T00:00:00",
        "period_end": "2025-01-31T00:00:00",
        "platforms": ["Instagram"],
        "imported_at": "2026-09-21T20:00:00+00:00",
        "method_version": METHOD_VERSION,
    }


def expected_baseline() -> dict[str, object]:
    return {
        "period_start": "2025-01-01",
        "period_end": "2025-01-07",
        "metric": "erv",
        "median": 4.0,
        "views": 700,
        "interactions": 28,
        "n_rate": 30,
        "creators": 5,
        "coverage_days": 7,
        "source_row_ids": ["source-a:1"],
        "statistic": "median_post_erv", "unit": "percent",
        "contract": {"metric": "erv", "unit": "percent", "statistic": "median_post_erv", "context": {"platform": "Instagram"}},
    }


def decision_event(**overrides: object) -> dict[str, object]:
    event: dict[str, object] = {
        "event_id": "event-decision-1",
        "recommendation_key": "recommendation-1",
        "revision_of": None,
        "source_hash": "source-a",
        "decided_at": "2025-01-07T20:05:00+00:00",
        "status": "accepted",
        "original_text": "Testar dois vídeos no contexto.",
        "edited_text": "",
        "owner": "Gestor de Social Media",
        "execution_window": "próximos 7 dias",
        "scope": {"platform": "Instagram", "content_type": "video"},
        "baseline": expected_baseline(),
        "method_version": METHOD_VERSION,
    }
    event.update(overrides)
    return event


def revision_event(original_id: str) -> dict[str, object]:
    return decision_event(
        event_id="event-decision-2",
        revision_of=original_id,
        status="edited",
        edited_text="Testar somente um vídeo.",
        baseline={**expected_baseline(), "median": 99.0},
    )


def outcome_event(**overrides: object) -> dict[str, object]:
    event: dict[str, object] = {
        "event_id": "event-outcome-1",
        "decision_id": "decision-placeholder",
        "source_hash": "source-b",
        "recorded_at": "2026-09-21T20:10:00+00:00",
        "execution_status": "yes",
        "execution_date": "2025-01-07",
        "observed": {
            "period_start": "2025-01-08",
            "period_end": "2025-01-14",
            "metric": "erv",
            "median": 5.0,
            "views": 840,
            "interactions": 42,
            "n_rate": 30,
            "creators": 5,
            "coverage_days": 7,
            "statistic": "median_post_erv", "unit": "percent",
            "contract": expected_baseline()["contract"],
        },
        "method_version": METHOD_VERSION,
    }
    event.update(overrides)
    return event


class StorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")
        initialize(self.conn)
        record_import(self.conn, import_event())

    def tearDown(self) -> None:
        self.conn.close()

    def test_initialize_enables_foreign_keys_and_creates_versioned_schema(self) -> None:
        self.assertEqual(self.conn.execute("PRAGMA foreign_keys").fetchone()[0], 1)
        self.assertEqual(self.conn.execute("SELECT version FROM schema_version").fetchone()[0], 1)

    def test_same_import_hash_and_event_id_are_idempotent(self) -> None:
        self.assertEqual(record_import(self.conn, import_event()), record_import(self.conn, import_event()))
        first = record_decision(self.conn, decision_event())
        self.assertEqual(first, record_decision(self.conn, decision_event()))
        self.assertEqual(self.conn.execute("SELECT count(*) FROM decisions").fetchone()[0], 1)

    def test_new_human_event_is_distinct_and_survives_reopen(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cockpit.sqlite3"
            first = sqlite3.connect(path)
            initialize(first)
            record_import(first, import_event())
            one = record_decision(first, decision_event())
            two = record_decision(first, decision_event(event_id="event-decision-new", status="rejected"))
            first.close()
            reopened = sqlite3.connect(path)
            initialize(reopened)
            self.assertEqual({item["decision_id"] for item in list_decisions(reopened)}, {one, two})
            reopened.close()

    def test_decision_revision_preserves_original_baseline(self) -> None:
        original = record_decision(self.conn, decision_event())
        revised = record_decision(self.conn, revision_event(original))
        self.assertNotEqual(original, revised)
        stored = next(item for item in list_decisions(self.conn) if item["decision_id"] == original)
        revised_stored = next(item for item in list_decisions(self.conn) if item["decision_id"] == revised)
        self.assertEqual(stored["baseline"], expected_baseline())
        self.assertEqual(revised_stored["baseline"], expected_baseline())

    def test_failed_write_rolls_back_without_false_success(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            record_decision(self.conn, decision_event(source_hash="missing"))
        self.assertEqual(self.conn.execute("SELECT count(*) FROM decisions").fetchone()[0], 0)

    def test_decision_and_revision_text_match_status(self) -> None:
        original_id = record_decision(self.conn, decision_event())
        for revision_of in (None, original_id):
            for status in ("accepted", "rejected", "edited"):
                with self.subTest(revision_of=revision_of, status=status):
                    decision_id = record_decision(self.conn, decision_event(event_id=f"{revision_of}-{status}", revision_of=revision_of, status=status, edited_text="  Ação alterada.  "))
                    decision = next(item for item in list_decisions(self.conn) if item["decision_id"] == decision_id)
                    self.assertEqual(decision["edited_text"], "Ação alterada." if status == "edited" else "")
                    self.assertEqual(decision["original_text"], decision_event()["original_text"])
            before = len(list_decisions(self.conn))
            with self.assertRaisesRegex(ValueError, "texto editado"):
                record_decision(self.conn, decision_event(event_id=f"empty-{revision_of}", revision_of=revision_of, status="edited", edited_text=" \n "))
            self.assertEqual(len(list_decisions(self.conn)), before)

    def test_database_contains_no_raw_csv_or_source_text_fields(self) -> None:
        columns = {
            row[1]
            for table in ("imports", "decisions", "outcomes")
            for row in self.conn.execute(f"PRAGMA table_info({table})")
        }
        self.assertTrue({"csv_bytes", "content_description", "comments_text", "content_url"}.isdisjoint(columns))

    def test_valid_comparable_outcome_is_observed(self) -> None:
        decision_id = record_decision(self.conn, decision_event())
        record_import(self.conn, import_event("source-b"))
        outcome_id = record_outcome(self.conn, outcome_event(decision_id=decision_id))
        outcome = list_decisions(self.conn)[0]["outcomes"][0]
        self.assertEqual(outcome["outcome_id"], outcome_id)
        self.assertEqual(outcome["status"], "observed")
        self.assertEqual(outcome["reason"], "comparable_after_declared_execution")
        self.assertEqual(outcome["comparison"]["median_delta"], 1.0)

    def test_outcome_guards_remain_pending(self) -> None:
        decision_id = record_decision(self.conn, decision_event())
        record_import(self.conn, import_event("source-b"))
        cases = (
            ("same-source", {"source_hash": "source-a"}, "same_source"),
            ("overlap", {"observed": {**outcome_event()["observed"], "period_start": "2025-01-07"}}, "overlapping_window"),
            ("scope", {"scope": {"platform": "TikTok"}}, "incompatible_scope"),
            ("method", {"method_version": "1.0.0"}, "method_mismatch"),
            ("sample", {"observed": {**outcome_event()["observed"], "n_rate": 29}}, "insufficient_sample"),
            ("execution", {"execution_date": None}, "execution_date_unknown"),
            ("coverage", {"observed": {**outcome_event()["observed"], "period_end": "2025-02-06", "coverage_days": 30}}, "coverage_mismatch"),
        )
        for index, (label, changes, expected) in enumerate(cases):
            with self.subTest(label=label):
                event = outcome_event(event_id=f"outcome-{index}", decision_id=decision_id, **changes)
                if changes.get("source_hash") == "source-a":
                    pass
                record_outcome(self.conn, event)
                outcome = next(
                    item
                    for item in list_decisions(self.conn)[0]["outcomes"]
                    if item["event_id"] == f"outcome-{index}"
                )
                self.assertEqual(outcome["status"], "pending")
                self.assertEqual(outcome["reason"], expected)

    def test_no_and_unknown_execution_have_distinct_observation_reasons(self) -> None:
        decision_id = record_decision(self.conn, decision_event())
        record_import(self.conn, import_event("source-b"))
        for status, reason in (("no", "comparable_action_not_executed"), ("unknown", "comparable_execution_unknown")):
            with self.subTest(execution_status=status):
                outcome_id = record_outcome(self.conn, outcome_event(event_id=f"observation-{status}", decision_id=decision_id, execution_status=status, execution_date=None))
                outcome = next(item for item in list_decisions(self.conn)[0]["outcomes"] if item["outcome_id"] == outcome_id)
                self.assertEqual((outcome["status"], outcome["reason"], outcome["execution_status"]), ("observed", reason, status))

    def test_decision_execution_and_observation_chronology(self) -> None:
        record_import(self.conn, import_event("source-b"))
        cases = (
            ("2026-09-21T20:05:00+00:00", "yes", "2025-01-07", "pending", "execution_before_decision"),
            ("2026-09-21T20:05:00+00:00", "unknown", None, "pending", "observed_before_or_on_decision"),
            ("2026-09-21T20:05:00+00:00", "no", None, "pending", "observed_before_or_on_decision"),
            ("2025-01-08T00:00:00+00:00", "yes", "2025-01-08", "pending", "observed_before_or_on_decision"),
            ("2025-01-07T20:05:00+00:00", "yes", "2025-01-08", "pending", "observed_before_execution"),
            # With a naive source calendar, do not silently reinterpret this
            # timestamp as UTC: its written civil date is 2025-01-07.
            ("2025-01-07T23:30:00-03:00", "yes", "2025-01-07", "observed", "comparable_after_declared_execution"),
        )
        for index, (decided_at, execution_status, execution_date, status, reason) in enumerate(cases):
            with self.subTest(reason=reason, decided_at=decided_at):
                decision_id = record_decision(self.conn, decision_event(event_id=f"chronology-{index}", decided_at=decided_at))
                record_outcome(self.conn, outcome_event(event_id=f"chronology-outcome-{index}", decision_id=decision_id, execution_status=execution_status, execution_date=execution_date))
                outcome = next(item for item in list_decisions(self.conn) if item["decision_id"] == decision_id)["outcomes"][0]
                self.assertEqual((outcome["status"], outcome["reason"]), (status, reason))

    def test_source_calendar_drives_offset_and_naive_chronology_after_reopen(self) -> None:
        record_import(self.conn, import_event("source-b"))
        cases = (
            # Exact +14:00 reproduction: 23:00 UTC is already the next civil day.
            ("plus-14", "2025-01-15T00:00:00+14:00", "2025-01-14T23:00:00+00:00",
             "unknown", None, "2025-01-21", datetime(2025, 1, 22, 18, tzinfo=timezone.utc),
             "pending", "observed_before_or_on_decision"),
            # At -12:00 the decision still belongs to the previous source day;
            # execution on that source day is not falsely classified as earlier.
            ("minus-12", "2025-01-15T00:00:00-12:00", "2025-01-15T11:00:00+00:00",
             "yes", "2025-01-14", "2025-01-21", datetime(2025, 1, 22, 18, tzinfo=timezone.utc),
             "observed", "comparable_after_declared_execution"),
            # A naive source keeps the wall-calendar date exactly as declared.
            ("naive", "2025-01-15T00:00:00", "2025-01-14T23:30:00-12:00",
             "unknown", None, "2025-01-21", datetime(2025, 1, 21, 23, 45, tzinfo=timezone.utc),
             "observed", "comparable_execution_unknown"),
            # Future guards use the same +14:00 source calendar.
            ("plus-14-as-of", "2025-01-15T00:00:00+14:00", "2025-01-14T00:00:00+00:00",
             "unknown", None, "2025-01-22", datetime(2025, 1, 21, 11, tzinfo=timezone.utc),
             "observed", "comparable_execution_unknown"),
            # Declared execution uses that same as-of day (local 22, UTC 21).
            ("plus-14-execution-as-of", "2025-01-15T00:00:00+14:00", "2025-01-13T00:00:00+00:00",
             "yes", "2025-01-22", "2025-01-21", datetime(2025, 1, 21, 11, tzinfo=timezone.utc),
             "pending", "observed_before_execution"),
        )
        for name, target_start, decided_at, execution_status, execution_date, period_end, now, status, reason in cases:
            with self.subTest(name=name):
                controls = {"filters": {"platform": ["Instagram"]}, "strict_audience": False}
                decision_id = record_decision(
                    self.conn,
                    decision_event(
                        event_id=f"calendar-decision-{name}",
                        decided_at=decided_at,
                        scope={**controls, "target_start": target_start},
                    ),
                )
                record_outcome(
                    self.conn,
                    outcome_event(
                        event_id=f"calendar-outcome-{name}",
                        decision_id=decision_id,
                        execution_status=execution_status,
                        execution_date=execution_date,
                        scope={**controls, "target_start": target_start},
                        observed={**outcome_event()["observed"], "period_start": "2025-01-15", "period_end": period_end},
                        recorded_at=now.isoformat(),
                    ),
                    clock=lambda now=now: now,
                )
                self.conn.commit()
                with tempfile.TemporaryDirectory() as tmp:
                    path = Path(tmp) / "history.sqlite3"
                    persisted = sqlite3.connect(path)
                    self.conn.backup(persisted)
                    persisted.close()
                    reopened = sqlite3.connect(path)
                    stored = next(item for item in list_decisions(reopened) if item["decision_id"] == decision_id)
                    self.assertEqual((stored["outcomes"][0]["status"], stored["outcomes"][0]["reason"]), (status, reason))
                    reopened.close()

    def test_future_dates_and_forged_recording_clock_remain_pending(self):
        decision_id = record_decision(self.conn, decision_event())
        record_import(self.conn, import_event("source-b"))
        now = datetime(2025, 1, 10, tzinfo=timezone.utc)
        for index, (execution, expected) in enumerate((("2025-01-11", "execution_in_future"), ("2025-01-07", "observation_in_future"))):
            record_outcome(self.conn, outcome_event(event_id=f"future-{index}", decision_id=decision_id, execution_date=execution), clock=lambda: now)
            outcome = next(item for item in list_decisions(self.conn)[0]["outcomes"] if item["event_id"] == f"future-{index}")
            self.assertEqual((outcome["status"], outcome["reason"]), ("pending", expected))
            self.assertFalse(outcome["observed"]["simulation"])
        record_outcome(self.conn, outcome_event(event_id="before-window-ended", decision_id=decision_id,
                       recorded_at="2025-01-10T18:00:00+00:00"),
                       clock=lambda: datetime(2025, 1, 22, tzinfo=timezone.utc))
        outcome = next(item for item in list_decisions(self.conn)[0]["outcomes"] if item["event_id"] == "before-window-ended")
        self.assertEqual(outcome["reason"], "observation_in_future")

    def test_legacy_method_and_changed_statistic_or_context_cannot_compare(self):
        record_import(self.conn, import_event("source-b"))
        old_id = record_decision(self.conn, decision_event(method_version="1.0.0"))
        record_outcome(self.conn, outcome_event(decision_id=old_id, method_version="1.0.0"))
        self.assertEqual(list_decisions(self.conn)[0]["outcomes"][0]["reason"], "method_mismatch")
        current = record_decision(self.conn, decision_event(event_id="current"))
        for index, (change, reason) in enumerate((({"contract": {"context": {"platform": "TikTok"}}}, "evidence_contract_mismatch"), ({"statistic": "median_creator_erv"}, "statistic_or_unit_mismatch"), ({"unit": "ratio"}, "statistic_or_unit_mismatch"))):
            record_outcome(self.conn, outcome_event(event_id=f"contract-{index}", decision_id=current, observed={**outcome_event()["observed"], **change}))
            stored = next(item for item in list_decisions(self.conn) if item["decision_id"] == current)
            self.assertEqual(next(item for item in stored["outcomes"] if item["event_id"] == f"contract-{index}")["reason"], reason)


if __name__ == "__main__":
    unittest.main()
