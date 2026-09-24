"""Testes do modulo Suporte (desafio 002) com os dados reais do desafio."""
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "app"))

from nucleo import leitura  # noqa: E402
from nucleo.carregar import tabelas_da_sessao  # noqa: E402
from nucleo.contratos import MODULOS, mapeamento_desafio  # noqa: E402
from modulos.suporte import relatorio  # noqa: E402
from modulos.suporte.analise import Premissas, analisar, decidir  # noqa: E402

PASTA = leitura.pasta_dados_desafio()
pytestmark = pytest.mark.skipif(PASTA is None, reason="dados do desafio ausentes")
M = MODULOS["suporte"]


@pytest.fixture(scope="module")
def r(tmp_path_factory):
    os.environ["G4_SESSOES"] = str(tmp_path_factory.mktemp("sess"))
    s = {"modulo": "suporte", "arquivos": {t.nome: os.path.join(PASTA, t.arquivo_desafio) for t in M.tabelas},
         "mapeamento": mapeamento_desafio(M)}
    return analisar(tabelas_da_sessao(s))


def test_usa_os_dois_datasets(r):
    assert r["volume"]["total"] == 8469
    assert r["classificador"]["n_teste"] + r["classificador"]["n_treino"] == 47837


def test_regra_de_duracao_so_positiva(r):
    assert r["info"]["n_duracao_valida"] == 1402
    assert (r["chamados"].duracao_h.dropna() > 0).all()


def test_classificador_bate_a_linha_de_base(r):
    comp = r["classificador"]["comparacao"]
    assert r["classificador"]["acuracia"] > 0.8
    assert r["classificador"]["acuracia"] > comp.iloc[2]["acurácia"] + 0.4   # muito acima do chute


def test_faixa_automatica_e_mais_precisa(r):
    f = r["automacao"]["faixas"].set_index("faixa")
    assert f.loc["Automático", "acerto_%"] > 95
    assert f.loc["Automático", "acerto_%"] > f.loc["Direto para humano", "acerto_%"]


def test_nunca_automatiza_cancelamento_e_critico(r):
    p = r["premissas"]
    texto = "VPN access not working please reset my password"
    assert decidir(texto, r["classificador"], p, tipo="Refund request")["decisao"] == "Direto para humano"
    assert decidir(texto, r["classificador"], p, prioridade="Critical")["decisao"] == "Direto para humano"


def test_exemplos_reais_do_nao_automatizar(r):
    assert len(r["exemplos"]) >= 3 and all(len(v) for v in r["exemplos"].values())


def test_texto_do_ds1_nao_tem_sinal(r):
    s = r["sinal_ds1"]
    assert abs(s["acuracia"] - s["acaso"]) < 0.05


def test_premissa_de_custo_recalcula(r):
    tabs = {"chamados": r["chamados"]}
    a = analisar(tabs, Premissas(custo_hora=50), clf=r["classificador"])
    b = analisar(tabs, Premissas(custo_hora=100), clf=r["classificador"])
    assert b["desperdicio"]["custo_medido"] == pytest.approx(2 * a["desperdicio"]["custo_medido"])


def test_relatorios(r):
    assert "Resumo executivo" in relatorio.markdown(r, "T")
    assert relatorio.pdf(r, "T")[:4] == b"%PDF"
