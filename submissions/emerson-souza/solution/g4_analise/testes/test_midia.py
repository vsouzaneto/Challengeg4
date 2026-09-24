"""Testes do modulo Midia (desafio 004) com os dados reais do desafio."""
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "app"))

from nucleo import leitura, sessoes  # noqa: E402
from nucleo.carregar import tabelas_da_sessao  # noqa: E402
from nucleo.contratos import MODULOS, mapeamento_desafio  # noqa: E402
from modulos.midia import relatorio  # noqa: E402
from modulos.midia.analise import Premissas, analisar  # noqa: E402

PASTA = leitura.pasta_dados_desafio()
pytestmark = pytest.mark.skipif(PASTA is None, reason="dados do desafio ausentes")
M = MODULOS["midia"]
ARQ = {t.nome: os.path.join(PASTA, t.arquivo_desafio) for t in M.tabelas} if PASTA else {}


@pytest.fixture(scope="module")
def r():
    return analisar(tabelas_da_sessao({"modulo": "midia", "arquivos": ARQ, "mapeamento": mapeamento_desafio(M)}))


def test_engajamento_calculado(r):
    c = r["posts"]
    assert len(c) == 52214
    assert c["eng_%"].between(0, 100).all()


def test_patrocinio_comparado_dentro_do_estrato(r):
    e = r["patrocinio"]["engajamento"]
    assert e["estratos"] >= 50            # 5 plataformas x 3 categorias x 5 faixas
    assert e["p_valor"] > 0.05            # nesta base nao ha diferenca


def test_sanidade_encontra_efeito_injetado(r):
    for v in r["sanidade"].values():
        assert v["achou"], v


def test_combinacoes_com_correcao(r):
    cb = r["combinacoes"]
    assert cb["limite_p"] < 0.05 and cb["aprovadas"] <= cb["p_brutos_abaixo_005"]


def test_estrategia_priorizada_com_evidencia(r):
    e = r["estrategia"]
    assert list(e.prioridade) == list(range(1, len(e) + 1))
    assert e[["o_que", "para_quem", "quando", "evidencia"]].notna().all().all()
    assert len(r["quick_wins"]) >= 2


def test_efeito_injetado_num_estrato_e_achado():
    tabs = tabelas_da_sessao({"modulo": "midia", "arquivos": ARQ, "mapeamento": mapeamento_desafio(M)})
    r2 = analisar(tabs, Premissas(efeito_sanidade_pct=5))
    assert r2["sanidade"]["patrocinio"]["achou"]


def test_relatorios(r):
    assert "Estratégia" in relatorio.markdown(r, "Teste")
    assert relatorio.pdf(r, "Teste")[:4] == b"%PDF"


def test_tela_de_midia_abre(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest
    monkeypatch.setenv("G4_SESSOES", str(tmp_path))
    sid = sessoes.criar("Midia teste", "midia", "desafio", mapeamento_desafio(M), ARQ)
    at = AppTest.from_file(os.path.join(RAIZ, "app", "tela.py"), default_timeout=240)
    at.session_state["pagina"] = "sessao"
    at.session_state["sessao_id"] = sid
    at.run()
    assert not at.exception, at.exception
    assert "Patrocínio não aumenta" in " ".join(m.value for m in at.markdown)


def test_diferenciais_cluster_e_recomendacao(r):
    from modulos.midia.analise import recomendar_post
    cl = r["clusters"]
    assert cl and len(cl["tabela"]) == cl["k"]
    rec = recomendar_post(r["posts"], Premissas(), plataforma="TikTok", tipo="video")
    assert rec["n"] > 1000 and rec["faixa_normal"][0] < rec["eng_%"] < rec["faixa_normal"][1]
