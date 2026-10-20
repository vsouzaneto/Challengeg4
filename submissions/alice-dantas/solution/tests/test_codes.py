"""Códigos emitidos pelo núcleo (plano do contrato, fase F2).

Os motivos com papel "group" e "order" precisam citar exatamente o que decidiu o
grupo e a ordem; é a garantia que só o back pode dar, já que o texto passa a ser
de quem apresenta.
"""
import re
from typing import get_args
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from api import schemas
from api.main import create_app
from leadscorer import codes, data, explain, policy, views
from leadscorer.errors import DataError

from conftest import EDGE_TABLES, PIPELINE, PRODUCTS, opp, write_raw

OUTCOME_FIELDS = {"close_date", "close_value", "won", "won_value"}
BAND_RANK = {label: i for i, (label, _) in enumerate(policy.VALUE_BANDS)}


def items(payload):
    return [entry for group in payload["groups"] for entry in group["items"]]


def group(payload, key):
    return next(g for g in payload["groups"] if g["state"] == key)


def by_role(entry, role):
    return [r for r in entry["reasons"] if r["role"] == role]


def group_from_reason(reason):
    """Oráculo: o grupo recalculado só com o código e os params do motivo de grupo (regra A)."""
    p = reason["params"]
    if reason["code"] == codes.MISSING_FIELD:
        return "nao_pontuavel"
    if reason["code"] == codes.PROSPECTING_STAGE:
        return "qualificar"
    if reason["code"] == codes.AGE_WITHIN_WON_CYCLE:
        assert p["age_days"] <= p["won_cycle_limit_days"]
        return "focar"
    if reason["code"] == codes.AGE_ABOVE_WON_CYCLE:
        assert p["won_cycle_limit_days"] < p["age_days"] <= p["cycle_limit_days"]
        return "acompanhar"
    assert reason["code"] == codes.AGE_ABOVE_CYCLE_LIMIT and p["age_days"] > p["cycle_limit_days"]
    return "revisar"


def order_key_from_reason(reason):
    """Oráculo: a chave de ordem dentro do grupo só com o motivo de ordem (o ID desempata)."""
    if reason["code"] == codes.LIST_PRICE:
        return BAND_RANK[reason["params"]["value_band"]], -reason["params"]["sales_price"]
    return len(BAND_RANK), 0


def assert_reasons_match_decision(entry, meta):
    """Exatamente um motivo de grupo e um de ordem; só eles reconstroem o grupo e a ordem,
    e os limites citados são os do `meta`."""
    assert [r["role"] for r in entry["reasons"]] == [codes.ROLE_GROUP, codes.ROLE_ORDER]
    reason, price = entry["reasons"]
    assert group_from_reason(reason) == entry["group"]
    for key in ("won_cycle_limit_days", "cycle_limit_days", "percentile"):
        if key in reason["params"]:
            assert reason["params"][key] == meta["cycle_percentile" if key == "percentile" else key]
    if entry["group"] in ("focar", "acompanhar", "revisar"):
        assert reason["params"]["age_days"] == entry["age_days"] and entry["deal_stage"] == "Engaging"
    elif entry["group"] == "qualificar":
        assert entry["deal_stage"] == "Prospecting" and reason["params"] == {"deal_stage": "Prospecting"}
    else:
        assert reason["params"] == {"field": entry["missing_field"]}
    if entry["product"] is None:
        assert (price["code"], price["params"]) == (codes.NO_PRODUCT, {})
    elif entry["sales_price"] is None:
        assert (price["code"], price["params"]) == (codes.NO_LIST_PRICE, {"product": entry["product"]})
    else:
        assert price["code"] == codes.LIST_PRICE
        assert price["params"] == {k: entry[k] for k in ("product", "sales_price", "value_band")}


def assert_order_rebuilt_from_reasons(payload):
    """A ordem dentro de cada grupo sai só dos motivos de ordem e do ID."""
    for g in payload["groups"]:
        keys = [(*order_key_from_reason(e["reasons"][1]), e["opportunity_id"]) for e in g["items"]]
        assert keys == sorted(keys), g["state"]


def assert_actions(payload):
    for g in payload["groups"]:
        assert (g["next_action"] is None) == (not g["items"]) == (g["empty"] is not None), g["state"]
        for entry in g["items"]:
            expected = (explain._action(codes.FIX_MISSING_FIELD, field=entry["missing_field"])
                        if entry["group"] == "nao_pontuavel" else
                        explain._verification(policy.NEXT_ACTIONS[entry["group"]], entry["account"] is not None))
            assert entry["next_action"] == expected
        if g["items"]:
            assert g["next_action"] == explain.group_next_action(g["state"])


def assert_ordering(payload):
    """`ordering` descreve a ordem real dos itens."""
    ordering = payload["ordering"]
    assert ordering == {"group_order": list(policy.STATES),
                        "within_group": ["value_band", "sales_price_desc", "opportunity_id"],
                        "age_affects_order": False}
    assert [g["state"] for g in payload["groups"]] == ordering["group_order"]
    for g in payload["groups"]:
        keys = [(BAND_RANK.get(e["value_band"], len(BAND_RANK)), -(e["sales_price"] or 0), e["opportunity_id"])
                for e in g["items"]]
        assert keys == sorted(keys), g["state"]


def assert_no_outcome(payload):
    """O que decide (grupo, ordem, ação) não cita o desfecho da oportunidade."""
    for entry in items(payload):
        deciding = by_role(entry, codes.ROLE_GROUP) + by_role(entry, codes.ROLE_ORDER) + [entry["next_action"]]
        for coded in deciding:
            assert not OUTCOME_FIELDS & set(coded["params"]), coded
        assert entry["deal_stage"] in policy.OPEN_STAGES


def check_payload(payload):
    meta = payload["meta"]
    assert meta["contract_version"] == codes.CONTRACT_VERSION
    for entry in items(payload):
        assert entry["group"] in policy.STATES
        assert_reasons_match_decision(entry, meta)
    assert_order_rebuilt_from_reasons(payload)
    assert_actions(payload)
    assert_ordering(payload)
    assert_no_outcome(payload)
    assert payload["summary"]["without_account"] == sum(e["account"] is None for e in items(payload))


@pytest.fixture
def dataset(raw_dir):
    return data.load(raw_dir)


def test_every_seller_payload_cites_what_decided(dataset):
    for seller in dataset.sellers:
        check_payload(views.seller_pipeline(dataset, seller))
    check_payload(views.team_pipeline(dataset))


def test_unscorable_items_name_the_missing_field(tmp_path):
    rows = PIPELINE + [opp("N1", "Bruno Beta", "GTX Basic", "Engaging"), opp("N2", "Bruno Beta", "", "Prospecting")]
    dataset = data.load(write_raw(tmp_path / "raw", sales_pipeline=rows))
    payload = views.seller_pipeline(dataset, "Bruno Beta")
    check_payload(payload)
    found = {e["opportunity_id"]: e for e in group(payload, "nao_pontuavel")["items"]}
    assert found["N1"]["next_action"] == {"code": codes.FIX_MISSING_FIELD, "params": {"field": "engage_date"}}
    assert found["N2"]["reasons"][1] == {"code": codes.NO_PRODUCT, "role": codes.ROLE_ORDER, "params": {}}
    assert group(payload, "nao_pontuavel")["next_action"] == {"code": codes.FIX_MISSING_FIELDS, "params": {}}


def test_prospecting_with_engage_date_stays_qualificar_and_the_reason_holds(tmp_path):
    rows = PIPELINE + [opp("PE", "Ana Alfa", "GTX Basic", "Prospecting", engaged=40)]
    payload = views.seller_pipeline(data.load(write_raw(tmp_path / "raw", sales_pipeline=rows)), "Ana Alfa")
    entry = next(e for e in items(payload) if e["opportunity_id"] == "PE")
    assert entry["group"] == "qualificar" and entry["age_days"] == 40
    assert entry["reasons"][0]["code"] == codes.PROSPECTING_STAGE


def test_empty_states_are_codes(dataset):
    bruno = views.seller_pipeline(dataset, "Bruno Beta")  # só uma Prospecting
    assert group(bruno, "focar")["empty"] == {"code": codes.START_WITH_GROUP, "params": {
        "group": "qualificar", "action": codes.CHECK_PROSPECTING, "has_engaging": False,
        "won_cycle_limit_days": 100, "cycle_limit_days": 138}}
    carla = views.seller_pipeline(dataset, "Carla Gama")  # sem abertas
    assert carla["empty"] == {"code": codes.NO_OPEN_FOR_SELLER, "params": {}}
    assert all(g["empty"] == {"code": codes.GROUP_EMPTY, "params": {}} for g in carla["groups"])
    nobody = views.team_pipeline(dataset, manager="Ninguem")
    assert nobody["empty"] == {"code": codes.NO_OPEN_FOR_FILTER, "params": {}}
    assert views.seller_pipeline(dataset, "Ana Alfa")["empty"] is None


def literals(annotation, field="code"):
    """Valores de `field` em cada modelo de uma união discriminada."""
    union = get_args(annotation)[0]
    return {value for model in get_args(union) for value in get_args(model.model_fields[field].annotation)}


def test_focar_empty_points_to_acompanhar_or_revisar(tmp_path):
    edges = data.load(write_raw(tmp_path / "edges", **EDGE_TABLES))
    for seller, start, action in (("Davi Delta", "acompanhar", codes.CHECK_PROGRESS),
                                  ("Eva Epsilon", "revisar", codes.CONFIRM_STILL_ACTIVE)):
        payload = views.seller_pipeline(edges, seller)
        check_payload(payload)
        assert group(payload, "focar")["empty"]["params"] == {
            "group": start, "action": action, "has_engaging": True, "won_cycle_limit_days": 100,
            "cycle_limit_days": 138}


def test_codes_and_schema_list_the_same_values():
    assert literals(schemas.Reason) == set(codes.REASON_CODES)
    assert literals(schemas.NextAction) == set(codes.ACTION_CODES)
    assert literals(schemas.GroupEmptyState) | set(get_args(schemas.PipelineEmpty.model_fields["code"].annotation)) == \
        set(codes.EMPTY_CODES)
    assert set(get_args(schemas.ErrorCode)) == set(codes.ERROR_CODES)
    assert literals(schemas.Reason, "role") == set(codes.ROLES)
    assert get_args(schemas.RankerCode) == codes.RANKER_CODES


def test_intelligence_codes_and_schema_list_the_same_values():
    assert literals(schemas.Diagnostic) == set(codes.DIAGNOSTIC_CODES)
    assert literals(schemas.Finding) == set(codes.FINDING_CODES)
    empties = {get_args(m.model_fields["code"].annotation)[0] for m in (schemas.HistoryEmpty, schemas.DealsEmpty)}
    assert empties == set(codes.INTELLIGENCE_EMPTY_CODES) and not empties & set(codes.EMPTY_CODES)
    assert get_args(schemas.Dimension) == codes.DIMENSIONS
    assert get_args(schemas.DealOutcome) == codes.OUTCOMES
    assert get_args(schemas.ChanceVerdict) == codes.CHANCE_VERDICTS
    assert get_args(schemas.Driver) == codes.DRIVERS
    assert get_args(schemas.SegmentOrder) == codes.SEGMENT_ORDERS


def test_every_error_raised_by_the_core_has_a_contract_code():
    used = set()
    for path in (policy.SOLUTION_DIR / "leadscorer").glob("*.py"):
        used |= set(re.findall(r"code=codes\.([A-Z_]+)", path.read_text(encoding="utf-8")))
    assert used and {getattr(codes, name) for name in used} == set(codes.ERROR_CODES)


def test_api_errors_carry_code_and_params(raw_dir, tmp_path):
    client = TestClient(create_app(raw_dir))
    cases = [
        (f"/api/sellers/{quote('Fulano')}/pipeline", 404, codes.SELLER_NOT_FOUND, {"seller": "Fulano"}),
        ("/api/meta?as_of=31/12/2017", 422, codes.INVALID_AS_OF_FORMAT,
         {"value": "31/12/2017", "minimum": "2017-12-31"}),
        ("/api/meta?as_of=2017-01-01", 422, codes.AS_OF_BEFORE_LAST_CLOSE,
         {"value": "2017-01-01", "minimum": "2017-12-31"}),
        ("/api/intelligence/deals?outcome=ganhas", 422, codes.INVALID_PARAMETER,
         {"name": "outcome", "value": "ganhas", "allowed": list(codes.OUTCOMES)}),
        ("/api/intelligence/deals?outcome=open&group=focus", 422, codes.INVALID_PARAMETER,
         {"name": "group", "value": "focus", "allowed": list(policy.STATES)}),
    ]
    for url, status, code, params in cases:
        response = client.get(url)
        assert (response.status_code, response.json()["code"], response.json()["params"]) == (status, code, params)
        schemas.ErrorBody.model_validate(response.json())
    raw = write_raw(tmp_path / "raw")
    (raw / "products.csv").unlink()
    body = TestClient(create_app(raw)).get("/api/sellers").json()
    assert (body["code"], body["params"]["files"]) == (codes.DATA_FILE_MISSING, ["products.csv"])
    schemas.ErrorBody.model_validate(body)


def test_data_errors_carry_the_offending_values(tmp_path):
    rows = PIPELINE + [opp("U1", "Ana Alfa", "GTX Ultra", "Engaging", engaged=5)]
    with pytest.raises(DataError) as error:
        data.load(write_raw(tmp_path / "raw", sales_pipeline=rows))
    assert error.value.code == codes.DATA_UNKNOWN_LABEL
    assert error.value.params == {"table": "sales_pipeline", "column": "product", "labels": ["GTX Ultra"], "ids": ["U1"]}
    duplicated = write_raw(tmp_path / "dup", products=PRODUCTS + PRODUCTS[:1])
    with pytest.raises(DataError) as error:
        data.load(duplicated)
    assert (error.value.code, error.value.params["values"]) == (codes.DATA_DUPLICATE_KEY, ["GTX Plus Pro"])


@pytest.mark.real_data
def test_real_every_item_cites_what_decided(real_dataset):
    payload = views.team_pipeline(real_dataset)
    assert payload["summary"]["total"] == 2089
    check_payload(payload)
    schemas.TeamPipeline.model_validate(payload)


@pytest.mark.real_data
def test_real_empty_states(real_dataset):
    darcel = views.seller_pipeline(real_dataset, "Darcel Schlecht")
    assert group(darcel, "focar")["empty"] == {"code": codes.START_WITH_GROUP, "params": {
        "group": "qualificar", "action": codes.CHECK_PROSPECTING, "has_engaging": True,
        "won_cycle_limit_days": 106, "cycle_limit_days": 138}}
    sellers = [views.seller_pipeline(real_dataset, s) for s in real_dataset.sellers]
    starts = [group(p, "focar")["empty"]["params"]["group"] for p in sellers
              if group(p, "focar")["empty"] and group(p, "focar")["empty"]["code"] == codes.START_WITH_GROUP]
    assert starts == ["qualificar"] * 10  # 10 sem Focar entre os 27 com Engaging; todos têm Qualificar (ADR-009)
    assert views.seller_pipeline(real_dataset, "Carl Lin")["empty"]["code"] == codes.NO_OPEN_FOR_SELLER
    assert views.seller_pipeline(real_dataset, "Zane Levy")["summary"]["without_account"] == 59
