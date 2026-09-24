"""Testes do modulo Leads (desafio 003) com os dados reais do desafio."""
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "app"))

from nucleo import leitura, sessoes  # noqa: E402
from nucleo.carregar import tabelas_da_sessao  # noqa: E402
from nucleo.contratos import MODULOS, mapeamento_desafio  # noqa: E402
from modulos.leads import relatorio  # noqa: E402
from modulos.leads.analise import Premissas, analisar  # noqa: E402

PASTA = leitura.pasta_dados_desafio()
pytestmark = pytest.mark.skipif(PASTA is None, reason="dados do desafio ausentes")
M = MODULOS["leads"]
ARQ = {t.nome: os.path.join(PASTA, t.arquivo_desafio) for t in M.tabelas} if PASTA else {}


@pytest.fixture(scope="module")
def r():
    return analisar(tabelas_da_sessao({"modulo": "leads", "arquivos": ARQ, "mapeamento": mapeamento_desafio(M)}))


def test_pontua_so_os_abertos(r):
    assert len(r["abertos"]) == 1589 + 500
    assert len(r["historico"]) == 4238 + 2473
    assert r["abertos"].score.between(1, 99).all()


def test_corrige_nomes(r):
    assert "GTXPro" not in set(r["deals"].produto)
    assert "technolgy" not in set(r["deals"].setor.dropna())
    assert r["deals"].valor.notna().all()  # todo produto achou preco depois da correcao


def test_todo_deal_tem_motivo_e_acao(r):
    ab = r["abertos"]
    assert ab.motivos.str.len().gt(0).all() and ab.proxima_acao.str.len().gt(0).all()
    # a conta do score fecha: base + pontos = score
    assert ab.conta_do_score.str.contains("base").all()


def test_parado_e_alem_do_maior_ciclo(r):
    ab = r["abertos"]
    lim = r["curva"]["max_ciclo"]
    assert (ab[ab.parado].idade_dias > lim).all()
    assert (ab.faixa == "Parado").sum() == ab.parado.sum()


def test_sem_vazamento_duracao_total_nao_e_fator(r):
    assert "ciclo_dias" not in r["fatores"]


def test_validacao_existe_e_e_honesta(r):
    v = r["validacao"]
    assert v and 0 <= v["auc"] <= 1 and v["n_teste"] > 100


def test_premissa_so_comprovados_zera_indicios():
    tabs = tabelas_da_sessao({"modulo": "leads", "arquivos": ARQ, "mapeamento": mapeamento_desafio(M)})
    r2 = analisar(tabs, Premissas(usar_indicios=False))
    assert not any(f["usado"] for f in r2["fatores"].values() if f["evidencia"] == "sem comprovação")


def test_relatorios(r):
    assert "Priorização" in relatorio.markdown(r, "Teste")
    assert relatorio.pdf(r, "Teste")[:4] == b"%PDF"


def test_tela_de_leads_abre(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest
    monkeypatch.setenv("G4_SESSOES", str(tmp_path))
    sid = sessoes.criar("Leads teste", "leads", "desafio", mapeamento_desafio(M), ARQ)
    at = AppTest.from_file(os.path.join(RAIZ, "app", "tela.py"), default_timeout=180)
    at.session_state["pagina"] = "sessao"
    at.session_state["sessao_id"] = sid
    at.run()
    assert not at.exception, at.exception
    assert "pipeline está parado" in " ".join(m.value for m in at.markdown)
