import hashlib
import json

import pandas as pd
import pytest

from leadscorer import cli_text, codes, data, policy, triage, views
from leadscorer.__main__ import main, render_detail, render_list

from conftest import EDGE_TABLES, PIPELINE, PRODUCTS, opp, write_raw
from test_explain import assert_verifiable, assert_vocabulary

FOCAR_EMPTY_QUALIFICAR = ("Nenhuma aberta há até 106 dias. Comece por Qualificar: verifique no CRM se já houve "
                          "engajamento e registre a data.")
FOCAR_EMPTY_REVISAR = ("Todas as negociações em andamento estão abertas há mais de 138 dias. "
                       "Comece por Confirmar: verifique no CRM quais seguem ativas.")


def ordered(frame, as_of=None):
    opps = triage.order(triage.classify(frame, triage.resolve_context(frame, as_of)))
    return list(zip(opps["opportunity_id"], opps["state"], opps["value_band"]))


def group(payload, key):
    return next(g for g in payload["groups"] if g["state"] == key)


def digest(dataset):
    payloads = [views.seller_pipeline(dataset, seller) for seller in dataset.sellers]
    return hashlib.sha256(json.dumps(payloads, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


@pytest.fixture
def unscorable_dir(tmp_path):
    rows = PIPELINE + [
        opp("N1", "Bruno Beta", "GTX Basic", "Engaging"),          # Engaging sem data
        opp("N2", "Bruno Beta", "", "Prospecting"),                # aberta sem produto
    ]
    return write_raw(tmp_path / "raw", sales_pipeline=rows)


def test_missing_fields_become_unscorable_with_reason(unscorable_dir):  # AC-1.6
    frame = data.load(unscorable_dir).opportunities
    opps = triage.classify(frame, triage.resolve_context(frame)).set_index("opportunity_id")
    assert opps.loc["N1", "state"] == opps.loc["N2", "state"] == policy.NAO_PONTUAVEL
    payload = views.seller_pipeline(data.load(unscorable_dir), "Bruno Beta")
    items = {e["opportunity_id"]: e for e in group(payload, "nao_pontuavel")["items"]}
    assert items["N1"]["missing_field"] == "engage_date"
    assert items["N2"]["missing_field"] == "product"
    assert sum(triage.summary(opps.reset_index()).values()) == len(opps)


def test_unscorable_panel_names_the_field(unscorable_dir):  # AC-3.6
    dataset = data.load(unscorable_dir)
    n1 = views.opportunity_detail(dataset, "N1")["item"]
    n2 = views.opportunity_detail(dataset, "N2")["item"]
    assert n1["reasons"][0]["params"] == {"field": "engage_date"}
    assert n1["next_action"] == {"code": codes.FIX_MISSING_FIELD, "params": {"field": "engage_date"}}
    assert cli_text.reason_text(n1["reasons"][0]) == "Completar porque falta a data de engajamento."
    assert cli_text.action_text(n1["next_action"]) == "Corrija a data de engajamento no CRM."
    assert cli_text.reason_text(n2["reasons"][0]) == "Completar porque falta o produto."
    assert cli_text.action_text(n2["next_action"]) == "Corrija o produto no CRM."
    assert n2["sales_price"] is None and n2["value_band"] is None


def test_unscorable_outputs_stay_verifiable_and_clean(unscorable_dir, capsys):
    dataset = data.load(unscorable_dir)
    payload = views.seller_pipeline(dataset, "Bruno Beta")
    for entry in group(payload, "nao_pontuavel")["items"]:
        assert_verifiable(entry, payload["meta"])
        assert_vocabulary(render_detail({"meta": payload["meta"], "seller": "Bruno Beta", "item": entry}))
    assert_vocabulary(render_list(payload))
    assert main(["--raw", str(unscorable_dir), "list", "--seller", "Bruno Beta"]) == 0
    assert "(sem produto)" in capsys.readouterr().out


def test_catalog_product_without_price_is_unscorable(tmp_path):
    products = [dict(row) for row in PRODUCTS]
    products[0]["sales_price"] = ""                                   # GTX Plus Pro sem preço
    entry = views.opportunity_detail(data.load(write_raw(tmp_path / "raw", products=products)), "EPP")["item"]
    assert (entry["group"], entry["missing_field"]) == (policy.NAO_PONTUAVEL, "sales_price")


def test_account_does_not_change_state_or_order(raw_dir):  # AC-1.7
    frame = data.load(raw_dir).opportunities
    assert ordered(frame.assign(account=frame["account"].fillna("Conta Qualquer"))) == ordered(frame)


def test_shuffled_closed_rows_and_future_win_change_nothing(raw_dir, tmp_path):  # AC-1.10
    rows = [dict(row) for row in reversed(PIPELINE)]
    by_id = {row["opportunity_id"]: row for row in rows}
    by_id["W1"]["opportunity_id"], by_id["L1"]["opportunity_id"] = "L1", "W1"
    for row in rows:
        if row["close_value"]:
            row["close_value"] = str(int(row["close_value"]) * 7 + 3)
    future_win = opp("X1", "Ana Alfa", "GTXPro", "Won", engaged=10, closed=-400)  # fecha depois do as_of
    shuffled = data.load(write_raw(tmp_path / "shuffled", sales_pipeline=rows + [future_win])).opportunities
    base = data.load(raw_dir).opportunities

    ctx = triage.resolve_context(shuffled, "2017-12-31")
    assert (ctx.won_cycle_limit_days, ctx.cycle_limit_days) == (100, 138)  # a ganha futura não entra em L1
    assert ordered(shuffled, "2017-12-31") == ordered(base)


def test_same_input_same_output_hash(raw_dir):  # AC-1.11
    assert digest(data.load(raw_dir)) == digest(data.load(raw_dir))


def test_focar_empty_points_to_next_group(raw_dir):
    payload = views.seller_pipeline(data.load(raw_dir), "Bruno Beta")  # só uma Prospecting
    empty = group(payload, "focar")["empty"]
    assert empty == {"code": codes.START_WITH_GROUP, "params": {
        "group": "qualificar", "action": codes.CHECK_PROSPECTING, "has_engaging": False,
        "won_cycle_limit_days": 100, "cycle_limit_days": 138}}
    assert cli_text.empty_text(empty) == (
        "Nenhuma negociação em andamento. Comece por Qualificar: verifique no CRM se já houve engajamento e registre a data.")


def test_focar_empty_text_cites_only_the_limit_that_matters(tmp_path):
    edges = data.load(write_raw(tmp_path / "edges", **EDGE_TABLES))
    davi = group(views.seller_pipeline(edges, "Davi Delta"), "focar")["empty"]
    assert cli_text.empty_text(davi) == (
        "Nenhuma aberta há até 100 dias. Comece por Acompanhar: consulte no CRM o último registro de cada uma.")
    eva = group(views.seller_pipeline(edges, "Eva Epsilon"), "focar")["empty"]
    assert cli_text.empty_text(eva) == FOCAR_EMPTY_REVISAR


def test_seller_without_open_deals(raw_dir, capsys):  # AC-2.5
    payload = views.seller_pipeline(data.load(raw_dir), "Carla Gama")
    assert payload["summary"] == {"total": 0, "focar": 0, "acompanhar": 0, "revisar": 0, "qualificar": 0,
                                  "nao_pontuavel": 0, "without_account": 0}
    assert payload["empty"] == {"code": codes.NO_OPEN_FOR_SELLER, "params": {}}
    assert main(["--raw", str(raw_dir), "list", "--seller", "Carla Gama"]) == 0
    assert "Nenhuma oportunidade aberta para este vendedor." in capsys.readouterr().out


@pytest.mark.real_data
def test_real_darcel_focar_empty(real_dataset):  # AC-2.4
    payload = views.seller_pipeline(real_dataset, "Darcel Schlecht")
    assert cli_text.empty_text(group(payload, "focar")["empty"]) == FOCAR_EMPTY_QUALIFICAR  # ADR-009
    assert (payload["summary"]["revisar"], payload["summary"]["qualificar"]) == (83, 111)


@pytest.mark.real_data
def test_real_carl_lin_has_no_open_deals(real_dataset):  # AC-2.5
    payload = views.seller_pipeline(real_dataset, "Carl Lin")
    assert payload["summary"]["total"] == 0
    assert payload["empty"]["code"] == codes.NO_OPEN_FOR_SELLER


@pytest.mark.real_data
def test_real_far_as_of_moves_every_engaging_to_revisar(real_dataset):  # AC-2.11
    frame = real_dataset.opportunities
    engaging = frame[frame["deal_stage"] == "Engaging"].groupby("sales_agent").size()
    for seller in real_dataset.sellers:
        payload = views.seller_pipeline(real_dataset, seller, "2030-01-01")
        assert payload["summary"]["focar"] == payload["summary"]["acompanhar"] == 0
        assert payload["summary"]["revisar"] == engaging.get(seller, 0)
        if payload["summary"]["revisar"]:
            expected = FOCAR_EMPTY_QUALIFICAR if payload["summary"]["qualificar"] else FOCAR_EMPTY_REVISAR
            assert cli_text.empty_text(group(payload, "focar")["empty"]) == expected


@pytest.mark.real_data
def test_real_account_and_shuffle_invariance(real_dataset):  # AC-1.7, AC-1.10
    frame = real_dataset.opportunities
    base = ordered(frame)
    assert ordered(frame.assign(account=frame["account"].fillna("Conta Qualquer"))) == base
    shuffled = frame.sample(frac=1, random_state=20260101).reset_index(drop=True)
    closed = shuffled["deal_stage"].isin(policy.CLOSED_STAGES)
    shuffled.loc[closed, "opportunity_id"] = shuffled.loc[closed, "opportunity_id"].sample(
        frac=1, random_state=7).to_numpy()
    future_win = shuffled[closed].iloc[[0]].assign(
        opportunity_id="FUTURO01", deal_stage="Won",
        engage_date=pd.Timestamp("2017-01-01"), close_date=pd.Timestamp("2018-06-30"))
    shuffled = pd.concat([shuffled, future_win], ignore_index=True)
    ctx = triage.resolve_context(shuffled, "2017-12-31")
    assert (ctx.won_cycle_limit_days, ctx.cycle_limit_days) == (106, 138)
    assert ordered(shuffled, "2017-12-31") == base


@pytest.mark.real_data
def test_real_output_is_deterministic(real_dataset):  # AC-1.11
    assert digest(real_dataset) == digest(data.load(policy.RAW_DIR))
