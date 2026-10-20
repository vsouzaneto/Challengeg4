"""'Por que está aqui' como dado (P0-3) e o texto da CLI montado a partir dele.

O núcleo entrega motivos e próximo passo em código; os testes conferem os valores
de cada código contra os dados (AC-3.7) e, onde importa a redação, o texto que a
CLI monta (`cli_text`). O texto da tela é testado no front (web/tests/copy.test.ts).
"""
import re

import pytest

from leadscorer import cli_text, codes, data, policy, triage, views
from leadscorer.__main__ import main, render_detail, render_list

NUMBER = re.compile(r"\d{2}/\d{2}/\d{4}|\d{1,3}(?:\.\d{3})+|\d+")
BAND_WORD = re.compile(r"\b(alt[oa]|médi[oa]|baix[oa])\b", re.IGNORECASE)


def context(dataset):
    return triage.resolve_context(dataset.opportunities)


def detail(dataset, opportunity_id):
    return views.opportunity_detail(dataset, opportunity_id)["item"]


def texts(item):
    """As frases que a CLI mostra para os motivos do item."""
    return [cli_text.reason_text(reason) for reason in item["reasons"]]


def all_items(dataset):
    sellers = sorted(dataset.opportunities["sales_agent"].unique())
    payloads = [views.seller_pipeline(dataset, seller) for seller in sellers]
    return payloads, [entry for p in payloads for g in p["groups"] for entry in g["items"]]


def assert_verifiable(entry, meta):  # AC-3.7
    """Exatamente dois motivos (grupo e ordem), com os valores do item e do `meta`, e todo
    número do texto vem dos parâmetros."""
    group_reason, order_reason = entry["reasons"]
    params = group_reason["params"]
    if entry["group"] in (policy.FOCAR, policy.ACOMPANHAR, policy.REVISAR):
        assert params["age_days"] == entry["age_days"]
        assert params["cycle_limit_days" if entry["group"] == policy.REVISAR else "won_cycle_limit_days"] == (
            meta["cycle_limit_days"] if entry["group"] == policy.REVISAR else meta["won_cycle_limit_days"])
    if order_reason["code"] == codes.LIST_PRICE:
        assert order_reason["params"]["sales_price"] == entry["sales_price"]
    for reason in entry["reasons"]:
        text, allowed = cli_text.reason_text(reason), set()
        for value in reason["params"].values():
            if isinstance(value, bool):
                continue
            if isinstance(value, int):
                allowed |= {str(value), cli_text.fmt_int(value)}
            elif isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                allowed.add(cli_text.iso_date(value))
            elif isinstance(value, str):
                text = text.replace(value, " ")  # números dentro de um nome (ex.: "GTK 500")
        for number in NUMBER.findall(text):
            assert number in allowed, (number, text)


def assert_vocabulary(text):  # AC-3.8
    """Nenhuma palavra começa por um termo proibido (por início de palavra: "comparado" passa)."""
    lowered = text.lower()
    for term in policy.FORBIDDEN_TERMS:
        assert not re.search(r"(?<!\w)" + re.escape(term), lowered), (term, text)
    for match in BAND_WORD.finditer(text):
        assert lowered[:match.start()].endswith("de tabela "), (match.group(), text)


def test_vocabulary_matches_the_start_of_a_word():
    assert_vocabulary("Comparado à regra atual, separadas por grupo.")
    for text in ("Negociação parada", "prazo de 106 dias", "Venceu ontem", "Atrasadas", "chance zero"):
        with pytest.raises(AssertionError):
            assert_vocabulary(text)


def test_focar_acompanhar_and_revisar_reasons(raw_dir):
    dataset = data.load(raw_dir)
    focar = detail(dataset, "E100")
    assert focar["reasons"][0] == {"code": codes.AGE_WITHIN_WON_CYCLE, "role": codes.ROLE_GROUP, "params": {
        "age_days": 100, "won_cycle_limit_days": 100, "percentile": 90}}
    assert texts(focar)[0] == "Focar porque está aberta há 100 dias. Entre as vendas ganhas, 90% fecharam em até 100 dias."
    acompanhar = detail(dataset, "E138")
    assert acompanhar["reasons"][0] == {"code": codes.AGE_ABOVE_WON_CYCLE, "role": codes.ROLE_GROUP, "params": {
        "age_days": 138, "won_cycle_limit_days": 100, "cycle_limit_days": 138, "percentile": 90}}
    assert texts(acompanhar)[0] == ("Acompanhar porque está aberta há 138 dias: mais do que 90% das vendas ganhas "
                                    "levaram (100 d), sem passar da venda mais longa já fechada (138 d).")
    assert acompanhar["next_action"]["code"] == codes.CHECK_PROGRESS
    revisar = detail(dataset, "E139")  # AC-3.2
    assert revisar["reasons"][0] == {"code": codes.AGE_ABOVE_CYCLE_LIMIT, "role": codes.ROLE_GROUP, "params": {
        "age_days": 139, "cycle_limit_days": 138}}
    assert texts(revisar)[0] == ("Confirmar porque está aberta há 139 dias, mais do que qualquer venda já "
                                 "fechada aqui (138 d).")
    assert revisar["next_action"]["code"] == codes.CONFIRM_STILL_ACTIVE
    shown = render_detail({"meta": views.meta(dataset, context(dataset)), "seller": "Ana Alfa", "item": revisar})
    assert "verifique no crm se" in shown.lower()
    assert "o tempo aberta não prova que ela terminou" in shown.lower()
    assert cli_text.LIMITS_NOTE in shown
    assert_vocabulary(shown)


def test_prospecting_has_no_invented_age(raw_dir):
    entry = detail(data.load(raw_dir), "P1")
    assert entry["reasons"][0]["code"] == codes.PROSPECTING_STAGE
    assert texts(entry)[0] == "Qualificar porque ainda está em prospecção."
    assert entry["age_days"] is None
    assert entry["next_action"]["code"] == codes.CHECK_PROSPECTING


def test_only_what_decided_is_a_reason(raw_dir):  # AC-3.7: sem motivos de contexto
    _, items = all_items(data.load(raw_dir))
    assert {tuple(r["role"] for r in entry["reasons"]) for entry in items} == {(codes.ROLE_GROUP, codes.ROLE_ORDER)}
    meta = views.meta(data.load(raw_dir), context(data.load(raw_dir)))
    assert set(meta) == {"as_of", "won_cycle_median_days", "won_cycle_limit_days", "cycle_limit_days",
                         "cycle_percentile", "audited", "contract_version"}


def test_fixture_reasons_are_verifiable_and_clean(raw_dir):
    payloads, _ = all_items(data.load(raw_dir))
    for payload in payloads:
        for entry in (e for g in payload["groups"] for e in g["items"]):
            assert_verifiable(entry, payload["meta"])
            assert_vocabulary(render_detail({"meta": payload["meta"], "seller": payload["seller"], "item": entry}))
        assert_vocabulary(render_list(payload))


def test_cli_explain_and_unknown_id(raw_dir, capsys):
    assert main(["--raw", str(raw_dir), "explain", "--id", "E138"]) == 0
    out = capsys.readouterr().out
    assert "Por que está aqui" in out and "O que verificar agora:" in out
    assert main(["--raw", str(raw_dir), "explain", "--id", "NAOEXISTE"]) == 1
    assert "não encontrada" in capsys.readouterr().err


@pytest.mark.real_data
def test_real_focar_panel_01XZ9CRY(real_dataset):  # AC-3.1
    entry = detail(real_dataset, "01XZ9CRY")
    assert entry["reasons"][0]["params"] == {"age_days": 104, "won_cycle_limit_days": 106, "percentile": 90}
    sentences = texts(entry)
    assert sentences[0] == "Focar porque está aberta há 104 dias. Entre as vendas ganhas, 90% fecharam em até 106 dias."
    assert "valor de tabela 5.482 (valor de tabela alto)" in sentences[1].lower()
    assert len(sentences) == 2
    assert entry["next_action"] == {"code": codes.CHECK_STATUS, "params": {"has_account": True}}
    assert cli_text.action_text(entry["next_action"], entry["account"]) == (
        "Consulte no CRM o andamento da negociação com Initech.")


@pytest.mark.real_data
def test_real_acompanhar_panel_J0G6ZLYZ(real_dataset):
    entry = detail(real_dataset, "J0G6ZLYZ")
    assert (entry["group"], entry["age_days"]) == (policy.ACOMPANHAR, 120)
    assert entry["reasons"][0]["params"] == {"age_days": 120, "won_cycle_limit_days": 106, "cycle_limit_days": 138,
                                             "percentile": 90}


@pytest.mark.real_data
def test_real_qualificar_panel_28EJ0L9T(real_dataset):  # AC-3.3
    entry = detail(real_dataset, "28EJ0L9T")
    assert (entry["product"], entry["account"], entry["age_days"]) == ("GTX Plus Pro", None, None)
    assert entry["reasons"][0] == {"code": codes.PROSPECTING_STAGE, "role": codes.ROLE_GROUP,
                                   "params": {"deal_stage": "Prospecting"}}
    assert texts(entry)[0] == "Qualificar porque ainda está em prospecção."
    assert cli_text.action_text(entry["next_action"]) == (
        "Em prospecção, sem data de início: verifique no CRM se já houve engajamento e registre a data quando "
        "houver.")


@pytest.mark.real_data
def test_real_2089_reasons_verifiable_and_clean(real_dataset):  # AC-3.7, AC-3.8
    payloads, items = all_items(real_dataset)
    assert len(items) == 2089
    for payload in payloads:
        meta = payload["meta"]
        for group in payload["groups"]:
            for entry in group["items"]:
                assert_verifiable(entry, meta)
                assert_vocabulary(render_detail({"meta": meta, "seller": payload["seller"], "item": entry}))
        assert_vocabulary(render_list(payload))


def test_cli_detail_has_suggestions_by_scenario_and_the_new_notice(raw_dir):
    dataset = data.load(raw_dir)
    meta = views.meta(dataset, context(dataset))
    without_account = detail(dataset, "EPP")  # Focar, sem conta registrada
    shown = render_detail({"meta": meta, "seller": "Ana Alfa", "item": without_account})
    assert cli_text.SUGGESTIONS_TITLE in shown and cli_text.SUGGESTIONS_INTRO in shown
    assert "Se já houve contato recente: retome de onde parou e registre o avanço no CRM." in shown
    assert "Se a conta não está registrada: consulte no CRM quem é a conta antes de contatar." in shown
    assert cli_text.LIMITS_NOTE in shown and shown.index(cli_text.SUGGESTIONS_TITLE) < shown.index(cli_text.LIMITS_NOTE)
    assert_vocabulary(shown)
    with_account = detail(dataset, "EGP")
    assert not any("conta não está registrada" in text for text in cli_text.suggestions_for(with_account))
    assert all(cli_text.suggestions_for(detail(dataset, entry_id)) for entry_id in ("E101", "E139", "P1"))
    assert set(cli_text.SUGGESTIONS) == set(policy.STATES)
