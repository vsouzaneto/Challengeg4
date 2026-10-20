import json

import pytest

from leadscorer import cli_text, codes, data, policy, views
from leadscorer.__main__ import main

from conftest import EDGE_TABLES, write_raw

LEGEND = (
    "Ordem: Focar → Qualificar → Acompanhar → Confirmar → Completar. Em cada grupo, maior "
    "valor de tabela primeiro. A idade aparece, mas não muda a ordem."
)


def group(payload, key):
    return next(g for g in payload["groups"] if g["state"] == key)


def test_summary_header_and_account_warning(raw_dir):
    payload = views.seller_pipeline(data.load(raw_dir), "Ana Alfa")
    assert payload["summary"] == {"total": 8, "focar": 5, "acompanhar": 2, "revisar": 1, "qualificar": 0,
                                  "nao_pontuavel": 0, "without_account": 5}
    assert payload["meta"]["as_of"] == "2017-12-31"
    # O payload traz os dados; a frase é de quem apresenta (aqui, a CLI).
    assert cli_text.data_label(payload["meta"]) == "Dados até 31/12/2017"
    assert cli_text.legend_text(payload["ordering"]) == LEGEND
    assert cli_text.account_warning(payload["summary"]) == "5 de 8 sem cliente registrado"


def test_every_item_is_identifiable_without_account(raw_dir):  # AC-2.7
    payload = views.seller_pipeline(data.load(raw_dir), "Ana Alfa")
    items = [entry for g in payload["groups"] for entry in g["items"]]
    assert all(entry["opportunity_id"] and entry["product"] and entry["engage_date"] for entry in items)
    no_account = [entry for entry in items if entry["account"] is None]
    assert no_account and all(cli_text.client_text(entry) == "sem cliente registrado" for entry in no_account)


def test_engaging_groups_show_age(raw_dir):
    payload = views.seller_pipeline(data.load(raw_dir), "Ana Alfa")
    ages = {e["opportunity_id"]: e["age_days"] for k in ("focar", "acompanhar", "revisar")
            for e in group(payload, k)["items"]}
    assert (ages["E100"], ages["E101"], ages["E138"], ages["E139"]) == (100, 101, 138, 139)


def test_empty_group_has_message(raw_dir):
    qualificar = group(views.seller_pipeline(data.load(raw_dir), "Ana Alfa"), "qualificar")
    assert qualificar["items"] == [] and qualificar["empty"] == {"code": codes.GROUP_EMPTY, "params": {}}


def test_cli_text_has_header_legend_and_one_warning(raw_dir, capsys):
    assert main(["--raw", str(raw_dir), "list", "--seller", "Ana Alfa"]) == 0
    out = capsys.readouterr().out
    assert "Dados até 31/12/2017" in out and LEGEND in out
    assert sum(line.startswith("Nota:") for line in out.splitlines()) == 1
    assert "2 oportunidades empatadas (GTX Basic, 550): sem ordem entre si" in out
    assert "%" not in out


def test_cli_json_is_the_payload(raw_dir, capsys):
    assert main(["--raw", str(raw_dir), "list", "--seller", "Ana Alfa", "--json"]) == 0
    expected = json.loads(json.dumps(views.seller_pipeline(data.load(raw_dir), "Ana Alfa")))
    assert json.loads(capsys.readouterr().out) == expected


@pytest.mark.real_data
def test_zane_levy_focus_list(real_dataset):  # AC-2.1
    payload = views.seller_pipeline(real_dataset, "Zane Levy")
    assert payload["summary"] == {"total": 88, "focar": 13, "acompanhar": 18, "revisar": 57, "qualificar": 0,
                                  "nao_pontuavel": 0, "without_account": 59}
    assert cli_text.account_warning(payload["summary"]) == "59 de 88 sem cliente registrado"
    focar = group(payload, "focar")["items"]
    assert [e["value_band"] for e in focar] == ["alto"] * 4 + ["médio"] * 7 + ["baixo"] * 2
    assert [e["opportunity_id"] for e in focar[:focar[0]["tie_size"]]] == ["01XZ9CRY", "FZWU2I30"]
    keys = [(-e["sales_price"], e["opportunity_id"]) for e in focar]
    assert keys == sorted(keys)
    assert focar[0]["opportunity_id"] == "01XZ9CRY" and focar[0]["age_days"] == 104


def test_team_by_seller_is_alphabetical_with_zero_open_and_adds_up(raw_dir):  # AC-2.9, AC-4.6
    dataset = data.load(raw_dir)
    payload = views.team_pipeline(dataset)
    rows = payload["by_seller"]
    assert [r["seller"] for r in rows] == ["Ana Alfa", "Bruno Beta", "Carla Gama"]
    assert rows[2] == {"seller": "Carla Gama", "total": 0, "focar": 0, "acompanhar": 0, "revisar": 0,
                       "qualificar": 0, "nao_pontuavel": 0, "without_account": 0}
    for key, value in payload["summary"].items():
        assert sum(r[key] for r in rows) == value, key
    for row in rows:
        assert row == {"seller": row["seller"], **views.seller_pipeline(dataset, row["seller"])["summary"]}


def test_team_by_seller_follows_the_filter(raw_dir):
    dataset = data.load(raw_dir)
    assert [r["seller"] for r in views.team_pipeline(dataset, manager="Mara Um")["by_seller"]] == [
        "Ana Alfa", "Bruno Beta"]
    east = views.team_pipeline(dataset, office="East")
    assert east["empty"] == {"code": codes.NO_OPEN_FOR_FILTER, "params": {}}
    assert [(r["seller"], r["total"]) for r in east["by_seller"]] == [("Carla Gama", 0)]
    assert views.team_pipeline(dataset, manager="Ninguem")["by_seller"] == []


def test_rules_are_the_policy(raw_dir):  # AC-4.6
    dataset = data.load(raw_dir)
    rules = views.rules(dataset)
    assert rules["ordering"] == views.ordering()
    assert rules["meta"] == views.meta(dataset, views.context(dataset, None))
    assert rules["value_bands"] == [{"band": "alto", "min_price": 3000, "max_price": None},
                                    {"band": "médio", "min_price": 500, "max_price": 2999},
                                    {"band": "baixo", "min_price": 0, "max_price": 499}]
    # Cada item cai na faixa que as regras descrevem.
    bands = {b["band"]: b for b in rules["value_bands"]}
    for group_ in views.team_pipeline(dataset)["groups"]:
        for entry in group_["items"]:
            if entry["sales_price"] is not None:
                band = bands[entry["value_band"]]
                assert band["min_price"] <= entry["sales_price"] <= (band["max_price"] or entry["sales_price"])


def assert_same_policy_everywhere(dataset):
    """A mesma política em todas as saídas: a carteira da equipe, a lista do vendedor, o detalhe
    e as regras usam a mesma classificação, ordem, motivos e `meta`."""
    team = views.team_pipeline(dataset)
    team_items = [entry for g in team["groups"] for entry in g["items"]]
    assert team["ordering"]["group_order"] == list(policy.STATES)
    assert views.rules(dataset)["meta"] == team["meta"]
    by_seller = {row["seller"]: row for row in team["by_seller"]}
    for seller in dataset.sellers:
        payload = views.seller_pipeline(dataset, seller)
        assert payload["meta"] == team["meta"]
        assert by_seller[seller] == {"seller": seller, **payload["summary"]}
        own = [entry for g in payload["groups"] for entry in g["items"]]
        in_team = [entry for entry in team_items if entry["sales_agent"] == seller]
        strip = lambda e: {k: v for k, v in e.items() if k != "tie_size"}  # o empate conta a lista inteira
        assert [strip(e) for e in in_team] == [strip(e) for e in own], seller
        for entry in own[:3]:
            assert views.opportunity_detail(dataset, entry["opportunity_id"])["item"] == entry


def test_same_policy_everywhere(raw_dir, tmp_path):
    assert_same_policy_everywhere(data.load(raw_dir))
    assert_same_policy_everywhere(data.load(write_raw(tmp_path / "edges", **EDGE_TABLES)))


@pytest.mark.real_data
def test_real_same_policy_everywhere(real_dataset):
    assert_same_policy_everywhere(real_dataset)


@pytest.mark.real_data
def test_real_team_by_seller_lists_all_35_sellers(real_dataset):
    rows = views.team_pipeline(real_dataset)["by_seller"]
    assert [r["seller"] for r in rows] == sorted(real_dataset.sellers) and len(rows) == 35
    assert sum(r["total"] == 0 for r in rows) == 8
    assert sum(r["total"] for r in rows) == 2089
