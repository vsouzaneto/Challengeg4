"""Synthetic protocol regressions; these ratings are NOT human evidence."""

import csv
import hashlib
import importlib.metadata
import json
import platform
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, replace
from datetime import UTC, datetime
from types import SimpleNamespace

import joblib
import pandas as pd
import pytest

from support_copilot.data import CUSTOMER_TAXONOMY, canonical_text, content_hash
from support_copilot.decision import TicketSignals, base_policy, lock_policy
from support_copilot.modeling import Prediction
from support_copilot.retrieval import (
    CSV_FIELDS,
    RetrievalPolicy,
    _freeze_json,
    _read_sealed,
    evaluate_retriever,
    finalize_review,
    fit_retriever,
    load_retrieval_policy,
    lock_review,
    main,
    prepare_review,
    verify_test_gate,
)


def signal(ticket_id="customer:query", **changes):
    return replace(TicketSignals("customer", ticket_id, True, True, True, "Low", False,
                                 False, (), ()), **changes)


@pytest.fixture
def dataset():
    def row(ticket_id, text, target="Technical issue", **changes):
        return {"ticket_id": ticket_id, "domain": "customer", "text": text,
                "text_group_id": "customer:group:" + content_hash(canonical_text(text)),
                "resolution": "reset the device", "target": target, "Ticket Status": "Closed",
                "Ticket Priority": "Low", **changes}

    parts = {"train": pd.DataFrame([
        row("customer:1", "device screen failed reset"),
        row("customer:2", "screen device failed reset"),
        row("customer:3", "failed screen device reset"),
        row("customer:4", "reset screen device failed"),
    ])}
    for offset, part in ((100, "calibration"), (200, "test")):
        parts[part] = pd.DataFrame([
            row(f"customer:{offset + n}", "device screen failed reset " +
                chr(97 + n // 26) + chr(97 + n % 26) + part,
                "Technical issue" if n % 2 else "Product inquiry") for n in range(60)
        ])
    manifest = {"partitions": {
        key: {"ids": list(frame.ticket_id), "groups": list(frame.text_group_id)}
        for key, frame in parts.items()
    }}
    manifest["split_version"] = content_hash(manifest)
    parts["manifest"] = manifest
    return parts


def fit(data, train=None):
    return fit_retriever(data["train"] if train is None else train,
                         split_manifest=data["manifest"], source_sha256="a" * 64,
                         configuration_sha256="b" * 64)


def packet(data, retriever, tmp_path, split="calibration", **kwargs):
    frame = data[split]
    return prepare_review(retriever, frame, {key: signal(key) for key in frame.ticket_id},
                          artifacts=tmp_path, split=split, **kwargs)


def rate(tmp_path, split="calibration", **changes):
    path = tmp_path / f"review/retrieval-{split}-template.csv"
    with path.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        row.update(reviewer_id="fixture_reviewer", reviewed_at=datetime.now(UTC).isoformat(),
                   reviewer_notes="fixture only")
        if row["source_id"]:
            row.update(relevance="5", correctness="5", safety="5", edit_effort="1")
        row.update(changes)
    write_ratings(path, rows)
    return path


def write_ratings(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def locks():
    return {domain: lock_policy(base_policy(domain)) for domain in ("customer", "it")}


def enabled(retriever):
    return RetrievalPolicy(True, 0.2, "fixture", "fixture", "c" * 64, "enabled",
                           retriever.index_version)


def test_train_only_and_sanitized_sources(dataset):
    train = dataset["train"].copy()
    train.loc[0, "resolution"] = ""
    train.loc[1, "Ticket Status"] = "Open"
    train.loc[2, "resolution"] = "contact private@example.test"
    retriever = fit(dataset, train)
    assert [row["ticket_id"] for row in retriever.records] == ["customer:4"]
    assert set(retriever.vectorizer.vocabulary_) == {"reset", "screen", "device", "failed"}
    with pytest.raises(ValueError, match="partition"):
        fit(dataset, pd.concat([train, dataset["test"].iloc[:1]]))
    with pytest.raises(ValueError, match="split_manifest"):
        fit_retriever(train)


def test_forged_group_overlap_and_provenance_rejected(dataset):
    bad = dataset["train"].copy()
    bad.loc[0, "text"] = dataset["test"].iloc[0].text
    with pytest.raises(ValueError, match="partition"):
        fit(dataset, bad)
    dataset["manifest"]["partitions"]["test"]["groups"][0] = (
        dataset["manifest"]["partitions"]["train"]["groups"][0])
    with pytest.raises(ValueError, match="hash"):
        fit(dataset)
    manifest = dataset["manifest"]
    manifest.pop("split_version")
    manifest["split_version"] = content_hash(manifest)
    with pytest.raises(ValueError, match="leakage"):
        fit(dataset)


def test_top_three_ties_draft_is_exact_historical_resolution(dataset):
    retriever = fit(dataset)
    result = retriever.suggest("device screen failed reset", enabled(retriever), signals=signal())
    assert result.status == "draft" and result.draft == "reset the device"
    assert [source.ticket_id for source in result.sources] == ["customer:1", "customer:2",
                                                             "customer:3"]
    assert all(source.similarity == pytest.approx(1) for source in result.sources)
    assert fit(dataset, dataset["train"].iloc[::-1]).index_version == retriever.index_version


@pytest.mark.parametrize("changes,no_sources", [
    ({"priority": "Critical"}, False),
    ({"sensitive_matches": ("category:Billing inquiry",)}, False),
    ({"ambiguous": True}, False), ({"zero_vector": True}, False),
    ({"zero_vector": None}, False), ({"input_valid": False}, True),
    ({"privacy_passed": False}, True), ({"artifact_valid": False}, True),
    ({"domain": "it"}, True), ({"priority": None}, False),
    ({"validation_reasons": ("risk_detector_unavailable",)}, True),
])
def test_every_risk_blocks_perfect_match(dataset, changes, no_sources):
    retriever = fit(dataset)
    result = retriever.suggest("device screen failed reset", enabled(retriever),
                               signals=signal(**changes))
    assert result.draft is None and result.status == "abstain" and result.reason_codes
    assert bool(result.sources) is not no_sources


@pytest.mark.parametrize("text", ["", " ", "device private@example.test", "John Doe failed"])
def test_private_or_invalid_text_cannot_query_even_with_forged_signals(dataset, text):
    retriever = fit(dataset)
    result = retriever.suggest(text, enabled(retriever), signals=signal())
    assert result.draft is None and not result.sources


def test_empty_index_zero_vector_pending_and_wrong_policy(dataset):
    retriever = fit(dataset)
    for text, policy in (("unknown unrelated", enabled(retriever)),
                         ("device screen failed reset", RetrievalPolicy()),
                         ("device screen failed reset", replace(enabled(retriever),
                                                                index_version="stale"))):
        assert retriever.suggest(text, policy, signals=signal()).draft is None
    train = dataset["train"].copy()
    train["resolution"] = None
    empty = fit(dataset, train)
    result = empty.suggest("device screen failed reset", enabled(empty), signals=signal())
    assert result.status == "unavailable" and not result.sources


def test_seeded_stratified_and_score_independent_packets(dataset, tmp_path):
    retriever = fit(dataset)
    first = packet(dataset, retriever, tmp_path / "first")
    second = packet(dataset, retriever, tmp_path / "second")
    assert first["packet_id"] == second["packet_id"]
    assert len(first["queries"]) == 30 and first["eligible"] == 60
    assert sum(query["target"] == "Technical issue" for query in first["queries"]) == 15
    train = dataset["train"].copy()
    train["resolution"] = None
    empty = packet(dataset, fit(dataset, train), tmp_path / "empty")
    assert [q["query_id"] for q in first["queries"]] == [q["query_id"] for q in empty["queries"]]
    assert all(query["abstention"] == "no_similar_source" for query in empty["queries"])
    assert packet(dataset, retriever, tmp_path / "first") == json.loads(json.dumps(first))


def test_less_than_thirty_never_duplicates_or_claims_evidence(dataset, tmp_path):
    retriever = fit(dataset)
    frame = dataset["calibration"]
    signals = {key: signal(key, ambiguous=i >= 29) for i, key in enumerate(frame.ticket_id)}
    review = prepare_review(retriever, frame, signals, artifacts=tmp_path)
    assert review["status"] == "insufficient_evidence" and review["eligible"] == 29
    assert len({q["query_id"] for q in review["queries"]}) == 29
    policy = lock_review(retriever, frame, artifacts=tmp_path)
    assert policy.status == "insufficient_evidence" and not policy.drafts_enabled
    with pytest.raises(ValueError, match="insufficient_evidence"):
        evaluate_retriever(retriever, frame, rate(tmp_path), packet=review)


@pytest.mark.parametrize("changes,reason", [
    ({"safety": ""}, "rating"), ({"safety": "6"}, "rating"),
    ({"correctness": "nan"}, "rating"), ({"reviewer_id": ""}, "reviewer"),
    ({"reviewed_at": ""}, "timestamp"), ({"reviewed_at": "2000-01-01T00:00:00Z"}, "timestamp"),
    ({"reviewed_at": "2099-01-01T00:00:00Z"}, "timestamp"),
    ({"packet_id": "different"}, "packet"), ({"source_id": "different"}, "source"),
    ({"reviewer_notes": "email private@example.test"}, "sanitization"),
])
def test_invalid_rubric_fails_closed(dataset, tmp_path, changes, reason):
    retriever = fit(dataset)
    packet(dataset, retriever, tmp_path)
    with pytest.raises(ValueError, match=reason):
        lock_review(retriever, dataset["calibration"], artifacts=tmp_path,
                    rubric_path=rate(tmp_path, **changes))
    assert not (tmp_path / "review/retrieval-policy-lock.json").exists()


def test_missing_duplicate_and_tampered_packets(dataset, tmp_path):
    retriever = fit(dataset)
    review = packet(dataset, retriever, tmp_path)
    rubric = rate(tmp_path)
    rows = list(csv.DictReader(io_read(rubric)))
    write_ratings(rubric, rows[:-1])
    with pytest.raises(ValueError, match="incomplete"):
        evaluate_retriever(retriever, dataset["calibration"], rubric, packet=review)
    rows[1] = rows[0]
    write_ratings(rubric, rows)
    with pytest.raises(ValueError, match="duplicate"):
        evaluate_retriever(retriever, dataset["calibration"], rubric, packet=review)
    path = tmp_path / "review/retrieval-calibration-packet.json"
    raw = json.loads(path.read_text())
    raw["queries"][0]["sources"][0]["resolution"] = "invented resolution"
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="hash"):
        lock_review(retriever, dataset["calibration"], artifacts=tmp_path, rubric_path=rubric)


def io_read(path):
    return path.read_text().splitlines()


def test_lock_selects_smallest_valid_threshold_and_is_immutable(dataset, tmp_path):
    retriever = fit(dataset)
    review = packet(dataset, retriever, tmp_path)
    rubric = rate(tmp_path)
    policy = lock_review(retriever, dataset["calibration"], artifacts=tmp_path, rubric_path=rubric)
    assert policy.threshold == 0.2 and policy.drafts_enabled
    assert load_retrieval_policy(retriever, tmp_path) == policy
    metrics = evaluate_retriever(retriever, dataset["calibration"], rubric, packet=review,
                                 policy=policy)
    assert metrics.complete and metrics.reviewed == 30 and metrics.accepted == 30
    assert metrics.coverage == 1 and metrics.reviewers == ("fixture_reviewer",)
    assert lock_review(retriever, dataset["calibration"], artifacts=tmp_path,
                       rubric_path=rubric) == policy
    with pytest.raises(ValueError, match="already_locked"):
        lock_review(retriever, dataset["calibration"], artifacts=tmp_path,
                    rubric_path=rate(tmp_path, safety="2"))


@pytest.mark.parametrize("changes", [{"safety": "2"}, {"correctness": "3"}, {"safety": "3"}])
def test_poor_review_disables_without_relaxing_threshold(dataset, tmp_path, changes):
    retriever = fit(dataset)
    packet(dataset, retriever, tmp_path)
    policy = lock_review(retriever, dataset["calibration"], artifacts=tmp_path,
                         rubric_path=rate(tmp_path, **changes))
    assert not policy.drafts_enabled and policy.status == "disabled" and policy.threshold is None


def test_no_source_has_no_favorable_denominator(dataset, tmp_path):
    train = dataset["train"].copy()
    train["resolution"] = None
    retriever = fit(dataset, train)
    review = packet(dataset, retriever, tmp_path)
    rubric = rate(tmp_path)
    policy = lock_review(retriever, dataset["calibration"], artifacts=tmp_path, rubric_path=rubric)
    metrics = evaluate_retriever(retriever, dataset["calibration"], rubric, packet=review)
    assert policy.status == "disabled" and not policy.drafts_enabled
    assert metrics.means == dict.fromkeys(("relevance", "correctness", "safety", "edit_effort"))
    assert metrics.accepted == 0 and metrics.reason_codes == ("no_candidate_denominator",)


def test_test_stays_sealed_until_all_locks_and_pending_cannot_enable_later(dataset, tmp_path):
    retriever = fit(dataset)
    with pytest.raises(ValueError, match="missing"):
        packet(dataset, retriever, tmp_path, "test", model_locks=locks())
    assert not (tmp_path / "review/retrieval-test-packet.json").exists()
    packet(dataset, retriever, tmp_path)
    lock_review(retriever, dataset["calibration"], artifacts=tmp_path, decision="pending_review")
    with pytest.raises(ValueError, match="both_domain"):
        verify_test_gate(retriever, tmp_path, {})
    invalid = locks()
    invalid["customer"] = replace(invalid["customer"], threshold=0.7)
    with pytest.raises(ValueError, match="not_locked"):
        verify_test_gate(retriever, tmp_path, invalid)
    final = packet(dataset, retriever, tmp_path, "test", model_locks=locks())
    cal = json.loads((tmp_path / "review/retrieval-calibration-packet.json").read_text())
    assert {q["query_id"] for q in final["queries"]}.isdisjoint(
        q["query_id"] for q in cal["queries"])
    with pytest.raises(ValueError, match="already_opened"):
        lock_review(retriever, dataset["calibration"], artifacts=tmp_path,
                    rubric_path=rate(tmp_path))


def test_final_review_read_only_threshold_and_failure_disables(dataset, tmp_path):
    retriever = fit(dataset)
    packet(dataset, retriever, tmp_path)
    policy = lock_review(retriever, dataset["calibration"], artifacts=tmp_path,
                         rubric_path=rate(tmp_path))
    review = packet(dataset, retriever, tmp_path, "test", model_locks=locks())
    rubric = rate(tmp_path, "test", safety="2")
    before = (tmp_path / "review/retrieval-policy-lock.json").read_bytes()
    with pytest.raises(ValueError, match="frozen"):
        evaluate_retriever(retriever, dataset["test"], rubric, packet=review,
                           policy=replace(policy, threshold=0.9))
    metrics = finalize_review(retriever, dataset["test"], rubric, artifacts=tmp_path,
                              model_locks=locks())
    assert metrics.unsafe_count == 30
    assert (tmp_path / "review/retrieval-policy-lock.json").read_bytes() == before
    final_policy = load_retrieval_policy(retriever, tmp_path)
    assert final_policy.threshold == policy.threshold and not final_policy.drafts_enabled
    assert asdict(policy)["drafts_enabled"]  # frozen original was never changed
    with pytest.raises(ValueError, match="already_locked"):
        finalize_review(retriever, dataset["test"], rate(tmp_path, "test"), artifacts=tmp_path,
                        model_locks=locks())


def test_stale_provenance_cannot_reuse_lock_or_open_test(dataset, tmp_path):
    retriever = fit(dataset)
    packet(dataset, retriever, tmp_path)
    lock_review(retriever, dataset["calibration"], artifacts=tmp_path,
                rubric_path=rate(tmp_path))
    stale = replace(retriever, provenance={**retriever.provenance,
                                           "source_sha256": "d" * 64})
    with pytest.raises(ValueError, match="provenance"):
        load_retrieval_policy(stale, tmp_path)
    with pytest.raises(ValueError, match="provenance"):
        packet(dataset, stale, tmp_path, "test", model_locks=locks())
    assert not (tmp_path / "review/retrieval-test-opened.json").exists()


def test_final_review_preserves_opening_packet_and_calibration_lock_bytes(dataset, tmp_path):
    retriever = fit(dataset)
    packet(dataset, retriever, tmp_path)
    lock_review(retriever, dataset["calibration"], artifacts=tmp_path,
                rubric_path=rate(tmp_path))
    packet(dataset, retriever, tmp_path, "test", model_locks=locks())
    paths = [tmp_path / "review" / name for name in (
        "retrieval-policy-lock.json",
        "retrieval-test-opened.json",
        "retrieval-test-packet.json",
    )]
    frozen = {path: path.read_bytes() for path in paths}
    finalize_review(retriever, dataset["test"], rate(tmp_path, "test"),
                    artifacts=tmp_path, model_locks=locks())
    assert {path: path.read_bytes() for path in paths} == frozen


def test_cli_reports_missing_artifacts_and_help(tmp_path, capsys):
    assert main(["prepare-review", "--artifacts", str(tmp_path)]) == 1
    assert "make reproduce" in capsys.readouterr().out
    with pytest.raises(SystemExit) as result:
        main(["--help"])
    assert result.value.code == 0
    assert "insufficient_evidence" in capsys.readouterr().out


def test_grid_rejects_low_score_bad_ratings_and_selects_point_six(dataset, tmp_path):
    frame = dataset["calibration"]
    frame.loc[:29, "text"] = frame.loc[:29, "text"].str.replace(
        "device screen failed reset", "device", regex=False)
    frame["text_group_id"] = frame.text.map(
        lambda text: "customer:group:" + content_hash(canonical_text(text)))
    manifest = dataset["manifest"]
    manifest["partitions"]["calibration"]["groups"] = list(frame.text_group_id)
    manifest.pop("split_version")
    manifest["split_version"] = content_hash(manifest)
    retriever = fit(dataset)
    review = packet(dataset, retriever, tmp_path)
    rubric = rate(tmp_path)
    bad_ids = {q["query_id"] for q in review["queries"] if q["sources"][0]["similarity"] < 0.6}
    rows = list(csv.DictReader(io_read(rubric)))
    for row in rows:
        if row["query_id"] in bad_ids:
            row["correctness"] = "1"
    write_ratings(rubric, rows)
    policy = lock_review(retriever, frame, artifacts=tmp_path, rubric_path=rubric)
    assert policy.drafts_enabled and policy.threshold == 0.6
    assert retriever.suggest(frame.iloc[0].text, policy, signals=signal()).draft is None


class FixtureModel:
    """Only a deterministic CLI fixture; never a training or evidence shortcut."""

    model_version = "fixture"

    def predict_one(self, text):
        return Prediction("customer", "ok", "Technical issue", 1.0,
                          {key: float(key == "Technical issue") for key in CUSTOMER_TAXONOMY},
                          "fixture", False)


def cli_manifest_metadata(manifest):
    """Protocol fixtures still obey the shared pre-deserialization boundary."""
    from support_copilot.ui import current_environment

    environment = current_environment()
    manifest.update(schema_version=1, code_revision="fixture+code." + environment["code"],
                    configuration_sha256=environment["configuration_sha256"],
                    lock_sha256=environment["lock_sha256"],
                    runtime={"python": platform.python_version(), "dependencies": {
                        name: importlib.metadata.version(name) for name in (
                            "scikit-learn", "joblib", "pandas", "numpy", "scipy")}})
    for entry in manifest["artifacts"].values():
        entry.update(schema_version=1, dependencies=[],
                     type="domain-model" if entry["path"].endswith(".joblib") else "json")


def test_cli_calibration_template_lock_then_test_without_reading_test_early(dataset, tmp_path):
    manifest = {"artifacts": {}, "splits": {"customer": dataset["manifest"]},
                "sources": {"customer": {"sha256": "a" * 64}},
                "configuration_sha256": "b" * 64}
    for part in ("train", "calibration", "test"):
        path = tmp_path / f"customer-{part}.json"
        path.write_text(json.dumps(dataset[part].to_dict("records")))
        manifest["artifacts"][f"data.customer.{part}"] = {
            "status": "ready", "path": path.name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    for domain in ("customer", "it"):
        path = tmp_path / f"{domain}.joblib"
        policy = lock_policy(base_policy(domain, "fixture"))
        joblib.dump(SimpleNamespace(model=FixtureModel(), policy=policy, reason_codes=(),
                                   configuration_sha256=policy.configuration_sha256), path)
        manifest["artifacts"][f"models.{domain}"] = {
            "status": "ready", "path": path.name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    cli_manifest_metadata(manifest)
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    common = ["--artifacts", str(tmp_path)]
    assert main(["prepare-review", *common, "--split", "test"]) == 1
    assert not (tmp_path / "review/retrieval-test-opened.json").exists()
    assert main(["prepare-review", *common]) == 0
    rubric = rate(tmp_path)
    assert main(["lock-review", *common, "--rubric", str(rubric)]) == 0
    assert main(["prepare-review", *common, "--split", "test"]) == 0
    final = rate(tmp_path, "test")
    assert main(["lock-review", *common, "--split", "test", "--rubric", str(final)]) == 0
    retriever = fit_retriever(dataset["train"], split_manifest=dataset["manifest"],
                              source_sha256="a" * 64,
                              configuration_sha256=manifest["configuration_sha256"])
    assert load_retrieval_policy(retriever, tmp_path).drafts_enabled


def test_cli_unsupported_without_model_binary_is_explicitly_insufficient(dataset, tmp_path, capsys):
    manifest = {"artifacts": {}, "splits": {"customer": dataset["manifest"]},
                "sources": {"customer": {"sha256": "a" * 64}},
                "configuration_sha256": "b" * 64}
    for part in ("train", "calibration"):
        path = tmp_path / f"customer-{part}.json"
        path.write_text(json.dumps(dataset[part].to_dict("records")))
        manifest["artifacts"][f"data.customer.{part}"] = {
            "status": "ready", "path": path.name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    path = tmp_path / "customer-policy.json"
    path.write_text(json.dumps(asdict(lock_policy(base_policy("customer")))))
    manifest["artifacts"]["policies.customer"] = {
        "status": "ready", "path": path.name,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }
    cli_manifest_metadata(manifest)
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    assert main(["prepare-review", "--artifacts", str(tmp_path)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "insufficient_evidence" and result["eligible"] == 0


def test_concurrent_lock_publication_never_overwrites(tmp_path):
    path = tmp_path / "lock.json"

    def write(value):
        try:
            _freeze_json({"value": value}, path)
            return value
        except ValueError:
            return None

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(write, ["first", "second"]))
    successful = [value for value in results if value is not None]
    assert len(successful) == 1
    assert _read_sealed(path) == {"value": successful[0]}
