"""Catálogo de textos da CLI (plano do contrato, fase F4).

A CLI monta a saída de `list` e `explain` só com chaves, códigos e números do
payload. Este arquivo confere cobertura dos códigos, vocabulário, a origem de cada
número.
"""
import re

import pytest

from leadscorer import cli_text, codes, data, policy, views
from leadscorer.__main__ import main, render_detail, render_list

from conftest import EDGE_TABLES, PIPELINE, opp, write_raw
from test_explain import assert_vocabulary

NUMBER = re.compile(r"\d{2}/\d{2}/\d{4}|\d{1,3}(?:\.\d{3})+|\d+")


@pytest.fixture
def payloads(raw_dir, tmp_path):
    base = data.load(raw_dir)
    edges = data.load(write_raw(tmp_path / "edges", **EDGE_TABLES))
    return [views.seller_pipeline(dataset, seller) for dataset in (base, edges) for seller in dataset.sellers]


def items(payload):
    return [entry for group in payload["groups"] for entry in group["items"]]


def test_every_contract_code_has_cli_text():
    assert set(cli_text.REASONS) == set(codes.REASON_CODES)
    assert {*cli_text.ACTIONS, *cli_text.ACCOUNT_ACTIONS} == set(codes.ACTION_CODES)
    assert set(cli_text.ACCOUNT_ACTIONS) == set(codes.ACCOUNT_ACTION_CODES)
    assert set(cli_text.EMPTY) == set(codes.EMPTY_CODES)
    assert set(cli_text.START_ACTIONS) == set(policy.START_ACTION_CODES.values())
    assert set(cli_text.GROUP_LABELS) == set(policy.STATES)
    assert set(cli_text.MISSING) == set(policy.MISSING_FIELDS)


def test_fixtures_exercise_every_code(payloads):
    reasons = {r["code"] for p in payloads for e in items(p) for r in e["reasons"]}
    actions = {e["next_action"]["code"] for p in payloads for e in items(p)}
    actions |= {g["next_action"]["code"] for p in payloads for g in p["groups"] if g["next_action"]}
    empty = {g["empty"]["code"] for p in payloads for g in p["groups"] if g["empty"]}
    empty |= {p["empty"]["code"] for p in payloads if p["empty"]}
    assert reasons == set(codes.REASON_CODES)
    assert actions == set(codes.ACTION_CODES)
    assert empty == set(codes.EMPTY_CODES) - {codes.NO_OPEN_FOR_FILTER}  # filtro só existe na visão de time
    starts = {g["empty"]["params"]["group"] for p in payloads for g in p["groups"]
              if g["empty"] and g["empty"]["code"] == codes.START_WITH_GROUP}
    assert starts == {"acompanhar", "revisar", "qualificar"}  # cada destino com o seu texto


def catalog_strings():
    """Todo texto fixo do catálogo da CLI (constantes públicas, inclusive dentro de tuplas e dicionários)."""
    def strings(value):
        if isinstance(value, str):
            yield value
        elif isinstance(value, (tuple, list)):
            for v in value:
                yield from strings(v)
        elif isinstance(value, dict):
            for v in value.values():
                yield from strings(v)
    for name, value in vars(cli_text).items():
        if not name.startswith("_"):
            yield from strings(value)


def test_vocabulary_of_the_catalog_and_of_every_output(payloads):  # AC-3.8 na CLI
    for text in catalog_strings():
        assert_vocabulary(text)
    assert_vocabulary(cli_text.empty_text({"code": codes.NO_OPEN_FOR_FILTER, "params": {}}))
    for payload in payloads:
        assert_vocabulary(render_list(payload))
        for entry in items(payload):
            assert_vocabulary(render_detail({"meta": payload["meta"], "seller": payload["seller"], "item": entry}))


def test_every_number_in_a_reason_comes_from_its_params(payloads):
    for payload in payloads:
        for entry in items(payload):
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


def test_prospecting_explain_says_the_stage(tmp_path, capsys):
    raw = write_raw(tmp_path / "raw", sales_pipeline=PIPELINE + [opp("PE", "Ana Alfa", "GTX Basic", "Prospecting",
                                                                    engaged=40)])
    assert main(["--raw", str(raw), "explain", "--id", "PE"]) == 0
    out = capsys.readouterr().out
    assert "Qualificar porque ainda está em prospecção." in out and "não tem data de engajamento" not in out
