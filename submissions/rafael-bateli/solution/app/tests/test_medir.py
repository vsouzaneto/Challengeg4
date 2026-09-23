import re

import numpy as np

import medir_llm as ml
from motor import llm


def test_interpretar_json_com_lixo_em_volta_e_classe_normalizada():
    txt = 'claro! {"r": [{"id": 1, "classe": "hardware", "confianca": 0.9}, {"id": 2, "classe": "Nada", "confianca": 1}]}'
    r = ml.interpretar(txt)
    assert r[1] == ("Hardware", 0.9)
    assert r[2] == (None, 0.0)
    assert ml.interpretar("sem json") == {}


def test_classificar_troca_de_provedor_quando_a_cota_acaba():
    chamadas = []

    def chamar(prov, msgs, temperatura=0, max_tokens=0, sessao=None):
        chamadas.append(prov)
        if prov == "groq" and len(chamadas) > 1:
            raise llm.ErroLLM("rate_limit", "429", 3600)   # cota do dia acabou
        ids = [int(x) for x in re.findall(r'"id": (\d+)', msgs[1]["content"])]
        return '{"r": [' + ",".join(f'{{"id": {i}, "classe": "Hardware", "confianca": 0.8}}' for i in ids) + "]}", 10

    itens = [(i, f"texto {i}") for i in range(45)]
    res = ml.classificar(itens, ["groq", "gemini"], chamar=chamar, dormir=lambda s: None)
    assert len(res) == 45
    assert sum(r["provedor"] == "groq" for r in res.values()) == 20
    assert sum(r["provedor"] == "gemini" for r in res.values()) == 25


def test_classificar_resposta_ininteligivel_conta_como_erro():
    def chamar(prov, msgs, temperatura=0, max_tokens=0, sessao=None):
        return "não sei", 1

    res = ml.classificar([(1, "a"), (2, "b")], ["groq"], chamar=chamar, dormir=lambda s: None)
    assert res[1]["classe"] is None and res[1]["provedor"] == "groq"


def test_bootstrap_dif_detecta_diferenca_clara():
    a = np.array([1] * 90 + [0] * 10, dtype=bool)
    b = np.array([1] * 60 + [0] * 40, dtype=bool)
    dif, lo, hi = ml.bootstrap_dif(a, b)
    assert abs(dif - 0.30) < 1e-9 and lo > 0.15 and hi < 0.45


def test_avaliar_m1_aplica_o_criterio_pre_registrado():
    ids = list(range(100))
    y = np.array(["A"] * 100)
    prev_mod = np.array(["A"] * 90 + ["B"] * 10)
    res = {i: {"classe": "A" if i < 80 else "B", "confianca": 1 - i / 100, "provedor": "groq",
               "modelo": "m"} for i in ids}
    r = ml.avaliar_m1(ids, res, y, prev_mod, cobertura=0.73)
    linha = r["por_modelo"]["groq · m"]
    assert linha["acerto_llm"] == 0.8 and linha["acerto_supervisionado"] == 0.9
    assert linha["veredito"].startswith("SUPERVISIONADO MANTIDO")
