"""Testes do nucleo: contratos batem com os dados reais do desafio, leitura, De/Para, sessoes e telas."""
import io
import os
import sys

import pandas as pd
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "app"))

from nucleo import cruzamentos, depara, leitura, sessoes  # noqa: E402
from nucleo.contratos import MODULOS, mapeamento_desafio  # noqa: E402

PASTA = leitura.pasta_dados_desafio()
precisa_dados = pytest.mark.skipif(PASTA is None, reason="dados do desafio ausentes")


@precisa_dados
@pytest.mark.parametrize("chave", list(MODULOS))
def test_contrato_bate_com_dados_do_desafio(chave):
    """Toda coluna do De/Para pronto existe no arquivo real do desafio."""
    for t in MODULOS[chave].tabelas:
        cab = pd.read_csv(os.path.join(PASTA, t.arquivo_desafio), nrows=0).columns
        for c in t.campos:
            if c.coluna_desafio:
                assert c.coluna_desafio in cab, f"{chave}/{t.nome}: {c.coluna_desafio} nao existe"


@precisa_dados
@pytest.mark.parametrize("chave", list(MODULOS))
def test_sugestao_automatica_acerta_dados_do_desafio(chave):
    for t in MODULOS[chave].tabelas:
        cab = pd.read_csv(os.path.join(PASTA, t.arquivo_desafio), nrows=0).columns
        sugestao = depara.sugerir(t, cab)
        esperado = mapeamento_desafio(MODULOS[chave])[t.nome]
        assert {k: v for k, v in sugestao.items() if k in esperado} == esperado
        assert all(sugestao[c.nome] is None for c in t.campos if not c.coluna_desafio)


def test_sugestao_com_nomes_diferentes():
    t = MODULOS["churn"].tabela("clientes")
    mapa = depara.sugerir(t, ["Customer ID", "Churned", "Pais", "Plano"])
    assert mapa["id_cliente"] == "Customer ID"
    assert mapa["cancelou"] == "Churned"
    assert depara.faltando(t, mapa) == []


def test_leitura_csv_ponto_e_virgula_excel_json(tmp_path):
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    (tmp_path / "p.csv").write_text("a;b\n1;x\n2;y\n")
    df.to_excel(tmp_path / "p.xlsx", index=False)
    df.to_json(tmp_path / "p.json", orient="records")
    for nome in ("p.csv", "p.xlsx", "p.json"):
        lido = leitura.ler(str(tmp_path / nome))
        assert list(lido.columns) == ["a", "b"] and len(lido) == 2
    assert len(leitura.perfil(df)) == 2


def test_sessoes_criar_listar_filhas_apagar(tmp_path, monkeypatch):
    monkeypatch.setenv("G4_SESSOES", str(tmp_path))
    mae = sessoes.criar("Churn teste", "churn", "desafio", {"clientes": {}}, {})
    filha = sessoes.criar("Suporte das contas em risco", "suporte", "desafio", {}, {},
                          origem_id=mae, origem_descricao="Churn teste", selo="verde")
    assert {s["id"] for s in sessoes.listar()} == {mae, filha}
    assert [f["id"] for f in sessoes.filhas(mae)] == [filha]
    sessoes.apagar(mae)
    assert sessoes.listar() == []


def test_matriz_de_cruzamentos_completa():
    assert len(cruzamentos.MATRIZ) == 12
    assert cruzamentos.MATRIZ[("churn", "suporte")][0] == "verde"


def test_telas_abrem_sem_erro(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest
    monkeypatch.setenv("G4_SESSOES", str(tmp_path))
    at = AppTest.from_file(os.path.join(RAIZ, "app", "tela.py"), default_timeout=60).run()
    assert not at.exception
    at.button[0].click().run()          # Nova sessao
    assert not at.exception
    assert '>Nova sessão</div>' in " ".join(m.value for m in at.markdown)


@precisa_dados
def test_criar_sessao_com_dados_do_desafio_pela_tela(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest
    monkeypatch.setenv("G4_SESSOES", str(tmp_path))
    at = AppTest.from_file(os.path.join(RAIZ, "app", "tela.py"), default_timeout=120).run()
    at.button[0].click().run()
    at.text_input[0].input("Churn RavenStack").run()
    criar = [b for b in at.button if b.label == "Criar sessão"][0]
    criar.click().run()
    assert not at.exception
    assert '>Churn RavenStack</div>' in " ".join(m.value for m in at.markdown)
    assert len(sessoes.listar()) == 1
