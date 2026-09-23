"""Synthetic audit fixtures, never evidence of operational decisions."""

import csv
import hashlib
import io
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from dataclasses import asdict, fields, replace
from datetime import datetime
from difflib import SequenceMatcher
from uuid import uuid4

import pytest

from support_copilot import store
from support_copilot.decision import TAXONOMIES, base_policy, decide_route, derive_signals
from support_copilot.modeling import Prediction
from support_copilot.store import (
    DecisionEvent,
    StoredDecision,
    export_decisions_csv,
    initialize_store,
    list_decisions,
    record_decision,
)


def event(**changes):
    values = dict(
        submission_id=str(uuid4()), ticket_id="customer:1", domain="customer",
        data_version="data-v1", model_version="model-v1", rules_version="rules-v1",
        retrieval_version="retrieval-v1", threshold=0.8, retrieval_threshold=0.7,
        prediction_status="ok", suggested_label="Technical issue", confidence=0.95,
        gate_action="auto_route", reason_codes=("validated_threshold",),
        source_ids=("customer:2", "customer:3"), human_action="approve", human_reason=None,
        suggestion_text="restart the device", final_text="restart the device",
    )
    return DecisionEvent(**(values | changes))


@pytest.fixture
def database(tmp_path):
    path = tmp_path / "decisions.sqlite3"
    initialize_store(path)
    return path


def test_idempotency_and_fresh_connection_survive_restart(database):
    submission = event()
    with closing(sqlite3.connect(database)) as connection:
        first = record_decision(connection, submission)
        assert first.id == 1 and first.edit_ratio == 0
        assert datetime.fromisoformat(first.created_at).utcoffset().total_seconds() == 0
        assert not connection.in_transaction
        assert record_decision(connection, submission) == first
        with pytest.raises(ValueError, match="submission_conflict"):
            record_decision(connection, replace(submission, human_reason="different"))
        assert list_decisions(connection) == [first]
    initialize_store(database)
    with closing(sqlite3.connect(database)) as restarted:
        assert list_decisions(restarted) == [first]
        assert record_decision(restarted, submission) == first


def test_concurrent_duplicate_submission_is_one_committed_event(database):
    submission = event()

    def submit(_):
        with closing(sqlite3.connect(database)) as connection:
            return record_decision(connection, submission)

    with ThreadPoolExecutor(max_workers=2) as workers:
        first, second = workers.map(submit, range(2))
    assert first == second
    with closing(sqlite3.connect(database)) as connection:
        assert list_decisions(connection) == [first]


def test_rollback_of_actual_insert_failure_preserves_previous_record(database):
    with closing(sqlite3.connect(database)) as connection:
        saved = record_decision(connection, event())
        connection.execute("""CREATE TRIGGER fail_insert AFTER INSERT ON decisions
                              BEGIN SELECT RAISE(ABORT, 'injected failure'); END""")
        with pytest.raises(sqlite3.IntegrityError, match="injected failure"):
            record_decision(connection, event())
        assert not connection.in_transaction
        assert list_decisions(connection) == [saved]
    with closing(sqlite3.connect(database)) as restarted:
        assert list_decisions(restarted) == [saved]


def test_pending_caller_transaction_is_neither_committed_nor_rolled_back(database, tmp_path):
    with closing(sqlite3.connect(database)) as connection:
        saved = record_decision(connection, event())
        connection.execute("UPDATE decisions SET human_reason='pending' WHERE id=?", (saved.id,))
        for operation in (lambda: record_decision(connection, event()),
                          lambda: list_decisions(connection),
                          lambda: export_decisions_csv(connection, tmp_path / "pending.csv")):
            with pytest.raises(ValueError, match="transaction_active"):
                operation()
            assert connection.in_transaction
        with closing(sqlite3.connect(database)) as reader:
            assert list_decisions(reader) == [saved]
            exported = export_decisions_csv(reader, tmp_path / "committed.csv")
            assert b"pending" not in exported.content
        connection.rollback()
        assert list_decisions(connection) == [saved]


@pytest.mark.parametrize("version", [0, 2, 999])
def test_unknown_schema_preserves_existing_bytes(database, version):
    with closing(sqlite3.connect(database)) as connection:
        record_decision(connection, event())
        connection.execute(f"PRAGMA user_version={version}")
    before = database.read_bytes()
    with pytest.raises(ValueError, match="schema_unknown"):
        initialize_store(database)
    assert database.read_bytes() == before
    with closing(sqlite3.connect(database)) as connection:
        with pytest.raises(ValueError, match="schema_unknown"):
            record_decision(connection, event())
        assert connection.execute("SELECT COUNT(*) FROM decisions").fetchone() == (1,)


def test_incompatible_schema_is_not_recreated(tmp_path):
    path = tmp_path / "old.sqlite3"
    with closing(sqlite3.connect(path)) as connection:
        connection.execute("CREATE TABLE decisions (private TEXT)")
        connection.execute("PRAGMA user_version=1")
    before = path.read_bytes()
    with pytest.raises(ValueError, match="schema_incompatible"):
        initialize_store(path)
    assert path.read_bytes() == before


def test_human_text_sanitized_before_validation_comparison_and_persistence(database):
    with closing(sqlite3.connect(database)) as connection:
        saved = record_decision(connection, event(
            suggestion_text="contact help@example.invalid",
            final_text="contact other@example.invalid", human_reason="   ",
        ))
        assert saved.suggestion_text == saved.final_text == "contact [EMAIL]"
        assert saved.human_reason is None and saved.edit_ratio == 0
        edited = record_decision(connection, event(
            human_action="edit_approve", final_text="restart then call +55 (11) 99999-1234",
            human_reason="email help@example.invalid",
        ))
        assert edited.final_text == "restart then call [PHONE]"
        assert edited.human_reason == "email [EMAIL]"
        assert edited.edit_ratio == 1 - SequenceMatcher(
            None, edited.suggestion_text, edited.final_text
        ).ratio()
    payload = database.read_bytes()
    assert b"example.invalid" not in payload and b"99999" not in payload


@pytest.mark.parametrize("field", ["suggestion_text", "final_text", "human_reason"])
def test_unsafe_names_quarantined_without_echo_or_write(database, field):
    raw = "my name is jane"
    with closing(sqlite3.connect(database)) as connection:
        with pytest.raises(ValueError, match="privacy_quarantine") as error:
            record_decision(connection, event(**{field: raw}))
        assert raw not in str(error.value)
        assert list_decisions(connection) == []


@pytest.mark.parametrize("action", ["reject", "escalate"])
def test_unavailable_snapshot_and_abstention_record_nulls(database, action):
    with closing(sqlite3.connect(database)) as connection:
        saved = record_decision(connection, event(
            human_action=action, human_reason="manual review", final_text=None,
            suggestion_text=None, model_version=None, retrieval_version=" ",
            threshold=None, retrieval_threshold=None, suggested_label=" ",
            confidence=None, prediction_status="unavailable", source_ids=(),
            gate_action="human_review", reason_codes=("model_unavailable", "retrieval_unavailable"),
        ))
        assert saved.edit_ratio is None and saved.retrieval_version is None
        assert saved.data_version == "data-v1" and saved.rules_version == "rules-v1"
        assert list_decisions(connection) == [saved]


@pytest.mark.parametrize("changes", [
    {"human_action": "approve", "suggestion_text": None},
    {"human_action": "approve", "final_text": "different"},
    {"human_action": "edit_approve", "final_text": " \n\t"},
    {"human_action": "reject", "human_reason": "  ", "final_text": None},
    {"human_action": "escalate", "human_reason": "review"},
    {"human_action": "send"}, {"submission_id": "invalid"}, {"ticket_id": "it:1"},
    {"confidence": float("nan")}, {"threshold": float("inf")}, {"confidence": True},
    {"retrieval_threshold": -0.1}, {"confidence": 0.5}, {"suggested_label": "Hardware"},
    {"prediction_status": "unavailable"}, {"data_version": None}, {"rules_version": None},
    {"source_ids": ()}, {"retrieval_threshold": None}, {"retrieval_version": None},
    {"source_ids": ("it:1",)}, {"source_ids": ("customer:2", "customer:2")},
    {"gate_action": "human_review", "reason_codes": ()},
    {"reason_codes": ("help@example.invalid",)},
])
def test_invalid_actions_and_inconsistent_snapshots_do_not_write(database, changes):
    with closing(sqlite3.connect(database)) as connection:
        with pytest.raises(ValueError):
            record_decision(connection, event(**changes))
        assert list_decisions(connection) == []


@pytest.mark.parametrize("reason", ["critical_priority", "ambiguous_input", "privacy_failed",
                                   "ood_zero_vector", "ood_check_unavailable",
                                   "category:Billing inquiry", r"text:\bcredit card\b"])
def test_risk_snapshot_keeps_exact_reason_but_forbids_draft_and_auto_route(database, reason):
    with closing(sqlite3.connect(database)) as connection:
        with pytest.raises(ValueError, match="auto_route"):
            record_decision(connection, event(reason_codes=(reason,)))
        with pytest.raises(ValueError, match="draft_provenance"):
            record_decision(connection, event(gate_action="human_review", reason_codes=(reason,)))
        saved = record_decision(connection, event(
            gate_action="human_review", reason_codes=(reason,), suggestion_text=None,
            final_text=None, human_action="escalate", human_reason="manual review",
        ))
        assert saved.reason_codes == (reason,)


def test_low_routing_confidence_still_allows_safe_retrieval_draft(database):
    with closing(sqlite3.connect(database)) as connection:
        saved = record_decision(connection, event(
            gate_action="human_review", reason_codes=("below_threshold",), confidence=0.6,
        ))
        assert saved.human_action == "approve"


@pytest.mark.parametrize("gate_action,reasons", [
    ("auto_route", ()),
    ("auto_route", ("confidence_eligible",)),
    ("auto_route", ("below_threshold",)),
    ("auto_route", ("automation_disabled",)),
    ("auto_route", ("classification_unsupported",)),
    ("auto_route", ("no_eligible_threshold",)),
    ("auto_route", ("model_unavailable",)),
    ("auto_route", ("validated_threshold", "automation_disabled")),
    ("human_review", ("validated_threshold",)),
    ("human_review", ("validated_threshold", "critical_priority")),
])
def test_gate_reason_contradictions_preserve_previous_record(database, gate_action, reasons):
    with closing(sqlite3.connect(database)) as connection:
        prior = record_decision(connection, event())
        with pytest.raises(ValueError, match=f"invalid_snapshot:{gate_action}"):
            record_decision(connection, event(gate_action=gate_action, reason_codes=reasons))
        assert not connection.in_transaction
        assert list_decisions(connection) == [prior]


@pytest.mark.parametrize("confidence,priority,enabled,expected_reason", [
    (.95, "Low", True, "validated_threshold"),
    (.60, "Low", True, "below_threshold"),
    (.95, "Critical", True, "critical_priority"),
    (.95, "Low", False, "automation_disabled"),
])
def test_real_gate_outputs_persist_unchanged(database, confidence, priority, enabled,
                                          expected_reason):
    probabilities = dict.fromkeys(TAXONOMIES["customer"], (1 - confidence) / 4)
    probabilities["Technical issue"] = confidence
    prediction = Prediction("customer", "ok", "Technical issue", confidence,
                            probabilities, "model-v1", False)
    policy = replace(base_policy("customer", "model-v1"), automation_enabled=enabled,
                     threshold=.8, disabled_reason=None if enabled else "automation_disabled")
    signals = derive_signals("device stopped working", domain="customer", ticket_id="customer:1",
                             priority=priority, prediction=prediction, policy=policy,
                             artifact_valid=True, privacy_passed=True)
    route = decide_route(prediction, signals, policy)
    assert route.reason_codes == (expected_reason,)
    submission = event(gate_action=route.action, reason_codes=route.reason_codes,
                       threshold=route.threshold, rules_version=route.rules_version,
                       confidence=confidence)
    if priority == "Critical":
        submission = replace(submission, suggestion_text=None, final_text=None,
                             human_action="escalate", human_reason="manual review")
    with closing(sqlite3.connect(database)) as connection:
        saved = record_decision(connection, submission)
    with closing(sqlite3.connect(database)) as restarted:
        assert list_decisions(restarted) == [saved]
        assert (saved.gate_action, saved.reason_codes) == (route.action, route.reason_codes)


def test_export_round_trips_every_field_and_real_bytes(database, tmp_path):
    with closing(sqlite3.connect(database)) as connection:
        saved = [record_decision(connection, event()), record_decision(connection, event(
            human_action="escalate", human_reason="revisão necessária", final_text=None,
        ))]
        exported = export_decisions_csv(connection, tmp_path / "exports" / "one.csv")
    assert exported.row_count == 2
    assert exported.content == exported.path.read_bytes()
    assert exported.sha256 == hashlib.sha256(exported.content).hexdigest()
    assert b"\r\n" not in exported.content
    rows = list(csv.DictReader(io.StringIO(exported.content.decode("utf-8"))))
    assert tuple(rows[0]) == tuple(field.name for field in fields(StoredDecision))
    for decision, row in zip(saved, rows, strict=True):
        for key, value in asdict(decision).items():
            if isinstance(value, tuple):
                assert json.loads(row[key]) == list(value)
            else:
                assert row[key] == ("" if value is None else str(value))


@pytest.mark.parametrize("raw", ["=1+1", "+1+1", "-1+1", "@sum(1)", "  =1+1",
                                 "\ttext", "\rtext", "\ntext", " \x00=1+1",
                                 "\ufeff@sum(1)", "\u200b +1", "\v-1", " \ttext"])
def test_formula_prefixes_including_whitespace_and_controls(raw):
    assert store._csv_text(raw) == "'" + raw
    assert store._csv_text("safe " + raw) == "safe " + raw


def test_export_neutralizes_formula_without_changing_stored_text(database, tmp_path):
    with closing(sqlite3.connect(database)) as connection:
        saved = record_decision(connection, event(
            human_action="reject", human_reason=" =1+1", final_text=None,
        ))
        exported = export_decisions_csv(connection, tmp_path / "formula.csv")
        row = next(csv.DictReader(io.StringIO(exported.content.decode())))
        assert saved.human_reason == "=1+1" and row["human_reason"] == "'=1+1"
        assert list_decisions(connection) == [saved]


def test_export_failure_preserves_prior_export(database, tmp_path, monkeypatch):
    with closing(sqlite3.connect(database)) as connection:
        record_decision(connection, event())
        destination = tmp_path / "saved.csv"
        exported = export_decisions_csv(connection, destination)
        with pytest.raises(FileExistsError):
            export_decisions_csv(connection, destination)
        assert destination.read_bytes() == exported.content
        assert not list(tmp_path.glob(".decisions-*.tmp"))

        def fail_publish(*args):
            raise OSError("injected publish failure")

        monkeypatch.setattr(store.os, "link", fail_publish)
        with pytest.raises(OSError, match="injected publish failure"):
            export_decisions_csv(connection, tmp_path / "failed.csv")
        assert not (tmp_path / "failed.csv").exists()
        assert not list(tmp_path.glob(".decisions-*.tmp"))
        assert destination.read_bytes() == exported.content
        assert len(list_decisions(connection)) == 1


def test_export_write_failure_leaves_no_partial_file(database, tmp_path, monkeypatch):
    def fail_sync(*args):
        raise OSError("injected disk failure")

    monkeypatch.setattr(store.os, "fsync", fail_sync)
    with closing(sqlite3.connect(database)) as connection:
        with pytest.raises(OSError, match="injected disk failure"):
            export_decisions_csv(connection, tmp_path / "failed.csv")
    assert not (tmp_path / "failed.csv").exists()
    assert not list(tmp_path.glob(".decisions-*.tmp"))
