"""Autocontained sanitized fixtures, never submission metrics or human evidence.

Run from the solution directory, including when collected from the sealed S07 copy.
Only manifest.generated_at is excluded: it records the wall time of publication,
not a scientific result. No other timestamps or numerical tolerances are ignored.
"""

import csv
import hashlib
import io
import json
import re
import runpy
import socket
import sqlite3
import struct
from contextlib import closing
from dataclasses import asdict, replace
from pathlib import Path
from types import SimpleNamespace

import joblib
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

import support_copilot.ui as ui
from support_copilot.data import (
    CUSTOMER_COLUMNS,
    CUSTOMER_TAXONOMY,
    IT_TAXONOMY,
    atomic_json,
    content_hash,
)
from support_copilot.decision import base_policy, lock_policy
from support_copilot.modeling import Prediction
from support_copilot.retrieval import RetrievalPolicy, lock_review
from support_copilot.store import list_decisions

ROOT = Path.cwd()  # S07 lives under runtime; never derive the solution from __file__.
REPRODUCE = runpy.run_path(str(ROOT / "scripts/reproduce.py"))["reproduce"]


def sources(root):
    root.mkdir(parents=True)
    words = [chr(97 + i // 26) + chr(97 + i % 26) + "token" for i in range(20)]
    customer = []
    for label, token in zip(CUSTOMER_TAXONOMY, (
            "billing", "cancellation", "product", "refund", "technical"), strict=True):
        for word in words:
            row = dict.fromkeys(CUSTOMER_COLUMNS, "")
            row.update({"Ticket ID": str(len(customer) + 1), "Ticket Type": label,
                        "Ticket Description": f"{token} {token} device {word}",
                        "Ticket Status": "Closed", "Ticket Priority": "Low",
                        "Ticket Channel": "Email", "Resolution": "reset the device",
                        "First Response Time": "2026-01-01T00:00:00Z",
                        "Time to Resolution": "2026-01-01T01:00:00Z"})
            customer.append(row)
    customer_path, it_path = root / "customer.csv", root / "it.csv"
    pd.DataFrame(customer).to_csv(customer_path, index=False)
    pd.DataFrame([{"Document": f"{token} {token} device {word}", "Topic_group": label}
                  for label, token in zip(IT_TAXONOMY, (
                      "access", "admin", "hr", "hardware", "project", "misc", "purchase",
                      "storage"), strict=True) for word in words]).to_csv(it_path, index=False)
    return customer_path, it_path


def canonical_run(root):
    manifest = json.loads((root / "manifest.json").read_text())
    manifest.pop("generated_at")  # The ONE allowed exclusion, justified in module docstring.
    values = {}
    for key, entry in manifest["artifacts"].items():
        if entry["status"] != "ready":
            continue
        path = root / entry["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]
        if entry["type"] in {"domain-model", "retriever"}:
            value = ui.logical_payload(joblib.load(path))
            # Binary hashes validate their own run, while equivalence uses semantic state.
            entry["sha256"] = entry["logical_sha256"]
        elif path.suffix == ".csv":
            value = json.loads(pd.read_csv(path, keep_default_na=entry["type"] != "review-template")
                               .to_json(orient="records"))
        else:
            value = json.loads(path.read_text())
        assert content_hash(value) == entry["logical_sha256"], key
        values[key] = value
    return json.loads(json.dumps({"manifest": manifest, "values": values}, sort_keys=True))


def test_reproduce_twice_same_inputs(tmp_path):
    customer, it = sources(tmp_path / "sources")
    first, second = tmp_path / "first", tmp_path / "second"
    REPRODUCE(customer, it, first)
    REPRODUCE(customer, it, second)
    assert canonical_run(first) == canonical_run(second)
    assert not (first / "data/customer-test.json").exists()
    assert not (first / "review/retrieval-test-template.csv").exists()
    assert json.loads((first / "models/metrics.json").read_text())["status"] == "sealed"


@pytest.fixture(scope="module")
def prepared(tmp_path_factory):
    root = tmp_path_factory.mktemp("workflow")
    customer, it = sources(root / "source")
    artifacts = root / "artifacts"
    REPRODUCE(customer, it, artifacts)
    return artifacts, customer, it


@pytest.mark.parametrize("mutation", ["metric", "split", "policy", "logical", "timestamp"])
def test_comparison_rejects_every_other_change(prepared, tmp_path, mutation):
    import shutil
    original = prepared[0]
    changed = tmp_path / "changed"
    shutil.copytree(original, changed)
    baseline = canonical_run(original)
    manifest = json.loads((changed / "manifest.json").read_text())
    if mutation == "split":
        manifest["splits"]["customer"]["partitions"]["train"]["ids"][0] = "customer:changed"
    elif mutation == "logical":
        manifest["artifacts"]["models.customer"]["logical_sha256"] = "a" * 64
    else:
        key = {"metric": "models.metrics", "policy": "policies.customer",
               "timestamp": "review.retrieval-calibration-packet"}[mutation]
        entry = manifest["artifacts"][key]
        path = changed / entry["path"]
        value = json.loads(path.read_text())
        value[{"metric": "status", "policy": "threshold", "timestamp": "created_at"}[
            mutation]] = "changed"
        atomic_json(value, path)
        entry["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        entry["logical_sha256"] = content_hash(value)
    atomic_json(manifest, changed / "manifest.json")
    try:
        actual = canonical_run(changed)
    except AssertionError:
        return
    assert actual != baseline


def test_comparison_allows_only_manifest_generated_at(prepared, tmp_path):
    import shutil
    changed = tmp_path / "changed"
    shutil.copytree(prepared[0], changed)
    manifest = json.loads((changed / "manifest.json").read_text())
    manifest["generated_at"] = "2030-01-01T00:00:00Z"
    atomic_json(manifest, changed / "manifest.json")
    assert canonical_run(prepared[0]) == canonical_run(changed)


def test_release_only_after_explicit_lock_preserves_runtime(prepared, tmp_path, monkeypatch):
    import shutil
    original, customer, it = prepared
    root = tmp_path / "artifacts"
    shutil.copytree(original, root)
    bundle = ui.load_artifacts(root)
    retriever = bundle.get("retrieval.customer").value
    calibration = pd.DataFrame(bundle.get("data.customer.calibration").value)
    lock_review(retriever, calibration, artifacts=root, decision="pending_review")
    sentinel = tmp_path / "decisions.sqlite3"
    sentinel.write_bytes(b"unrelated runtime preserved")
    REPRODUCE(customer, it, root)
    assert (root / "review/retrieval-test-opened.json").exists()
    assert (root / "review/retrieval-test-template.csv").exists()
    assert sentinel.read_bytes() == b"unrelated runtime preserved"
    released = ui.load_artifacts(root)
    assert released.get("queue.customer").status == "ready"
    assert "models.customer" in released.manifest["artifacts"]["queue.customer"]["dependencies"]
    app = app_for(released, tmp_path / "runtime", monkeypatch)
    scorecard = app.switch_page("pages/scorecard.py").run()
    assert not scorecard.exception
    captions = " ".join(item.value for item in scorecard.caption)
    assert "Teste final aberto após locks" in captions and "lacrado" not in captions
    before = canonical_run(root)
    REPRODUCE(customer, it, root)
    assert canonical_run(root) == before


@pytest.mark.parametrize("kind", ["missing", "corrupt", "schema", "traversal", "symlink"])
def test_invalid_it_artifact_isolated_before_deserialization(prepared, tmp_path, monkeypatch, kind):
    import shutil
    root = tmp_path / "artifacts"
    shutil.copytree(prepared[0], root)
    manifest = json.loads((root / "manifest.json").read_text())
    entry = manifest["artifacts"]["models.it"]
    path = root / entry["path"]
    if kind == "missing":
        path.unlink()
    elif kind == "corrupt":
        path.write_bytes(b"invalid")
    elif kind == "schema":
        entry["schema_version"] = 99
    elif kind == "traversal":
        entry["path"] = "../outside.joblib"
    else:
        outside = tmp_path / "outside.joblib"
        outside.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(outside)
    atomic_json(manifest, root / "manifest.json")
    loaded, original_load = [], joblib.load
    forbidden = entry["sha256"]
    def spy(path):
        loaded.append(hashlib.sha256(path.getvalue()).hexdigest())
        return original_load(path)
    monkeypatch.setattr(joblib, "load", spy)
    bundle = ui.load_artifacts(root)
    assert bundle.get("models.it").status != "ready"
    assert forbidden not in loaded
    assert bundle.get("analytics.operational_summary").status == "ready"
    assert bundle.get("models.customer").status == "ready"
    assert bundle.get("models.it").correction == "make reproduce"


def fixture_bundle(prepared, *, priority="Low", text=None):
    """A synthetic perfect classifier is adversarial fixture only, never a real artifact."""
    bundle = ui.load_artifacts(prepared[0])
    policy = lock_policy(replace(base_policy("customer", "fixture"), automation_enabled=True,
                                  threshold=0.5, disabled_reason=None))
    probabilities = {label: float(label == "Technical issue") for label in CUSTOMER_TAXONOMY}
    prediction = Prediction("customer", "ok", "Technical issue", 1.0, probabilities,
                            "fixture", False)
    model = SimpleNamespace(predict_one=lambda _: prediction)
    retriever = bundle.get("retrieval.customer").value
    if text is None:
        text = next(row["text"] for row in retriever.records
                    if row["text"].startswith("technical "))
    retrieval = RetrievalPolicy(True, 0.2, "fixture", "fixture", "a" * 64,
                                 "enabled", retriever.index_version)
    states = dict(bundle.features)
    for key, value in {
        "queue.customer": [{"ticket_id": "customer:fixture-a", "text": text,
                            "priority": priority},
                           {"ticket_id": "customer:fixture-b", "text": text,
                            "priority": priority}],
        "models.customer": SimpleNamespace(model=model),
        "policies.customer": asdict(policy), "retrieval.policy": asdict(retrieval),
    }.items():
        states[key] = ui.FeatureState("ready", value, "fixture-only")
    return replace(bundle, features=states)


def app_for(bundle, runtime, monkeypatch, *, operator="fixture-operator"):
    monkeypatch.setenv("SUPPORT_COPILOT_RUNTIME", str(runtime))
    monkeypatch.setattr(ui, "load_artifacts", lambda _: bundle)
    monkeypatch.setattr(ui, "authorized_operator", lambda: operator)
    monkeypatch.setattr(socket, "create_connection", lambda *args, **kwargs: pytest.fail("network"))
    app = AppTest.from_file(str(ROOT / "app.py")).run()
    return app.switch_page("pages/queue.py").run()


def test_anonymous_user_cannot_mutate_or_read_decisions(prepared, tmp_path, monkeypatch):
    app = app_for(fixture_bundle(prepared), tmp_path, monkeypatch, operator=None)
    for label in ("Aprovar", "Editar e aprovar", "Rejeitar", "Escalonar"):
        assert button(app, label).disabled
    assert not (tmp_path / "decisions.sqlite3").exists()
    evidence = app.switch_page("pages/evidence.py").run()
    assert not evidence.exception
    assert "somente leitura" in evidence.warning[-1].value.lower()
    assert all(widget.label != "Persistir export CSV" for widget in evidence.button)
    assert not (tmp_path / "decisions.sqlite3").exists()


def director_app_for(bundle, runtime, monkeypatch):
    monkeypatch.setenv("SUPPORT_COPILOT_RUNTIME", str(runtime))
    monkeypatch.setattr(ui, "load_artifacts", lambda _: bundle)
    monkeypatch.setattr(socket, "create_connection", lambda *args, **kwargs: pytest.fail("network"))
    return AppTest.from_file(str(ROOT / "app.py")).run()


def button(app, label):
    return next(widget for widget in app.button if widget.label == label)


@pytest.mark.parametrize("issuer,subject,expected", [
    ("https://idp.example", "operator-1", "https://idp.example#operator-1"),
    ("https://evil.example", "operator-1", None),
    ("https://idp.example", "operator-2", None),
    (None, "operator-1", None),
])
def test_operator_requires_exact_oidc_issuer_and_subject(monkeypatch, issuer, subject, expected):
    user = SimpleNamespace(is_logged_in=True,
                           to_dict=lambda: {"iss": issuer, "sub": subject})
    secrets = {"authorization": {
        "allowed_issuers": ["https://idp.example"],
        "allowed_subjects": ["operator-1"],
    }}
    monkeypatch.setattr(ui, "st", SimpleNamespace(user=user, secrets=secrets))
    assert ui.authorized_operator() == expected


@pytest.mark.parametrize("label,action", [("Aprovar", "approve"),
    ("Editar e aprovar", "edit_approve"), ("Rejeitar", "reject"), ("Escalonar", "escalate")])
def test_four_actions_rerun_restart_export(prepared, tmp_path, monkeypatch, label, action):
    bundle = fixture_bundle(prepared)
    before = canonical_run(prepared[0])
    app = app_for(bundle, tmp_path, monkeypatch)
    assert not app.exception and app.title[0].value == "Fila diária"
    assert not button(app, "Aprovar").disabled
    submission_id = app.session_state["submission_id"]
    app.text_area[0].input("reset device then retry private@example.test")
    app.text_area[1].input("review requested")
    button(app, label).click().run()
    assert not app.exception and "audit_id=1" in app.success[0].value
    assert not app.session_state["ticket_edits"]["customer:fixture-a"]["dirty"]
    app.run()
    assert app.session_state["submission_id"] == submission_id
    with closing(sqlite3.connect(tmp_path / "decisions.sqlite3", isolation_level=None)) as conn:
        rows = list_decisions(conn)
    assert len(rows) == 1 and rows[0].human_action == action
    assert rows[0].ticket_id == "customer:fixture-a"
    if action == "edit_approve":
        assert "[EMAIL]" in rows[0].final_text and rows[0].edit_ratio > 0
    # Fresh app session sees the same real SQLite event and persists exact export bytes.
    fresh = AppTest.from_file(str(ROOT / "app.py")).run()
    fresh.switch_page("pages/evidence.py").run()
    button(fresh, "Persistir export CSV").click().run()
    assert not fresh.exception and fresh.download_button
    export = fresh.session_state["export"]
    assert export.content == export.path.read_bytes()
    exported = list(csv.DictReader(io.StringIO(export.content.decode())))
    assert exported[0]["id"] == "1" and exported[0]["submission_id"] == submission_id
    assert canonical_run(prepared[0]) == before


@pytest.mark.parametrize("changes", [{"priority": "Critical"},
                                    {"text": "technical device refund"},
                                    {"text": "technical device private@example.test"}])
def test_risk_precedes_perfect_confidence_in_pipeline_and_ui(prepared, tmp_path, monkeypatch,
                                                          changes):
    bundle = fixture_bundle(prepared, **changes)
    app = app_for(bundle, tmp_path, monkeypatch)
    assert not app.exception
    assert button(app, "Aprovar").disabled and button(app, "Editar e aprovar").disabled
    assert not button(app, "Escalonar").disabled
    row = bundle.get("queue.customer").value[0]
    assessed = ui.assess_ticket({**row, "domain": "customer", "Ticket Priority": row["priority"]},
                                bundle.get("models.customer").value.model,
                                ui._policy(bundle, "customer"),
                                bundle.get("retrieval.customer").value,
                                RetrievalPolicy(**bundle.get("retrieval.policy").value))
    assert assessed["route"]["action"] == "human_review"
    assert assessed["retrieval"]["draft"] is None
    if changes.get("priority") == "Critical":
        # An exact indexed description is the maximal cosine match, still never a draft.
        assert assessed["prediction"]["confidence"] == 1.0
        assert assessed["retrieval"]["sources"][0]["similarity"] == pytest.approx(1.0)
    if "@" in changes.get("text", ""):
        assert assessed["retrieval"]["sources"] == ()  # Privacy blocks querying altogether.


def test_ticket_change_and_failed_write_preserve_form(prepared, tmp_path, monkeypatch):
    bundle = fixture_bundle(prepared)
    app = app_for(bundle, tmp_path, monkeypatch)
    old_uuid = app.session_state["submission_id"]
    app.text_area[0].input("edited first ticket")
    app.text_area[1].input("first reason")
    app.run()
    app.selectbox[2].select("customer:fixture-b").run()
    assert "Alterações não persistidas de customer:fixture-a preservadas" in app.warning[0].value
    assert app.text_area[0].value == "reset the device"
    assert app.session_state["submission_id"] != old_uuid
    new_uuid = app.session_state["submission_id"]
    app.text_area[0].input("edited second ticket")
    monkeypatch.setattr(ui, "persist_decision", lambda *_: (_ for _ in ()).throw(
        sqlite3.OperationalError("fixture failure")))
    button(app, "Editar e aprovar").click().run()
    assert app.error and not app.success
    assert app.text_area[0].value == "edited second ticket"
    assert app.session_state["submission_id"] == new_uuid
    app.selectbox[2].select("customer:fixture-a").run()
    assert app.text_area[0].value == "edited first ticket"
    assert app.text_area[1].value == "first reason"
    assert app.session_state["submission_id"] == old_uuid
    app.selectbox[2].select("customer:fixture-b").run()
    assert app.text_area[0].value == "edited second ticket"
    assert app.session_state["submission_id"] == new_uuid


def test_ticket_draft_survives_immediate_switch_and_commit_clears_dirty(
        prepared, tmp_path, monkeypatch):
    app = app_for(fixture_bundle(prepared), tmp_path, monkeypatch)
    app.text_area[0].input("pending answer")
    app.text_area[1].input("pending reason")
    app.selectbox[2].select("customer:fixture-b").run()
    assert app.warning and not app.success
    app.selectbox[2].select("customer:fixture-a").run()
    assert app.text_area[0].value == "pending answer"
    assert app.text_area[1].value == "pending reason"
    button(app, "Editar e aprovar").click().run()
    assert app.success
    assert not app.session_state["ticket_edits"]["customer:fixture-a"]["dirty"]
    app.selectbox[2].select("customer:fixture-b").run()
    assert not app.warning
    app.selectbox[2].select("customer:fixture-a").run()
    assert button(app, "Editar e aprovar").disabled
    assert app.text_area[0].value == "pending answer"
    assert app.success


def test_presentation_formats_copy_without_changing_internal_values(monkeypatch):
    captured = []
    monkeypatch.setattr(ui.st, "dataframe",
                        lambda frame, **kwargs: captured.append((frame, kwargs)))
    source = [{"priority": "Critical", "confidence": 0.875, "missing": None}]
    ui._table(source, {"priority": "Prioridade", "confidence": "Confiança", "missing": "Ausente"},
              categories=("priority",), percentages=("confidence",))
    frame, options = captured[0]
    assert frame.iloc[0].to_dict() == {
        "priority": "Crítica", "confidence": "87,50%", "missing": "Indisponível"}
    assert options["column_config"]["confidence"]["label"] == "Confiança"
    assert source == [{"priority": "Critical", "confidence": 0.875, "missing": None}]
    assert ui._label("category:Refund request") == "Categoria sensível: Pedido de reembolso"
    assert ui._label("text:private_pattern") == "Expressão sensível detectada"


def _primary_elements(node):
    if node.type == "expander" and node.label == "Detalhes técnicos":
        return
    yield node
    for child in getattr(node, "children", {}).values():
        yield from _primary_elements(child)


def test_pages_use_portuguese_labels_and_keep_raw_json_in_technical_details(
        prepared, tmp_path, monkeypatch):
    app = app_for(fixture_bundle(prepared, priority="Critical"), tmp_path, monkeypatch)
    assert app.selectbox[0].options == ["Todas", "Crítica", "Alta", "Média", "Baixa"]
    assert app.selectbox[1].options == ["Todas", "Revisão humana", "Encaminhamento automático"]
    assert app.dataframe[0].value.iloc[0]["Prioridade"] == "Crítica"
    assert app.dataframe[0].value.iloc[0]["Confiança"] == "100,00%"
    for page in (None, "pages/scorecard.py", "pages/it_lab.py", "pages/evidence.py"):
        if page:
            app.switch_page(page).run()
        assert not app.exception
        if page == "pages/scorecard.py":
            assert app.title[0].value == "Diagnóstico operacional" and not app.header
        if page == "pages/it_lab.py":
            app.text_area[0].input("hardware device")
            button(app, "Classificar IT").click().run()
            assert not app.exception
        primary = list(_primary_elements(app.main))
        assert not any(item.type == "json" for item in primary)
        text = " ".join(str(item.value) for item in primary
                        if item.type in {"markdown", "caption", "warning", "info", "title"})
        for code in ("human_review", "critical_priority", "ambiguous_input", "no_reliable_signal",
                     "Technical issue", "insufficient_support", "customer_structured_operational"):
            assert code not in text


def test_default_director_brief_and_separate_pages(prepared, tmp_path, monkeypatch):
    monkeypatch.setenv("SUPPORT_COPILOT_ARTIFACTS", str(tmp_path))
    monkeypatch.setenv("SUPPORT_COPILOT_RUNTIME", str(tmp_path / "runtime"))
    app = AppTest.from_file(str(ROOT / "app.py")).run()
    assert not app.exception and app.title[0].value == "Resposta ao Diretor"
    assert "make reproduce" in app.warning[0].value
    monkeypatch.setenv("SUPPORT_COPILOT_ARTIFACTS", str(prepared[0]))
    scorecard = app.switch_page("pages/scorecard.py").run()
    assert not scorecard.exception
    assert [x.value for x in scorecard.subheader] == [
        "Histórico observado", "Desempenho medido", "Cenários projetados"]
    captions = " ".join(item.value for item in scorecard.caption)
    assert "fonte: Dados operacionais estruturados" in captions
    assert "não observa custo nem moeda" in captions
    assert all(item.value == 30000 for item in scorecard.number_input
               if item.label == "Volume anual elegível")
    assert all(item.value == 0 for item in scorecard.number_input
               if item.label == "Custo por hora (premissa; moeda não definida)")
    scorecard_text = " ".join(str(getattr(item, "value", ""))
                              for item in _primary_elements(scorecard.main))
    for hours in ("150,00", "625,00", "1.600,00"):
        assert hours in scorecard_text
    lab = app.switch_page("pages/it_lab.py").run()
    lab.text_area[0].input("hardware device")
    button(lab, "Classificar IT").click().run()
    assert not lab.exception


def test_director_brief_answers_three_questions_from_verified_artifacts(
        prepared, tmp_path, monkeypatch):
    app = director_app_for(ui.load_artifacts(prepared[0]), tmp_path / "runtime", monkeypatch)
    assert not app.exception and app.title[0].value == "Resposta ao Diretor"
    text = " ".join(str(item.value) for item in _primary_elements(app.main)
                    if item.type in {"markdown", "caption", "warning", "info", "title"})
    for answer in ("Onde perdemos tempo?", "O que automatizar?", "Funciona?",
                   "Piloto shadow", "automação Customer bloqueada", "1.000 tickets",
                   "macro-F1 ≥ 75%", "reduzir em ≥ 20%"):
        assert answer in text
    assert "0% Customer" in text
    evidence = ui.automation_evidence({"domains": {
        "customer": {"macro_f1": 0.1394, "ece": 0.0328,
                     "denominators": {"n_total": 231},
                     "risk_coverage": [{"threshold": 0.5, "coverage": 0,
                                        "selective_risk": None, "n_total": 231}]},
        "it": {"macro_f1": 0.8351, "ece": 0.0414,
               "denominators": {"n_total": 5301},
               "risk_coverage": [{"threshold": 0.55, "coverage": 0.3742690058,
                                  "selective_risk": 0.1063508065, "n_total": 5301}]},
    }}, {"customer": {"threshold": None}, "it": {"threshold": 0.55}}).set_index(
        "Domínio")
    assert evidence.loc["Customer", "Cobertura no teste"] == 0
    assert evidence.loc["Customer", "Decisão atual"] == "Bloqueada: 0% elegível"
    assert evidence.loc["IT", "Teste congelado (n)"] == 5301
    assert evidence.loc["IT", "Limiar travado"] == pytest.approx(0.55)
    assert evidence.loc["IT", "Cobertura no teste"] == pytest.approx(0.3742690058)
    assert evidence.loc["IT", "Risco seletivo"] == pytest.approx(0.1063508065)
    assert "shadow" in evidence.loc["IT", "Decisão atual"]
    queue = app.switch_page("pages/queue.py").run()
    assert not queue.exception and queue.title[0].value == "Fila diária"


@pytest.mark.parametrize("test_status,retrieval_status,expected", [
    ("sealed", "pending_review", "aguardando revisão humana"),
    ("sealed", "insufficient_evidence", "sem evidência suficiente"),
    ("released_after_locks", "enabled", "Teste final aberto após locks"),
    ("released_after_locks", "disabled", "recuperação desativada"),
    ("released_after_locks", "insufficient_evidence", "sem evidência suficiente"),
    ("unknown", "disabled", "Estado do teste final não verificável"),
    (None, "insufficient_evidence", "Estado do teste final não verificável"),
])
def test_scorecard_reports_verified_test_lifecycle(
        prepared, tmp_path, monkeypatch, test_status, retrieval_status, expected):
    bundle = ui.load_artifacts(prepared[0])
    states = dict(bundle.features)
    states["models.metrics"] = ui.FeatureState(
        "corrupt" if test_status is None else "ready", {"status": test_status},
        "models/metrics.json", "artifact_hash_mismatch" if test_status is None else None)
    states["retrieval.metrics"] = ui.FeatureState(
        "ready", {"status": retrieval_status}, "retrieval/metrics.json")
    app = app_for(replace(bundle, features=states), tmp_path, monkeypatch)
    scorecard = app.switch_page("pages/scorecard.py").run()
    assert not scorecard.exception
    captions = " ".join(item.value for item in scorecard.caption)
    assert "Associação não demonstra causalidade" in captions
    assert expected in captions
    assert ("Teste final lacrado" in captions) == (test_status == "sealed")
    assert ("Teste final aberto após locks" in captions) == (
        test_status == "released_after_locks")
    if test_status is None:
        assert any("make reproduce" in item.value for item in scorecard.warning)


def test_demo_has_no_install_download_or_training():
    import subprocess
    command = subprocess.check_output(["make", "-n", "demo"], cwd=ROOT, text=True)
    assert "pip install" not in command and "scripts/reproduce.py" not in command
    assert "curl -" not in command and "streamlit" in command


@pytest.mark.parametrize("field", ["lock_sha256", "configuration_sha256", "code_revision"])
def test_stale_environment_never_loads_binary(prepared, tmp_path, monkeypatch, field):
    import shutil
    root = tmp_path / "artifacts"
    shutil.copytree(prepared[0], root)
    manifest = json.loads((root / "manifest.json").read_text())
    manifest[field] = "changed"
    atomic_json(manifest, root / "manifest.json")
    monkeypatch.setattr(joblib, "load", lambda *_: pytest.fail("stale binary loaded"))
    bundle = ui.load_artifacts(root)
    assert bundle.get("models.customer").status == "stale"


def test_hash_check_is_shared_with_cli(prepared, tmp_path, monkeypatch):
    import shutil

    from support_copilot.retrieval import _artifact

    root = tmp_path / "artifacts"
    shutil.copytree(prepared[0], root)
    manifest = json.loads((root / "manifest.json").read_text())
    (root / manifest["artifacts"]["models.customer"]["path"]).write_bytes(b"corrupt")
    monkeypatch.setattr(joblib, "load", lambda *_: pytest.fail("corrupt binary loaded"))
    with pytest.raises(ValueError, match="hash_mismatch"):
        _artifact(root, manifest, "models.customer")


def test_unsupported_models_create_policies_without_binary(tmp_path):
    customer, it = sources(tmp_path / "source")
    # One sanitized representative per class: taxonomy remains valid, support is insufficient.
    for path, target in ((customer, "Ticket Type"), (it, "Topic_group")):
        pd.read_csv(path).groupby(target).head(1).to_csv(path, index=False)
    manifest = REPRODUCE(customer, it, tmp_path / "artifacts")
    for domain in ("customer", "it"):
        assert manifest["models"][domain]["status"] == "insufficient_support"
        assert manifest["artifacts"][f"models.{domain}"]["status"] == "unavailable"
        assert not (tmp_path / f"artifacts/models/{domain}.joblib").exists()
        assert (tmp_path / f"artifacts/models/{domain}-policy.json").exists()
    assert manifest["retrieval"]["eligible_queries"] == 0


def test_reject_requires_reason_and_readback_failure_never_confirms(prepared, tmp_path,
                                                                  monkeypatch):
    app = app_for(fixture_bundle(prepared), tmp_path, monkeypatch)
    button(app, "Rejeitar").click().run()
    assert app.error and not app.success
    monkeypatch.setattr(ui, "list_decisions", lambda _: [])
    button(app, "Aprovar").click().run()
    assert app.error and not app.success
    with closing(sqlite3.connect(tmp_path / "decisions.sqlite3", isolation_level=None)) as conn:
        assert len(list_decisions(conn)) == 1  # Commit exists; missing readback is NOT success.


def test_pipeline_sanitizer_checks_final_whitespace_normalized_form(tmp_path):
    from support_copilot.data import load_customer_tickets, sanitize_text

    # Synthetic reproduction of the real failure: joining lines must not create
    # a value accepted at ingestion and quarantined by the model's second check.
    with pytest.raises(ValueError, match="suspected_name"):
        sanitize_text("Technical\nIssue")
    assert sanitize_text(sanitize_text("reset\n the device")) == "reset the device"
    customer, _ = sources(tmp_path / "source")
    raw = pd.read_csv(customer, keep_default_na=False)
    raw.loc[0, "Ticket Description"] = "Technical\nIssue"
    raw.to_csv(customer, index=False)
    frame = load_customer_tickets(customer)
    assert frame.attrs["quality"]["excluded"]["privacy_quarantine"] == 1
    assert all(sanitize_text(text) == text for text in frame.text)


def test_corrupt_customer_model_blocks_queue_with_actionable_relative_path(prepared, tmp_path,
                                                                         monkeypatch):
    import shutil

    root = tmp_path / "private-home" / "artifacts"
    shutil.copytree(prepared[0], root)
    bundle = ui.load_artifacts(root)
    lock_review(bundle.get("retrieval.customer").value,
                pd.DataFrame(bundle.get("data.customer.calibration").value),
                artifacts=root, decision="pending_review")
    REPRODUCE(prepared[1], prepared[2], root)
    assert ui.load_artifacts(root).get("queue.customer").status == "ready"
    (root / "models/customer.joblib").write_bytes(b"corrupt")
    bundle = ui.load_artifacts(root)
    assert bundle.get("models.customer").status == "corrupt"
    assert bundle.get("queue.customer").status == "stale"
    assert bundle.get("queue.customer").reason == "dependency_unavailable:models.customer"
    assert bundle.get("analytics.operational_summary").status == "ready"
    assert bundle.get("models.it").status == "ready"
    assert all(not Path(state.path).is_absolute() and ".." not in Path(state.path).parts
               for state in bundle.features.values())
    app = app_for(bundle, tmp_path / "runtime", monkeypatch)
    assert not app.exception and not app.button
    warnings = "\n".join(warning.value for warning in app.warning)
    assert "models/customer.joblib" in warnings
    assert "Integridade do arquivo divergente" in warnings and "make reproduce" in warnings
    assert any("artifact_hash_mismatch" in item.value for item in app.json)
    assert str(tmp_path) not in warnings and "private-home" not in warnings
    app.switch_page("pages/evidence.py").run()
    assert not app.exception
    resource_table = app.dataframe[0].value
    assert "models/customer.joblib" in resource_table["caminho"].tolist()
    assert all(not Path(path).is_absolute() for path in resource_table["caminho"])


def test_missing_manifest_and_rejected_path_never_expose_local_absolute_path(prepared, tmp_path):
    import shutil

    missing = ui.load_artifacts(tmp_path / "private-home" / "missing")
    assert missing.get("manifest").path == "manifest.json"
    assert missing.get("unregistered").path == "manifest.json"
    root = tmp_path / "artifacts"
    shutil.copytree(prepared[0], root)
    manifest = json.loads((root / "manifest.json").read_text())
    manifest["artifacts"]["models.customer"]["path"] = str(tmp_path / "private-model.joblib")
    atomic_json(manifest, root / "manifest.json")
    rejected = ui.load_artifacts(root).get("models.customer")
    assert rejected.status == "incompatible"
    assert rejected.path == "manifest.json"


def test_delivery_documentation_contract():
    documents = (ROOT / "README.md", ROOT.parent.parent / "README.md")
    technical, executive = (path.read_text(encoding="utf-8") for path in documents)

    for command in ("make doctor", "make setup", "make data", "make reproduce",
                    "make demo", "make test", "make lint"):
        assert command in technical
    for section in ("Histórico observado", "Desempenho medido", "Cenários projetados",
                    "Evidências finais", "Protocolo humano de recuperação"):
        assert section in technical
    for answer in ("Onde estamos perdendo tempo?", "O que pode ser automatizado com IA?",
                   "Como isso funciona na prática?"):
        assert answer in executive
    assert "LinkedIn:** Não informado" in executive
    assert "insufficient_evidence" in technical and "zero consultas elegíveis" in technical
    assert "Screenshot real da demonstração" in executive
    assert "CK-12" in executive and "zero consultas elegíveis" in executive
    assert "primeiro `make setup` precisa de rede ou de" in technical
    assert "cache local completo" in technical and "sem build isolation" in technical
    assert "baixe os dois ZIPs" in technical and "extraia exatamente" in technical

    link_pattern = re.compile(r"\[[^]]+\]\(([^)]+)\)")
    for document, content in zip(documents, (technical, executive), strict=True):
        for target in link_pattern.findall(content):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            relative = target.split("#", 1)[0]
            assert not relative.startswith(("data/raw/", "data/runtime/", "artifacts/"))
            assert (document.parent / relative).resolve().exists(), (document, target)


def test_public_demo_evidence_correlates_capture_export_and_metrics():
    """Public evidence must be real, internally linked and safe to open in a spreadsheet."""
    evidence = ROOT / "evidence"
    screenshot = evidence / "screenshot.png"
    export = evidence / "decisions-demo.csv"
    metrics = json.loads((evidence / "metrics.json").read_text(encoding="utf-8"))
    demo = metrics["demo_evidence"]

    image = screenshot.read_bytes()
    assert image.startswith(b"\x89PNG\r\n\x1a\n")
    width, height = struct.unpack(">II", image[16:24])
    assert width >= 1000 and height >= 600
    assert hashlib.sha256(image).hexdigest() == demo["screenshot_sha256"]

    content = export.read_bytes()
    assert hashlib.sha256(content).hexdigest() == demo["export_sha256"]
    rows = list(csv.DictReader(io.StringIO(content.decode("utf-8"))))
    assert rows and [int(row["id"]) for row in rows] == demo["audit_ids"]
    assert set(demo["actions_observed"]) == {row["human_action"] for row in rows}
    assert all(row["submission_id"] and row["created_at"] for row in rows)
    assert all(not any(value.lstrip().startswith(("=", "+", "-", "@"))
                       for value in row.values() if value) for row in rows)
    assert demo["approval_evidence"] == "blocked_insufficient_retrieval_evidence"
    assert metrics["retrieval_evaluation"]["eligible"] == 0
    assert metrics["retrieval_evaluation"]["ck_12_complete"] is False
