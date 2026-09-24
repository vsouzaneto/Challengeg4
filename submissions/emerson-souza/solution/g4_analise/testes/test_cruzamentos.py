"""Testes das pontes entre modulos (cooperativo) com os dados reais do desafio."""
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "app"))

from nucleo import cruzamentos, leitura  # noqa: E402
from nucleo.carregar import tabelas_da_sessao  # noqa: E402
from nucleo.contratos import MODULOS, mapeamento_desafio  # noqa: E402
from modulos.churn.analise import analisar as analisar_churn  # noqa: E402
from modulos.churn.pontes import para_suporte  # noqa: E402
from modulos.suporte.analise import analisar as analisar_suporte  # noqa: E402

PASTA = leitura.pasta_dados_desafio()
pytestmark = pytest.mark.skipif(PASTA is None, reason="dados do desafio ausentes")


@pytest.fixture(scope="module")
def churn():
    m = MODULOS["churn"]
    s = {"nome": "teste", "modulo": "churn", "mapeamento": mapeamento_desafio(m),
         "arquivos": {t.nome: os.path.join(PASTA, t.arquivo_desafio) for t in m.tabelas}}
    return s, analisar_churn(tabelas_da_sessao(s))


def test_ponte_churn_suporte_so_leva_as_contas_certas(churn):
    s, r = churn
    saida = para_suporte(s, r)
    ch = saida["tabelas"]["chamados"]
    assert saida["modulo"] == "suporte"
    assert set(ch.id_cliente) <= set(r["precisa_suporte"].index)
    assert ch.id_cliente.nunique() == len(r["precisa_suporte"])  # toda conta sinalizada tem chamado
    assert set(ch.columns) <= {c.nome for c in MODULOS["suporte"].tabela("chamados").campos}


def test_suporte_roda_nos_tickets_da_ravenstack(churn):
    s, r = churn
    ch = para_suporte(s, r)["tabelas"]["chamados"]
    x = analisar_suporte({"chamados": ch})
    assert x["classificador"] is None and x["automacao"] is None  # sem texto, sem classificador
    assert x["info"]["n_duracao_valida"] == len(ch)
    assert x["desperdicio"]["chamados_medidos"] == len(ch)
    assert 0 < x["volume"]["resposta_mediana_h"] < 5  # 1a resposta vem em minutos -> horas


def test_selo_verde_na_matriz():
    assert cruzamentos.MATRIZ[("churn", "suporte")][0] == "verde"


def test_tela_envia_churn_para_suporte(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest
    from nucleo import sessoes
    monkeypatch.setenv("G4_SESSOES", str(tmp_path))
    m = MODULOS["churn"]
    arquivos = {t.nome: os.path.join(PASTA, t.arquivo_desafio) for t in m.tabelas}
    sid = sessoes.criar("Churn teste", "churn", "desafio", mapeamento_desafio(m), arquivos)
    at = AppTest.from_file(os.path.join(RAIZ, "app", "tela.py"), default_timeout=180)
    at.session_state["pagina"] = "sessao"
    at.session_state["sessao_id"] = sid
    at.run()
    assert not at.exception, at.exception
    botao = next(b for b in at.button if b.label == "Enviar para Suporte")
    botao.click().run()
    assert not at.exception, at.exception
    filhas = sessoes.filhas(sid)
    assert len(filhas) == 1 and filhas[0]["modulo"] == "suporte" and filhas[0]["selo"] == "verde"
    assert at.session_state["sessao_id"] == filhas[0]["id"]
    textos = " ".join(m.value for m in at.markdown)
    assert "Desperdício" in textos and "1ª resposta" in textos


def test_ponte_churn_leads_carteira_de_expansao(churn):
    from modulos.churn.pontes import para_leads
    from modulos.leads.analise import analisar as analisar_leads
    s, r = churn
    saida = para_leads(s, r)
    x = analisar_leads(saida["tabelas"])
    ativos = int((~r["mestra"].cancelou).sum())
    assert len(x["abertos"]) == ativos
    assert (x["abertos"].lista == "Foco").all()          # sem datas: ninguem vira 'parado' nem 'prospeccao'
    assert x["validacao"] is None and x["curva"] is None
    assert x["abertos"].valor.sum() == pytest.approx(r["mestra"][~r["mestra"].cancelou].mrr.sum())
    assert cruzamentos.MATRIZ[("churn", "leads")][0] == "amarelo"


# ---------------------------------------------------------------- pontes da etapa 8

def _sessao(chave, so=None):
    m = MODULOS[chave]
    arq = {t.nome: os.path.join(PASTA, t.arquivo_desafio) for t in m.tabelas if so is None or t.nome in so}
    return {"id": None, "nome": chave, "modulo": chave, "arquivos": arq, "mapeamento": mapeamento_desafio(m)}


@pytest.fixture(scope="module")
def suporte():
    s = _sessao("suporte", so=("chamados",))
    return s, analisar_suporte(tabelas_da_sessao(s))


def test_suporte_para_churn_sem_receita(suporte):
    from modulos.suporte.pontes import para_churn
    s, r = suporte
    x = analisar_churn(para_churn(s, r)["tabelas"])
    assert x["base"]["sem_receita"] and x["base"]["clientes"] > 8000
    assert 0.15 < x["base"]["taxa_churn"] < 0.25          # ~20% pediram cancelamento
    assert "faixa_idade" in x["segmentos"]


def test_suporte_para_leads_e_lista(suporte):
    from modulos.suporte.pontes import para_leads
    s, r = suporte
    out = para_leads(s, r)
    assert out["tipo"] == "lista" and len(out["df"]) == 1641


def test_pontes_tipo_b_filtram_a_base_de_destino(churn, suporte):
    from nucleo import perfis
    from modulos.churn.pontes import para_midia as churn_midia
    from modulos.suporte.pontes import para_midia as suporte_midia
    base = dict(perfis.bases_de_destino("midia"))["Dados do desafio"]
    for fn, (s, r) in ((churn_midia, churn), (suporte_midia, suporte)):
        out = fn(s, r, base)
        assert 0 < len(out["brutas"]["posts"]) < 52214
        assert out["modulo"] == "midia"


def test_leads_e_midia_tipo_b():
    from nucleo import perfis
    from modulos.leads.analise import analisar as analisar_leads
    from modulos.leads.pontes import para_midia
    from modulos.midia.analise import analisar as analisar_midia
    from modulos.midia.pontes import para_leads
    s = _sessao("leads")
    out = para_midia(s, analisar_leads(tabelas_da_sessao(s)), dict(perfis.bases_de_destino("midia"))["Dados do desafio"])
    assert "USA" in out["descricao"]
    s = _sessao("midia")
    out = para_leads(s, analisar_midia(tabelas_da_sessao(s)), dict(perfis.bases_de_destino("leads"))["Dados do desafio"])
    assert 0 < len(out["brutas"]["oportunidades"]) < 8800


def test_tela_tipo_b_cria_sub_sessao_com_base_escolhida(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest
    from nucleo import sessoes
    monkeypatch.setenv("G4_SESSOES", str(tmp_path))
    m = MODULOS["churn"]
    sid = sessoes.criar("Churn teste", "churn", "desafio", mapeamento_desafio(m),
                        {t.nome: os.path.join(PASTA, t.arquivo_desafio) for t in m.tabelas})
    at = AppTest.from_file(os.path.join(RAIZ, "app", "tela.py"), default_timeout=240)
    at.session_state["pagina"] = "sessao"
    at.session_state["sessao_id"] = sid
    at.run()
    next(b for b in at.button if b.label == "Enviar para Mídia").click().run()
    assert not at.exception, at.exception
    f = [x for x in sessoes.filhas(sid) if x["modulo"] == "midia"]
    assert len(f) == 1 and f[0]["selo"] == "azul"
    assert "posts" in f[0]["arquivos"] and f[0]["mapeamento"]["posts"]["audiencia_local"] == "audience_location"
