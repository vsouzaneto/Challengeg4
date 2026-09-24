"""Testes do modulo Churn (desafio 001) com os dados reais do desafio."""
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "app"))

from nucleo import leitura, sessoes  # noqa: E402
from nucleo.carregar import tabelas_da_sessao  # noqa: E402
from nucleo.contratos import MODULOS, mapeamento_desafio  # noqa: E402
from modulos.churn import relatorio  # noqa: E402
from modulos.churn.analise import NIVEL_EVIDENCIA, Premissas, analisar  # noqa: E402

PASTA = leitura.pasta_dados_desafio()
pytestmark = pytest.mark.skipif(PASTA is None, reason="dados do desafio ausentes")
M = MODULOS["churn"]


@pytest.fixture(scope="module")
def tabs():
    s = {"modulo": "churn", "arquivos": {t.nome: os.path.join(PASTA, t.arquivo_desafio) for t in M.tabelas},
         "mapeamento": mapeamento_desafio(M)}
    return tabelas_da_sessao(s)


@pytest.fixture(scope="module")
def r(tabs):
    return analisar(tabs)


def test_numeros_base_conferidos(r):
    b = r["base"]
    assert (b["clientes"], b["canceladas"]) == (500, 110)
    assert round(b["taxa_churn"], 3) == 0.22
    assert b["mrr_perdido"] == 254952          # MRR da ultima assinatura, sem duplicar


def test_motivos_somam_as_canceladas(r):
    assert r["motivos"].contas.sum() == 110


def test_sinais_medidos_antes_da_data_de_referencia(r):
    m = r["mestra"]
    assert (m.loc[m.cancelou, "ref"] <= r["contexto"]["fim_base"]).all()
    assert len(r["sinais"]) == 6


def test_acoes_ordenadas_pela_evidencia(r):
    niveis = [NIVEL_EVIDENCIA.get(e, 3) for e in r["acoes"].evidencia]
    assert niveis == sorted(niveis)


def test_modelo_avaliado_com_validacao_cruzada(r):
    auc = r["modelo"]["auc_lr"][0]
    assert 0.3 < auc < 0.8     # base sintetica: numero honesto perto do acaso


def test_premissas_recalculam(tabs):
    a = analisar(tabs, Premissas(taxa_recuperacao_pct=10))
    b = analisar(tabs, Premissas(taxa_recuperacao_pct=40))
    assert b["acoes"].impacto_estimado_mrr.sum() == pytest.approx(4 * a["acoes"].impacto_estimado_mrr.sum())
    c = analisar(tabs, Premissas(pesos_pelos_dados=False))
    assert c["premissas"].pesos["queda_uso"] == 20


def test_funciona_sem_tabelas_opcionais(tabs):
    minimo = {k: v for k, v in tabs.items() if k in ("clientes", "contratos", "cancelamentos")}
    r = analisar(minimo)
    assert r["base"]["canceladas"] == 110
    assert any("desligado" in q for q in r["qualidade"])


def test_relatorios(r):
    md = relatorio.markdown(r, "Teste")
    assert "Resumo executivo" in md and "Plano de ação" in md
    assert relatorio.pdf(r, "Teste")[:4] == b"%PDF"


def test_tela_do_churn_abre(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest
    monkeypatch.setenv("G4_SESSOES", str(tmp_path))
    arquivos = {t.nome: os.path.join(PASTA, t.arquivo_desafio) for t in M.tabelas}
    sid = sessoes.criar("Churn teste", "churn", "desafio", mapeamento_desafio(M), arquivos)
    at = AppTest.from_file(os.path.join(RAIZ, "app", "tela.py"), default_timeout=180)
    at.session_state["pagina"] = "sessao"
    at.session_state["sessao_id"] = sid
    at.run()
    assert not at.exception, at.exception
    textos = " ".join(m.value for m in at.markdown)
    assert "cancelaram" in textos
