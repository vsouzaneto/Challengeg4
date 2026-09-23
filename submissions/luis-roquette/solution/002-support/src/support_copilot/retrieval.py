"""Train-only lexical precedents and an offline, fail-closed human review protocol.

prepare-review --artifacts artifacts --split calibration|test writes a canonical
review/retrieval-<split>-packet.json and a CSV template. Seed 42 samples 30 distinct
eligible queries proportionally by type, without replacement or score filtering.
Packets bind source/split/index/configuration hashes, query context, withheld
reference, signals, top-three sources and similarities (NOT calibrated confidence).
The reference is for the reviewer only and never enters the reference index.
Fewer than 30 eligible queries records insufficient_evidence, with actual counts;
it never duplicates queries or relaxes eligibility. Missing sources are explicit
abstentions, excluded from the draft denominator, not favorable observations.

The human CSV has query_id,source_id,relevance,correctness,safety,edit_effort,
reviewer_notes,packet_id,reviewer_id,reviewed_at. Keep IDs unchanged. A reviewer_id
is a stable pseudonym; reviewed_at is an ISO-8601 timestamp with timezone, no
earlier than packet creation and no later than now. Do not put personal details
in notes. Notes pass the shared sanitizer; arbitrary names may be quarantined.
One reviewer is allowed and is reported as such, not independent raters.
For relevance: 1 unrelated, 2 weak overlap, 3 partial, 4 mostly relevant, 5 direct.
For correctness: 1 wrong, 2 major errors, 3 mixed, 4 minor issues, 5 correct.
For safety: 1 harmful, 2 unsafe, 3 uncertain, 4 safe with caveats, 5 safe.
For edit_effort: 1 none, 2 light edits, 3 moderate, 4 substantial, 5 full rewrite.
All four integer ratings are required when a source exists. With no source all
four stay blank; reviewer/ timestamp/notes must still acknowledge the abstention.

lock-review --artifacts artifacts --rubric <calibration.csv> validates ALL 30
rows, authorship, timestamps, IDs and hashes. The smallest threshold in
0.20..0.90 step 0.10 with a nonempty accepted set, mean correctness/safety >=4,
and no safety <3 is locked. No eligible threshold records disabled. Missing or
incomplete ratings never become zeros or successes; drafts stay pending_review.
--decision disabled|pending_review explicitly freezes an unreviewed demonstration.
Only calibration can be prepared without final locks. Opening test requires both
domain model/routing locks and the retrieval decision lock. An opening marker is
written BEFORE exposing test queries: disabled/pending_review cannot later become
enabled for this version, even if its calibration rubric is completed afterwards.
lock-review --split test only records final quality and can disable assistance;
it never retunes the frozen threshold. Failure needs a new independently evaluated
version. evaluate_retriever itself is read-only. Absent/incomplete final review
does not establish CK-12 or authorize claims of final validation.

The CLI reads manifest-registered sanitized frames and ModelTrainingResult
artifacts under keys data.customer.train/calibration/test and models.customer/it.
Unsupported models have no binary: register their RoutingPolicy JSON under
policies.customer/it instead. Missing classifiers then yield zero eligible
queries because the OOD detector is unavailable; this never invents safe signals.
It checks paths/hashes before loading trusted local joblib files, never uploads.
Pipeline callers supply split_manifest to fit_retriever (or frame.attrs with that
key), derive TicketSignals centrally, and pass review packets via unseen.attrs
['review_packet'] or the explicit packet argument to evaluate_retriever. The
pipeline owns materializing the held-out frame AFTER verify_test_gate succeeds.
Hashes establish consistency, not authenticity against edits to all local files.
Immutable JSON publication requires local hard links; unsupported storage fails closed.
On missing/stale artifacts: run make reproduce. No paid API or free generation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import random
import re
import tempfile
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from support_copilot.data import atomic_json, canonical_text, content_hash, sanitize_text
from support_copilot.decision import RoutingPolicy, TicketSignals, derive_signals, policy_hash

THRESHOLDS = tuple(i / 10 for i in range(2, 10))
DIMENSIONS = ("relevance", "correctness", "safety", "edit_effort")
CSV_FIELDS = ("query_id", "source_id", *DIMENSIONS, "reviewer_notes", "packet_id",
              "reviewer_id", "reviewed_at")


@dataclass(frozen=True)
class SourceMatch:
    ticket_id: str
    similarity: float
    resolution: str
    text_group_id: str


@dataclass(frozen=True)
class RetrievalPolicy:
    drafts_enabled: bool = False
    threshold: float | None = None
    policy_version: str = "pending_review"
    packet_id: str | None = None
    calibration_rubric_sha256: str | None = None
    status: str = "pending_review"
    index_version: str | None = None


@dataclass(frozen=True)
class RetrievalResult:
    status: str
    sources: tuple[SourceMatch, ...]
    draft: str | None
    reason_codes: tuple[str, ...]
    index_version: str
    policy_version: str
    threshold: float | None


@dataclass(frozen=True)
class RetrievalMetrics:
    status: str
    population: int
    eligible: int
    sample: int
    reviewed: int
    complete: bool
    means: dict[str, float | None]
    unsafe_count: int
    accepted: int
    coverage: float | None
    reason_codes: tuple[str, ...]
    reviewers: tuple[str, ...] = ()


def _safe_text(text) -> bool:
    try:
        return (bool(text) and sanitize_text(text) == text
                and bool(re.search(r"\b\w\w+\b", re.sub(r"\[[A-Z]+\]", "", text))))
    except (ValueError, TypeError):
        return False


def _signal_reasons(signals: TicketSignals) -> tuple[str, ...]:
    reasons = list(signals.validation_reasons)
    for blocked, reason in (
        (signals.domain != "customer", "domain_mismatch"),
        (not signals.input_valid, "invalid_input"),
        (not signals.privacy_passed, "privacy_failed"),
        (not signals.artifact_valid, "artifact_invalid"),
        (signals.zero_vector is not False, "ood_check_failed"),
        (signals.ambiguous, "ambiguous_input"),
        (signals.priority not in {"Low", "Medium", "High", "Critical"}, "unknown_priority"),
        (signals.priority == "Critical", "critical_priority"),
    ):
        if blocked:
            reasons.append(reason)
    reasons.extend(signals.sensitive_matches)
    return tuple(dict.fromkeys(reasons))


@dataclass
class TicketRetriever:
    records: tuple[dict, ...]
    vectorizer: TfidfVectorizer | None
    matrix: object
    index_version: str
    provenance: dict
    partitions: dict

    def suggest(self, text: str, policy: RetrievalPolicy, *,
                signals: TicketSignals) -> RetrievalResult:
        reasons = _signal_reasons(signals)
        sources = ()
        if (not signals.input_valid or not signals.privacy_passed
                or not signals.artifact_valid or signals.domain != "customer"
                or signals.validation_reasons or not _safe_text(text)):
            reasons = reasons or ("invalid_or_private_input",)
        elif self.vectorizer is None:
            reasons = (*reasons, "no_safe_sources")
        else:
            vector = self.vectorizer.transform([text])
            scores = (self.matrix @ vector.T).toarray().ravel()
            matches = [SourceMatch(row["ticket_id"], min(1.0, max(0.0, float(score))),
                                   row["resolution"], row["text_group_id"])
                       for row, score in zip(self.records, scores, strict=True)
                       if math.isfinite(score) and score > 0
                       and row["ticket_id"] != signals.ticket_id]
            sources = tuple(sorted(matches, key=lambda match: (-match.similarity,
                                                               match.ticket_id))[:3])
            if not sources:
                reasons = (*reasons, "no_similar_source")
        if not reasons:
            if (not policy.drafts_enabled or policy.status != "enabled"
                    or policy.threshold not in THRESHOLDS or not policy.packet_id
                    or not policy.calibration_rubric_sha256
                    or policy.index_version != self.index_version):
                reasons = ("retrieval_policy_not_validated",)
            elif sources[0].similarity < policy.threshold:
                reasons = ("below_retrieval_threshold",)
        draft = None if reasons else sources[0].resolution
        status = "draft" if draft else "unavailable" if self.vectorizer is None else "abstain"
        return RetrievalResult(status, sources, draft, reasons or ("validated_precedent",),
                               self.index_version, policy.policy_version, policy.threshold)


def _partitions(manifest: dict) -> dict:
    payload = {key: value for key, value in manifest.items() if key != "split_version"}
    if manifest.get("split_version") != content_hash(payload):
        raise ValueError("split_hash_mismatch")
    parts = {key: manifest["partitions"][key] for key in ("train", "calibration", "test")}
    for key, part in parts.items():
        if len(part["ids"]) != len(part["groups"]) or any(
            len(part[field]) != len(set(part[field])) for field in ("ids", "groups")
        ):
            raise ValueError("duplicate_split_membership")
        for other in parts:
            if other != key and any(set(part[field]) & set(parts[other][field])
                                    for field in ("ids", "groups")):
                raise ValueError("split_leakage")
    return parts


def _validate_rows(frame: pd.DataFrame, part: dict) -> None:
    required = {"ticket_id", "domain", "text", "text_group_id", "resolution", "target",
                "Ticket Status", "Ticket Priority"}
    if not required <= set(frame.columns) or frame.ticket_id.duplicated().any():
        raise ValueError("retrieval_frame_schema_or_duplicate_id")
    membership = dict(zip(part["ids"], part["groups"], strict=True))
    for row in frame.to_dict("records"):
        expected = "customer:group:" + content_hash(canonical_text(row["text"]))
        if (row["domain"] != "customer" or membership.get(row["ticket_id"]) != expected
                or row["text_group_id"] != expected):
            raise ValueError("retrieval_partition_or_group_mismatch")


def fit_retriever(train_closed: pd.DataFrame, *, split_manifest: dict | None = None,
                  source_sha256: str | None = None,
                  configuration_sha256: str | None = None) -> TicketRetriever:
    manifest = split_manifest or train_closed.attrs.get("split_manifest")
    if manifest is None:
        raise ValueError("retrieval_requires_split_manifest")
    parts = _partitions(manifest)
    _validate_rows(train_closed, parts["train"])
    records = tuple({key: row[key] for key in ("ticket_id", "text", "resolution", "text_group_id")}
                    for row in train_closed.sort_values("ticket_id").to_dict("records")
                    if row["Ticket Status"] == "Closed" and _safe_text(row["text"])
                    and _safe_text(row["resolution"]))
    provenance = {
        "source_sha256": source_sha256 or train_closed.attrs.get("source", {}).get("sha256"),
        "split_sha256": manifest["split_version"],
        "configuration_sha256": configuration_sha256,
        "reference_sha256": content_hash(records), "protocol_version": 1,
    }
    if not all(isinstance(provenance[key], str) and re.fullmatch(r"[0-9a-f]{64}",
               provenance[key]) for key in ("source_sha256", "configuration_sha256")):
        raise ValueError("retrieval_requires_source_and_configuration_hashes")
    vectorizer = TfidfVectorizer() if records else None
    matrix = vectorizer.fit_transform([row["text"] for row in records]) if records else None
    return TicketRetriever(records, vectorizer, matrix, content_hash(provenance), provenance, parts)


def _sealed(value: dict) -> dict:
    return {**value, "sha256": content_hash(value)}


def _read_sealed(path: Path) -> dict:
    try:
        value = json.loads(path.read_text())
        if value.pop("sha256") != content_hash(value):
            raise ValueError("review_hash_mismatch")
        return value
    except (OSError, KeyError, TypeError, json.JSONDecodeError):
        raise ValueError("review_artifact_missing_or_invalid:make reproduce") from None


def _freeze_json(value: dict, path: Path) -> None:
    """Publish complete bytes exclusively: concurrent calls cannot replace a lock."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=path.parent) as directory:
        temporary = Path(directory) / "sealed.json"
        atomic_json(_sealed(value), temporary)
        try:
            os.link(temporary, path)
        except FileExistsError:
            if content_hash(_read_sealed(path)) != content_hash(value):
                raise ValueError("review_artifact_already_frozen") from None


def _paths(artifacts: Path, split: str) -> tuple[Path, Path]:
    if split not in {"calibration", "test"}:
        raise ValueError("invalid_review_split")
    root = artifacts / "review"
    return root / f"retrieval-{split}-packet.json", root / f"retrieval-{split}-template.csv"


def _lock_path(artifacts: Path) -> Path:
    return artifacts / "review/retrieval-policy-lock.json"


def _opening_path(artifacts: Path) -> Path:
    return artifacts / "review/retrieval-test-opened.json"


def _check_provenance(value: dict, retriever: TicketRetriever) -> None:
    if (value.get("provenance") != retriever.provenance
            or value.get("index_version") != retriever.index_version):
        raise ValueError("review_provenance_mismatch:make reproduce")


def _locked_policy(lock: dict, retriever: TicketRetriever) -> RetrievalPolicy:
    _check_provenance(lock, retriever)
    policy = RetrievalPolicy(**lock["policy"])
    if (policy.policy_version != content_hash(asdict(replace(policy, policy_version="")))
            or policy.index_version != retriever.index_version
            or policy.status not in {"enabled", "disabled", "pending_review",
                                     "insufficient_evidence"}
            or policy.drafts_enabled != (policy.status == "enabled")
            or not policy.packet_id
            or (policy.drafts_enabled and (policy.threshold not in THRESHOLDS
                                           or not policy.calibration_rubric_sha256))
            or (not policy.drafts_enabled and policy.threshold is not None)):
        raise ValueError("retrieval_policy_version_or_state_mismatch")
    return policy


def verify_test_gate(retriever: TicketRetriever, artifacts: Path, model_locks: dict) -> dict:
    """Call BEFORE loading final test payload; unavailable models need disabled locks too."""
    lock = _read_sealed(_lock_path(artifacts))
    _locked_policy(lock, retriever)
    if set(model_locks) != {"customer", "it"}:
        raise ValueError("both_domain_locks_required")
    for domain, policy in model_locks.items():
        if (policy.domain != domain or not policy.locked
                or policy.configuration_sha256 != policy_hash(policy)):
            raise ValueError("model_or_routing_not_locked")
    state = {"index_version": retriever.index_version, "provenance": retriever.provenance,
             "retrieval_lock_sha256": content_hash(lock),
             "model_locks": {domain: policy.configuration_sha256
                             for domain, policy in sorted(model_locks.items())}}
    marker = _opening_path(artifacts)
    if marker.exists():
        if _read_sealed(marker) != state:
            raise ValueError("test_opened_configuration_changed")
    else:
        _freeze_json(state, marker)
    return lock


def prepare_review(retriever: TicketRetriever, unseen: pd.DataFrame,
                   signals: dict[str, TicketSignals], *, artifacts: Path,
                   split: str = "calibration", model_locks: dict | None = None,
                   created_at: str | None = None) -> dict:
    # Pipeline supplies the frozen evaluation-start timestamp from configuration.json.
    # It is a real configuration input, not an ignored or fabricated wall-clock receipt.
    if created_at is not None:
        stamp = datetime.fromisoformat(created_at)
        if stamp.tzinfo is None or stamp > datetime.now(UTC):
            raise ValueError("review_invalid_creation_timestamp")
    packet_path, template_path = _paths(artifacts, split)
    test_gate = None
    if split == "test":
        lock = verify_test_gate(retriever, artifacts, model_locks or {})
        test_gate = {**_read_sealed(_opening_path(artifacts)), "policy": lock["policy"]}
    _validate_rows(unseen, retriever.partitions[split])
    if set(unseen.ticket_id) != set(retriever.partitions[split]["ids"]):
        raise ValueError("review_requires_entire_partition")
    eligible = []
    for row in unseen.sort_values("ticket_id").to_dict("records"):
        signal = signals.get(row["ticket_id"])
        if signal is None or signal.ticket_id != row["ticket_id"]:
            raise ValueError("query_signals_missing_or_mismatched")
        if (not _signal_reasons(signal) and _safe_text(row["text"])
                and _safe_text(row["resolution"])):
            eligible.append(row)
    # Largest-remainder proportional allocation; deterministic ties and sampling.
    strata = {}
    rng = random.Random(42)
    for row in eligible:
        strata.setdefault(row["target"], []).append(row)
    size = min(30, len(eligible))
    quotas = {key: size * len(rows) // max(1, len(eligible)) for key, rows in strata.items()}
    order = sorted(strata, key=lambda key: (-(size * len(strata[key]) % len(eligible)), key))
    for key in order[:size - sum(quotas.values())]:
        quotas[key] += 1
    chosen = []
    for key in sorted(strata):
        rng.shuffle(strata[key])
        chosen.extend(strata[key][:quotas[key]])
    queries = []
    for row in sorted(chosen, key=lambda row: row["ticket_id"]):
        signal = signals[row["ticket_id"]]
        result = retriever.suggest(row["text"], RetrievalPolicy(), signals=signal)
        queries.append({"query_id": row["ticket_id"], "text": row["text"],
                        "reference": row["resolution"], "target": row["target"],
                        "text_group_id": row["text_group_id"], "signals": asdict(signal),
                        "sources": [asdict(source) for source in result.sources],
                        "eligibility": "eligible", "abstention": None if result.sources
                        else "no_similar_source"})
    packet = {"schema_version": 1, "split": split, "seed": 42,
              "provenance": retriever.provenance, "index_version": retriever.index_version,
              "population": len(unseen), "eligible": len(eligible), "queries": queries,
              "test_gate": test_gate,
              "status": "pending_review" if len(eligible) >= 30 else "insufficient_evidence"}
    packet["packet_id"] = content_hash(packet)
    if packet_path.exists():
        old = _read_sealed(packet_path)
        if (old.get("packet_id") != packet["packet_id"]
                or created_at is not None and old.get("created_at") != created_at):
            raise ValueError("review_packet_already_frozen")
        return old
    packet["created_at"] = created_at or datetime.now(UTC).isoformat()
    _freeze_json(packet, packet_path)
    # Exclusive creation preserves human edits; a missing template is recoverable manually.
    with template_path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        for query in queries:
            writer.writerow({"query_id": query["query_id"], "packet_id": packet["packet_id"],
                             "source_id": query["sources"][0]["ticket_id"]
                             if query["sources"] else ""})
    return packet


def _validate_packet(retriever: TicketRetriever, unseen: pd.DataFrame, packet: dict) -> None:
    _check_provenance(packet, retriever)
    payload = {key: value for key, value in packet.items()
               if key not in {"packet_id", "created_at"}}
    if content_hash(payload) != packet.get("packet_id"):
        raise ValueError("packet_id_mismatch")
    _validate_rows(unseen, retriever.partitions[packet["split"]])
    if set(unseen.ticket_id) != set(retriever.partitions[packet["split"]]["ids"]):
        raise ValueError("review_requires_entire_partition")
    by_id = unseen.set_index("ticket_id").to_dict("index")
    query_ids = [query["query_id"] for query in packet["queries"]]
    if len(set(query_ids)) != len(query_ids):
        raise ValueError("duplicate_packet_queries")
    for query in packet["queries"]:
        row = by_id.get(query["query_id"])
        if row is None or any(query[key] != row[field] for key, field in (
            ("text", "text"), ("reference", "resolution"), ("target", "target"),
            ("text_group_id", "text_group_id"),
        )):
            raise ValueError("packet_query_mismatch")
        signal = TicketSignals(**query["signals"])
        if (signal.ticket_id != query["query_id"] or _signal_reasons(signal)
                or not _safe_text(query["reference"])):
            raise ValueError("packet_ineligible_query")
        result = retriever.suggest(query["text"], RetrievalPolicy(), signals=signal)
        if [asdict(source) for source in result.sources] != query["sources"]:
            raise ValueError("packet_sources_mismatch")


def _ratings(packet: dict, rubric_path: Path) -> tuple[list[dict], str]:
    payload = rubric_path.read_bytes()
    reader = csv.DictReader(io.StringIO(payload.decode("utf-8")))
    rows = list(reader)
    if (reader.fieldnames != list(CSV_FIELDS)
            or any(set(row) != set(CSV_FIELDS) or None in row.values() for row in rows)):
        raise ValueError("rubric_schema_mismatch")
    expected = {query["query_id"]: query for query in packet["queries"]}
    if len(rows) != len(expected) or {row["query_id"] for row in rows} != set(expected):
        raise ValueError("rubric_incomplete_or_duplicate")
    if packet["status"] == "insufficient_evidence" or len(rows) != 30:
        raise ValueError("insufficient_evidence:30_distinct_eligible_queries_required")
    created = datetime.fromisoformat(packet["created_at"])
    rated = []
    for row in rows:
        query = expected[row["query_id"]]
        source = query["sources"][0] if query["sources"] else None
        if (row["packet_id"] != packet["packet_id"]
                or row["source_id"] != (source["ticket_id"] if source else "")):
            raise ValueError("rubric_packet_or_source_mismatch")
        if not re.fullmatch(r"[a-z0-9_-]{1,64}", row["reviewer_id"]):
            raise ValueError("rubric_reviewer_required:use_stable_lowercase_pseudonym")
        try:
            stamp = datetime.fromisoformat(row["reviewed_at"])
            if stamp.tzinfo is None or not created <= stamp <= datetime.now(UTC):
                raise ValueError
        except (ValueError, TypeError):
            raise ValueError("rubric_invalid_timestamp") from None
        notes = sanitize_text(row["reviewer_notes"])
        if notes != row["reviewer_notes"]:
            raise ValueError("rubric_notes_require_sanitization")
        if source is None:
            if any(row[key] for key in DIMENSIONS) or not notes:
                raise ValueError("rubric_missing_source_requires_unrated_acknowledgment")
            values = {}
        else:
            if any(row[key] not in {"1", "2", "3", "4", "5"} for key in DIMENSIONS):
                raise ValueError("rubric_incomplete_or_invalid_rating")
            values = {key: int(row[key]) for key in DIMENSIONS}
        rated.append({**values, "similarity": source["similarity"] if source else None,
                      "reviewer_id": row["reviewer_id"], "reviewer_notes": notes})
    return rated, hashlib.sha256(payload).hexdigest()


def _acceptable(rows: list[dict]) -> bool:
    return bool(rows) and all(sum(row[key] for row in rows) / len(rows) >= 4
                              for key in ("correctness", "safety")) and all(
        row["safety"] >= 3 for row in rows)


def evaluate_retriever(retriever: TicketRetriever, unseen: pd.DataFrame, rubric_path: Path,
                       *, packet: dict | None = None,
                       policy: RetrievalPolicy | None = None) -> RetrievalMetrics:
    packet = packet or unseen.attrs.get("review_packet")
    if packet is None:
        raise ValueError("review_packet_required")
    _validate_packet(retriever, unseen, packet)
    rows, _ = _ratings(packet, rubric_path)
    if packet["split"] == "test":
        gate = packet.get("test_gate")
        if (policy is None or not gate or asdict(policy) != gate["policy"]
                or set(gate["model_locks"]) != {"customer", "it"}
                or gate["index_version"] != retriever.index_version
                or gate["retrieval_lock_sha256"] != content_hash({
                    "policy": asdict(policy), "index_version": retriever.index_version,
                    "provenance": retriever.provenance})):
            raise ValueError("test_requires_frozen_retrieval_policy")
    threshold = policy.threshold if policy and policy.drafts_enabled else None
    candidates = [row for row in rows if row["similarity"] is not None]
    accepted = [row for row in candidates if threshold is not None
                and row["similarity"] >= threshold]
    return RetrievalMetrics(
        "reviewed", packet["population"], packet["eligible"], len(rows), len(rows), True,
        {key: sum(row[key] for row in candidates) / len(candidates) if candidates else None
         for key in DIMENSIONS}, sum(row["safety"] < 3 for row in candidates), len(accepted),
        len(accepted) / len(rows), () if candidates else ("no_candidate_denominator",),
        tuple(sorted({row["reviewer_id"] for row in rows})),
    )


def lock_review(retriever: TicketRetriever, unseen: pd.DataFrame, *, artifacts: Path,
                rubric_path: Path | None = None, decision: str | None = None) -> RetrievalPolicy:
    if _opening_path(artifacts).exists():
        raise ValueError("test_already_opened:no_calibration_changes")
    packet = _read_sealed(_paths(artifacts, "calibration")[0])
    _validate_packet(retriever, unseen, packet)
    threshold, rubric_hash = None, None
    if decision is not None and (decision not in {"disabled", "pending_review"}
                                 or rubric_path is not None):
        raise ValueError("invalid_explicit_review_decision")
    if packet["status"] == "insufficient_evidence":
        status = "insufficient_evidence"
    elif decision is not None:
        status = decision
    elif rubric_path is None:
        raise ValueError("calibration_rubric_required")
    else:
        rows, rubric_hash = _ratings(packet, rubric_path)
        threshold = next((value for value in THRESHOLDS if _acceptable([
            row for row in rows if row["similarity"] is not None and row["similarity"] >= value
        ])), None)
        status = "enabled" if threshold is not None else "disabled"
    policy = RetrievalPolicy(status == "enabled", threshold, "", packet["packet_id"],
                             rubric_hash, status, retriever.index_version)
    policy = replace(policy, policy_version=content_hash(asdict(policy)))
    lock = {"policy": asdict(policy), "index_version": retriever.index_version,
            "provenance": retriever.provenance}
    path = _lock_path(artifacts)
    if path.exists() and _read_sealed(path) != lock:
        raise ValueError("retrieval_policy_already_locked")
    _freeze_json(lock, path)
    return policy


def load_retrieval_policy(retriever: TicketRetriever, artifacts: Path) -> RetrievalPolicy:
    lock = _read_sealed(_lock_path(artifacts))
    policy = _locked_policy(lock, retriever)
    final_path = artifacts / "review/retrieval-test-result.json"
    if _opening_path(artifacts).exists():
        opening = _read_sealed(_opening_path(artifacts))
        if opening["retrieval_lock_sha256"] != content_hash(lock):
            raise ValueError("test_opened_configuration_changed")
    if final_path.exists():
        final = _read_sealed(final_path)
        if final["retrieval_lock_sha256"] != content_hash(lock):
            raise ValueError("final_review_lock_mismatch")
        if not final["passed"]:
            policy = replace(policy, drafts_enabled=False, status="disabled")
    return policy


def finalize_review(retriever: TicketRetriever, unseen: pd.DataFrame, rubric_path: Path,
                    *, artifacts: Path, model_locks: dict) -> RetrievalMetrics:
    lock = verify_test_gate(retriever, artifacts, model_locks)
    packet = _read_sealed(_paths(artifacts, "test")[0])
    policy = RetrievalPolicy(**lock["policy"])
    metrics = evaluate_retriever(retriever, unseen, rubric_path, packet=packet, policy=policy)
    rows, rubric_hash = _ratings(packet, rubric_path)
    accepted = [row for row in rows if row["similarity"] is not None
                and policy.threshold is not None and row["similarity"] >= policy.threshold]
    result = {"metrics": asdict(metrics), "rubric_sha256": rubric_hash,
              "packet_id": packet["packet_id"], "retrieval_lock_sha256": content_hash(lock),
              "passed": policy.drafts_enabled and _acceptable(accepted)}
    path = artifacts / "review/retrieval-test-result.json"
    if path.exists() and content_hash(_read_sealed(path)) != content_hash(result):
        raise ValueError("final_review_already_locked")
    _freeze_json(result, path)
    return metrics


def _artifact(root: Path, manifest: dict, key: str):
    """Only the trusted local pipeline can supply manifest-registered binary artifacts."""
    from support_copilot.ui import read_artifact

    return read_artifact(root, manifest, key)


def _model_state(root: Path, manifest: dict, domain: str):
    if manifest["artifacts"].get(f"models.{domain}", {}).get("status") == "ready":
        result = _artifact(root, manifest, f"models.{domain}")
        if (result.policy.domain != domain
                or result.configuration_sha256 != result.policy.configuration_sha256
                or result.policy.configuration_sha256 != policy_hash(result.policy)
                or (result.model is not None
                    and result.model.model_version != result.policy.model_version)):
            raise ValueError("model_policy_mismatch")
        return result.model, result.policy, result.reason_codes
    policy = RoutingPolicy(**_artifact(root, manifest, f"policies.{domain}"))
    if (policy.domain != domain or policy.model_version is not None
            or policy.configuration_sha256 != policy_hash(policy)
            or policy.automation_enabled):
        raise ValueError("missing_model_has_enabled_policy")
    return None, policy, (policy.disabled_reason or "model_unavailable",)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("prepare-review", "lock-review"))
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--split", choices=("calibration", "test"), default="calibration")
    parser.add_argument("--rubric", type=Path)
    parser.add_argument("--decision", choices=("disabled", "pending_review"))
    args = parser.parse_args(argv)
    try:
        root = args.artifacts
        manifest = json.loads((root / "manifest.json").read_text())
        train = pd.DataFrame(_artifact(root, manifest, "data.customer.train"))
        retriever = fit_retriever(train, split_manifest=manifest["splits"]["customer"],
                                  source_sha256=manifest["sources"]["customer"]["sha256"],
                                  configuration_sha256=manifest["configuration_sha256"])
        models = {}
        if args.split == "test" or args.command == "prepare-review":
            domains = ("customer", "it") if args.split == "test" else ("customer",)
            models = {domain: _model_state(root, manifest, domain) for domain in domains}
        locks = {domain: result[1] for domain, result in models.items()}
        if args.split == "test":
            verify_test_gate(retriever, root, locks)
        unseen = pd.DataFrame(_artifact(root, manifest, f"data.customer.{args.split}"))
        if args.command == "prepare-review":
            model, policy, reasons = models["customer"]
            from support_copilot.modeling import Prediction

            signals = {}
            for row in unseen.to_dict("records"):
                prediction = model.predict_one(row["text"]) if model else Prediction(
                    "customer", "unsupported", reason_codes=reasons)
                signals[row["ticket_id"]] = derive_signals(
                    row["text"], domain="customer", ticket_id=row["ticket_id"],
                    priority=row["Ticket Priority"], prediction=prediction, policy=policy,
                    artifact_valid=True, privacy_passed=_safe_text(row["text"]),
                )
            packet = prepare_review(retriever, unseen, signals, artifacts=root, split=args.split,
                                    model_locks=locks)
            print(json.dumps({key: packet[key] for key in ("status", "packet_id", "eligible")}))
        elif args.split == "calibration":
            policy = lock_review(retriever, unseen, artifacts=root, rubric_path=args.rubric,
                                 decision=args.decision)
            print(json.dumps(asdict(policy)))
        else:
            if args.rubric is None or args.decision is not None:
                raise ValueError("test_requires_rubric_and_forbids_retuning")
            metrics = finalize_review(retriever, unseen, args.rubric, artifacts=root,
                                      model_locks=locks)
            print(json.dumps(asdict(metrics)))
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as error:
        # Avoid printing untrusted artifact contents or private file paths.
        reason = str(error)
        prefixes = ("retrieval_", "review_", "rubric_", "packet_", "test_", "model_",
                    "both_domain_", "calibration_", "final_review_", "insufficient_evidence",
                    "artifact_", "privacy_quarantine", "missing_model_", "query_signals_",
                    "split_", "duplicate_split_", "invalid_review_")
        if not reason.startswith(prefixes) or not re.fullmatch(r"[a-z0-9_: -]+", reason):
            reason = type(error).__name__
        print(f"review_failed:{reason}:check artifacts and run make reproduce")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
