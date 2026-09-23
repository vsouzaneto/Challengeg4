import json
from pathlib import Path

import pandas as pd
import pytest

from support_copilot.data import (
    CUSTOMER_COLUMNS,
    IT_TAXONOMY,
    OPERATIONAL_COLUMNS,
    atomic_json,
    canonical_json,
    canonical_text,
    load_customer_analytics,
    load_customer_tickets,
    load_it_tickets,
    make_split,
    sanitize_customer_analytics_frame,
    sanitize_customer_frame,
    sanitize_text,
    write_manifest,
)


def customer_row(**changes):
    row = dict.fromkeys(CUSTOMER_COLUMNS, "")
    row.update({"Ticket ID": "1", "Customer Name": "Example Person",
                "Customer Email": "example@example.invalid", "Customer Age": "31",
                "Customer Gender": "Other", "Ticket Description": "device does not boot",
                "Ticket Type": "Technical issue", "Ticket Status": "Closed",
                "Ticket Priority": "High", "Ticket Channel": "Email",
                "Customer Satisfaction Rating": "4"})
    row.update(changes)
    return row


def split_frame(n=20):
    # Words, rather than numbers, make independent canonical fixture groups.
    words = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota",
             "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", "rho", "sigma", "tau", "upsilon"]
    return pd.DataFrame([
        {"ticket_id": f"it:{label}:{i}", "domain": "it", "text": f"{label} {word}",
         "text_group_id": "untrusted", "target": label}
        for label in ("Hardware", "Access") for i, word in enumerate(words[:n])
    ])


def manifest():
    return {"schema_version": 1, "generated_at": "2026-09-21T00:00:00Z",
            "code_revision": "abc+diff.def", "configuration_sha256": "a" * 64,
            "lock_sha256": "b" * 64, "runtime": {"python": "3.12", "dependencies": {}},
            "sources": {}, "splits": {}, "models": {}, "artifacts": {},
            "retrieval": {
                "status": "unavailable", "reason": "not_implemented", "reference_split": None,
                "index_version": None, "policy_version": None, "packet_ids": [],
                "rubric_sha256": {}, "lock_sha256": None, "threshold": None,
                "eligible_queries": None, "reviewed_queries": 0,
            }}


def test_known_pii_masked_and_unknown_names_quarantined():
    output = sanitize_text("Example Person: example@example.invalid +55 (11) 99999-1234",
                           ["Example Person"])
    assert output == "[NAME]: [EMAIL] [PHONE]"
    for raw in ("Contact Jane", "my name is jane", "John Smith needs help", "cpf: 123",
                "Jane called"):
        with pytest.raises(ValueError, match="privacy_quarantine") as error:
            sanitize_text(raw)
        assert raw not in str(error.value)
    assert sanitize_text(None) == ""
    with pytest.raises(ValueError, match="invalid_type"):
        sanitize_text(4)


def test_customer_boundary_and_quality():
    raw = pd.DataFrame([
        customer_row(**{"Ticket Description": "Example needs help", "Resolution": "restart"}),
        customer_row(**{"Ticket ID": "2", "Resolution": "ask Jane Smith"}),
        customer_row(**{"Ticket ID": "3", "Customer Satisfaction Rating": "-2",
                        "First Response Time": "private@example.invalid"}),
    ])
    frame = sanitize_customer_frame(raw)
    assert len(frame) == 2
    assert frame.iloc[0].text == "[NAME] needs help"
    assert not set(frame) & {"Customer Name", "Customer Email", "Customer Age", "Customer Gender"}
    assert frame.iloc[1]["Customer Satisfaction Rating"] is None
    assert frame.iloc[1].satisfaction_status == "invalid"
    assert frame.iloc[1]["First Response Time"] == "[INVALID_TIMESTAMP]"
    assert frame.attrs["quality"]["excluded"]["privacy_quarantine"] == 1


def test_structured_lane_preserves_observations_without_text_or_pii():
    raw = pd.DataFrame([
        customer_row(**{"First Response Time": "2023-01-01 09:00:00",
                        "Time to Resolution": "2023-01-01 10:00:00"}),
        customer_row(**{"Ticket ID": "2", "Ticket Description": "ask Jane Smith",
                        "First Response Time": "2023-01-01 09:00:00",
                        "Time to Resolution": "2023-01-01 11:00:00"}),
        customer_row(**{"Ticket ID": "3", "Resolution": "ask Jane Smith",
                        "First Response Time": "2023-01-01 09:00:00",
                        "Time to Resolution": "2023-01-01 12:00:00"}),
        customer_row(**{"Ticket ID": "4", "Ticket Description": "",
                        "First Response Time": "private@example.invalid",
                        "Customer Satisfaction Rating": "private@example.invalid"}),
    ])
    before = raw.copy(deep=True)
    structured = sanitize_customer_analytics_frame(raw)
    textual = sanitize_customer_frame(raw)
    pd.testing.assert_frame_equal(raw, before)
    assert len(structured) == 4
    assert len(textual) == 1
    assert textual.attrs["quality"]["excluded"] == {"privacy_quarantine": 2, "empty_text": 1}
    assert set(structured) == {
        *OPERATIONAL_COLUMNS, "ticket_id", "domain", "target", "satisfaction_status",
    }
    assert structured.attrs["quality"]["input_rows"] == 4
    assert structured.attrs["quality"]["sanitized_rows"] == 4
    assert structured.attrs["quality"]["invalid_satisfaction"] == 1
    assert structured["satisfaction_status"].eq("valid").sum() == 3
    assert structured["First Response Time"].eq("[INVALID_TIMESTAMP]").sum() == 1
    payload = canonical_json(structured.to_dict("records")).decode()
    for secret in ("Example", "Jane", "Smith", "@", "device does not boot", "Other"):
        assert secret not in payload
    # Expose no textual schema even if metadata is accidentally dropped downstream.
    with pytest.raises(ValueError, match="split_forbidden:structured_analytics"):
        make_split(structured.assign(text="injected", text_group_id="injected"), "target")
    without_attrs = structured.copy()
    without_attrs.attrs = {}
    with pytest.raises(ValueError, match="split_schema_mismatch"):
        make_split(without_attrs, "target")
    pd.testing.assert_frame_equal(
        structured, sanitize_customer_analytics_frame(raw.sample(frac=1, random_state=17))
    )


def test_structured_loader_provenance_and_shared_validation(tmp_path):
    path = tmp_path / "customer.csv"
    raw = pd.DataFrame([customer_row(), customer_row(**{"Ticket ID": "2"})])
    raw.to_csv(path, index=False)
    structured, textual = load_customer_analytics(path), load_customer_tickets(path)
    pd.testing.assert_frame_equal(structured, load_customer_analytics(path))
    assert structured.attrs["source"]["sha256"] == textual.attrs["source"]["sha256"]
    assert structured.attrs["source"]["data_version"] != textual.attrs["source"]["data_version"]
    assert structured.attrs["source"]["allowed_columns"] == list(structured.columns)
    assert structured.attrs["source"]["lane"] == "structured_operational"
    assert "lane" not in textual.attrs
    for changed, message in (
        (raw.drop(columns=["Ticket Channel"]), "schema_mismatch"),
        (raw.assign(**{"Ticket ID": ["1", "1"]}), "duplicate_id"),
        (raw.assign(**{"Ticket Channel": "private@example.invalid"}), "invalid_enum"),
        (raw.assign(**{"Ticket Type": "private@example.invalid"}), "invalid_taxonomy"),
    ):
        for loader in (sanitize_customer_frame, sanitize_customer_analytics_frame):
            with pytest.raises(ValueError, match=message) as error:
                loader(changed)
            assert "private@example.invalid" not in str(error.value)


def test_structured_loading_cannot_change_textual_splits(tmp_path):
    path = tmp_path / "customer.csv"
    words = ("alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
             "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", "rho",
             "sigma", "tau", "upsilon")
    raw = pd.DataFrame([
        customer_row(**{"Ticket ID": str(i + 1), "Ticket Description": f"device {word}"})
        for i, word in enumerate(words)
    ] + [customer_row(**{"Ticket ID": "21", "Ticket Description": "ask Jane Smith"})])
    raw.to_csv(path, index=False)
    before = make_split(load_customer_tickets(path), "target")
    assert len(load_customer_analytics(path)) == 21
    after = make_split(load_customer_tickets(path), "target")
    assert before.manifest == after.manifest
    assert [len(after.train), len(after.calibration), len(after.test)] == [12, 4, 4]
    assert "customer:21" not in {
        ticket for partition in after.manifest["partitions"].values() for ticket in partition["ids"]
    }


REAL_CUSTOMER_FIXTURE = Path(__file__).parents[1] / "data/raw/customer_support_tickets.csv"


@pytest.mark.skipif(
    not REAL_CUSTOMER_FIXTURE.is_file(), reason="optional public CSV not downloaded"
)
def test_structured_real_customer_source_counts():
    frame = load_customer_analytics(REAL_CUSTOMER_FIXTURE)
    first = pd.to_datetime(frame["First Response Time"], format="mixed", utc=True)
    resolved = pd.to_datetime(frame["Time to Resolution"], format="mixed", utc=True)
    eligible = frame["Ticket Status"].eq("Closed") & first.notna() & resolved.notna()
    eligible &= resolved >= first
    assert len(frame) == frame.attrs["source"]["total_rows"] == 8469
    assert int(eligible.sum()) == 1404
    assert int(frame["satisfaction_status"].eq("valid").sum()) == 2769
    assert set(frame) == {
        *OPERATIONAL_COLUMNS, "ticket_id", "domain", "target", "satisfaction_status",
    }
    assert canonical_json(frame.to_dict("records")) == canonical_json(
        load_customer_analytics(REAL_CUSTOMER_FIXTURE).to_dict("records")
    )


def test_loaders_schema_id_taxonomy_and_missing_source(tmp_path):
    path = tmp_path / "customer.csv"
    pd.DataFrame([customer_row()]).to_csv(path, index=False)
    frame = load_customer_tickets(path)
    assert frame.ticket_id.tolist() == ["customer:1"]
    assert len(frame.attrs["source"]["sha256"]) == 64
    for rows, message in (([customer_row(), customer_row()], "duplicate_id"),
                          ([{"secret_column": "secret"}], "schema_mismatch")):
        pd.DataFrame(rows).to_csv(path, index=False)
        with pytest.raises(ValueError, match=message):
            load_customer_tickets(path)
    with pytest.raises(ValueError) as missing:
        load_customer_tickets(tmp_path / "missing.csv")
    assert str(missing.value) == (
        "source_missing:customer; download ZIP "
        "https://www.kaggle.com/api/v1/datasets/download/"
        "suraj520/customer-support-ticket-dataset; extract customer_support_tickets.csv; "
        "place at data/raw/customer_support_tickets.csv"
    )
    it = tmp_path / "it.csv"
    pd.DataFrame({"Document": ["reset access"] * 8, "Topic_group": IT_TAXONOMY}).to_csv(
        it, index=False
    )
    assert set(load_it_tickets(it).target) == set(IT_TAXONOMY)
    pd.DataFrame({"Document": ["reset"], "Topic_group": ["other"]}).to_csv(it, index=False)
    with pytest.raises(ValueError, match="invalid_taxonomy"):
        load_it_tickets(it)


def test_split_disjoint_deterministic_stratified_and_test_sealed():
    frame = split_frame()
    split = make_split(frame, "target")
    repeated = make_split(frame.sample(frac=1, random_state=7), "target")
    assert split.split_version == repeated.split_version
    assert [len(split.train), len(split.calibration), len(split.test)] == [24, 8, 8]
    assert not {"text", "target", "resolution"} & set(split.test)
    for key in ("ticket_id", "text_group_id"):
        sets = [set(part[key]) for part in (split.train, split.calibration, split.test)]
        assert not (sets[0] & sets[1] or sets[0] & sets[2] or sets[1] & sets[2])
    assert set(split.calibration_fit.target) == {"Hardware", "Access"}
    assert not set(split.calibration_fit.ticket_id) & set(split.policy_selection.ticket_id)


def test_duplicate_conflict_and_scarcity_are_counted():
    frame = split_frame()
    duplicate = frame.iloc[0].copy()
    duplicate["ticket_id"] = "it:duplicate"
    conflict = frame.iloc[1].copy()
    conflict["ticket_id"], conflict["target"] = "it:conflict", "Access"
    frame = pd.concat([frame, pd.DataFrame([duplicate, conflict])], ignore_index=True)
    split = make_split(frame, "target")
    assert split.manifest["exclusions"]["duplicate_rows"] == 1
    assert split.manifest["exclusions"]["conflicting_rows"] == 2
    assert "it:conflict" not in set(split.train.ticket_id) | set(split.test.ticket_id)
    scarce = make_split(split_frame(4), "target")
    assert scarce.manifest["status"] == "insufficient_support"
    assert scarce.train.empty and scarce.test.empty
    assert scarce.manifest["exclusions"]["representatives"] == 8
    assert canonical_text("Ticket 123: Reset!") == canonical_text("ticket 999 reset")
    with pytest.raises(ValueError, match="domain_mismatch"):
        make_split(frame.assign(domain=["customer"] + ["it"] * (len(frame) - 1)), "target")


def test_manifest_finite_atomic_and_no_self_hash(tmp_path, monkeypatch):
    path = tmp_path / "manifest.json"
    good = manifest()
    write_manifest(good, path)
    before = path.read_bytes()
    assert json.loads(before) == good
    for value in (float("nan"), float("inf")):
        invalid = manifest()
        invalid["runtime"]["invalid"] = value
        with pytest.raises(ValueError, match="finite JSON"):
            write_manifest(invalid, path)
        assert path.read_bytes() == before
    invalid = manifest()
    invalid["artifacts"]["self"] = {"status": "ready", "path": "manifest.json",
                                      "sha256": "a" * 64, "logical_sha256": "b" * 64}
    with pytest.raises(ValueError, match="artifact_path"):
        write_manifest(invalid, path)
    monkeypatch.setattr("support_copilot.data.os.replace",
                        lambda *_: (_ for _ in ()).throw(OSError()))
    with pytest.raises(ValueError, match="artifact_write_failed"):
        atomic_json({"new": 1}, path)
    assert path.read_bytes() == before
    assert list(tmp_path.iterdir()) == [Path(path)]
