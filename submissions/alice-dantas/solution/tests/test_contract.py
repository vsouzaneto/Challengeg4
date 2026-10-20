"""Contrato tipado da API (plano do contrato, fase F1)."""
import importlib.util
import json
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from api.schemas import (Evidence, Intelligence, IntelligenceDeals, Meta, Rules, SellerList, SellerPipeline,
                         TeamPipeline)
from leadscorer import codes, data, evidence, intelligence, policy, views
from leadscorer.__main__ import main

def load_script(name):
    spec = importlib.util.spec_from_file_location(name, policy.SOLUTION_DIR / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


export_openapi = load_script("export_openapi")
export_fixtures = load_script("export_fixtures")


def as_json(payload):
    return json.loads(json.dumps(payload))


def dumped(model, payload):
    """O payload depois de passar pelo modelo, como a API o serializa."""
    return model.model_validate(payload).model_dump(mode="json", exclude_unset=True)


def loose_objects(node, where="#"):
    """Objetos sem propriedades declaradas nem tipo para as chaves extras."""
    if isinstance(node, dict):
        if node.get("type") == "object" and "properties" not in node and node.get("additionalProperties") in (None, True):
            yield where
        if node.get("additionalProperties") is True:
            yield where
        for key, value in node.items():
            yield from loose_objects(value, f"{where}/{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from loose_objects(value, f"{where}[{i}]")


def test_contract_snapshot_is_current():
    assert export_openapi.CONTRACT_PATH.exists(), "rode scripts/export_openapi.py"
    assert export_openapi.CONTRACT_PATH.read_text(encoding="utf-8") == export_openapi.render(export_openapi.schema()), (
        "web/contract/openapi.json desatualizado: rode scripts/export_openapi.py")


def test_front_fixtures_are_current():
    for name, document in export_fixtures.fixtures().items():
        path = export_fixtures.FIXTURES_DIR / f"{name}.json"
        assert path.exists() and path.read_text(encoding="utf-8") == export_fixtures.render(document), (
            f"web/tests/fixtures/{name}.json desatualizado: rode scripts/export_fixtures.py")


# Campos de texto pronto que saíram do payload na fase F5: o texto é de quem apresenta.
REMOVED_TEXT = {
    "payload": {"legend", "empty_message", "account_warning"},
    "meta": {"as_of_label", "data_label", "data_warning"},
    "group": {"label", "empty_message", "next_step"},
    "item": {"client", "value_label", "state", "reason", "explanation", "next_step"},
}


def test_payload_carries_no_ready_made_text(raw_dir):
    dataset = data.load(raw_dir)
    for payload in (views.seller_pipeline(dataset, "Ana Alfa"), views.team_pipeline(dataset)):
        assert not REMOVED_TEXT["payload"] & set(payload)
        assert not REMOVED_TEXT["meta"] & set(payload["meta"])
        for group in payload["groups"]:
            assert not REMOVED_TEXT["group"] & set(group)
            for entry in group["items"]:
                assert not REMOVED_TEXT["item"] & set(entry)
    assert '"deprecated"' not in export_openapi.render(export_openapi.schema())


def test_every_route_answers_with_a_typed_model():
    document = export_openapi.schema()
    for path, item in document["paths"].items():
        for status, response in item["get"]["responses"].items():
            schema = response["content"]["application/json"]["schema"]
            assert "$ref" in schema, (path, status, schema)
    assert list(loose_objects(document)) == []


def test_errors_share_one_body():
    responses = export_openapi.schema()["paths"]["/api/sellers/{seller}/pipeline"]["get"]["responses"]
    assert {status: r["content"]["application/json"]["schema"]["$ref"] for status, r in responses.items() if status != "200"} == {
        status: "#/components/schemas/ErrorBody" for status in ("404", "422", "503")}


def test_payloads_pass_through_the_models_unchanged(raw_dir):
    dataset = data.load(raw_dir)
    for seller in ("Ana Alfa", "Bruno Beta", "Carla Gama"):
        payload = views.seller_pipeline(dataset, seller)
        assert dumped(SellerPipeline, payload) == as_json(payload), seller
    for manager, office in ((None, None), ("Mara Um", None), ("Ninguem", "Marte")):
        payload = views.team_pipeline(dataset, manager, office)
        assert dumped(TeamPipeline, payload) == as_json(payload)
    ctx = views.context(dataset, None)
    assert dumped(Meta, views.meta(dataset, ctx)) == as_json(views.meta(dataset, ctx))
    assert dumped(SellerList, {"sellers": views.sellers(dataset)}) == as_json({"sellers": views.sellers(dataset)})
    assert dumped(Rules, views.rules(dataset)) == as_json(views.rules(dataset))
    assert dumped(Evidence, evidence.load()) == as_json(evidence.load())
    for filters in (intelligence.Filters(), intelligence.Filters(sector="retail"), intelligence.Filters(account="X")):
        payload = intelligence.payload(dataset, filters)
        assert dumped(Intelligence, payload) == as_json(payload)
    for outcome in codes.OUTCOMES:
        payload = intelligence.deals(dataset, outcome=outcome)
        assert dumped(IntelligenceDeals, payload) == as_json(payload)


def test_states_and_actions_flow_from_policy():
    """Grupos e ações do contrato saem da política: um grupo novo em policy.STATES aparece no
    contrato (e quebra os catálogos da tela e da CLI até ganhar texto)."""
    from typing import get_args
    from api import schemas
    assert get_args(schemas.StateKey) == policy.STATES
    assert set(get_args(schemas.SimpleActionCode)) == {codes.CHECK_PROSPECTING, codes.FIX_MISSING_FIELDS}
    assert set(get_args(schemas.AccountActionCode)) == set(codes.ACCOUNT_ACTION_CODES)
    assert {*get_args(schemas.SimpleActionCode), *get_args(schemas.AccountActionCode)} == {
        *policy.NEXT_ACTIONS.values(), codes.FIX_MISSING_FIELDS}
    assert set(get_args(schemas.StartActionCode)) == set(policy.START_ACTION_CODES.values())
    assert set(schemas.Summary.model_fields) == {"total", *policy.STATES, "without_account"}
    assert set(schemas.SellerSummary.model_fields) == {"seller", "total", *policy.STATES, "without_account"}


def test_a_field_without_contract_breaks_validation(raw_dir):
    payload = views.seller_pipeline(data.load(raw_dir), "Ana Alfa")
    payload["groups"][0]["items"][0]["score"] = 1
    with pytest.raises(ValueError, match="score"):
        SellerPipeline.model_validate(payload)


def test_cli_json_is_valid_contract(raw_dir, capsys):
    assert main(["--raw", str(raw_dir), "list", "--seller", "Ana Alfa", "--json"]) == 0
    SellerPipeline.model_validate(json.loads(capsys.readouterr().out))


def test_api_errors_follow_the_error_body(raw_dir):
    client = TestClient(create_app(raw_dir))
    for url, status in ((f"/api/sellers/{quote('Fulano')}/pipeline", 404), ("/api/meta?as_of=31/12/2017", 422)):
        response = client.get(url)
        assert response.status_code == status and set(response.json()) == {"detail", "code", "params"}


@pytest.mark.real_data
@pytest.mark.parametrize("seller", ["Zane Levy", "Darcel Schlecht", "Carl Lin"])
def test_real_payloads_pass_through_the_models_unchanged(real_dataset, seller):
    payload = views.seller_pipeline(real_dataset, seller)
    assert dumped(SellerPipeline, payload) == as_json(payload)
