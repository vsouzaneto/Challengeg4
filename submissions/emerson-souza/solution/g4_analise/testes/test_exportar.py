"""Salvar arquivos (substitui o download do navegador, que nao funciona na janela) e exportar tudo."""
import io
import os
import sys

import pandas as pd
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "app"))

from nucleo import exportar, leitura, sessoes  # noqa: E402
from nucleo.carregar import tabelas_da_sessao  # noqa: E402
from nucleo.contratos import MODULOS, mapeamento_desafio  # noqa: E402

PASTA = leitura.pasta_dados_desafio()
pytestmark = pytest.mark.skipif(PASTA is None, reason="dados do desafio ausentes")


def _r(chave):
    import importlib
    m = MODULOS[chave]
    s = {"modulo": chave, "arquivos": {t.nome: os.path.join(PASTA, t.arquivo_desafio) for t in m.tabelas},
         "mapeamento": mapeamento_desafio(m)}
    return importlib.import_module(f"modulos.{chave}.analise").analisar(tabelas_da_sessao(s))


def test_salvar_nao_sobrescreve(tmp_path, monkeypatch):
    monkeypatch.setenv("G4_EXPORTAR", str(tmp_path))
    a = exportar.salvar(b"1", "x.csv")
    assert os.path.exists(a) and a.startswith(str(tmp_path)) and a.endswith(".csv")


@pytest.mark.parametrize("chave,linhas", [("churn", 500), ("leads", 8800), ("suporte", 8469)])
def test_csv_e_excel(chave, linhas):
    r = _r(chave)
    csv = exportar.csv_principal(chave, r)
    df = pd.read_csv(io.BytesIO(csv), sep=";", decimal=",")
    assert len(df) == linhas
    xl = pd.ExcelFile(io.BytesIO(exportar.excel_completo(chave, r)))
    assert "dados_analisados" in xl.sheet_names and len(xl.sheet_names) > 3


def test_leads_csv_tem_score_nos_abertos():
    r = _r("leads")
    df = exportar.tabela_principal("leads", r)
    assert df.loc[df.situacao == "aberto", "score"].notna().all()
    assert df.loc[df.situacao != "aberto", "score"].isna().all()


def test_botoes_salvam_pdf_e_exportacao(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest
    monkeypatch.setenv("G4_SESSOES", str(tmp_path / "s"))
    monkeypatch.setenv("G4_EXPORTAR", str(tmp_path / "e"))
    m = MODULOS["churn"]
    sid = sessoes.criar("Churn", "churn", "desafio", mapeamento_desafio(m),
                        {t.nome: os.path.join(PASTA, t.arquivo_desafio) for t in m.tabelas})
    at = AppTest.from_file(os.path.join(RAIZ, "app", "tela.py"), default_timeout=240)
    at.session_state["pagina"] = "sessao"
    at.session_state["sessao_id"] = sid
    at.run()
    for rotulo in ("Salvar PDF", "Salvar Markdown", "Salvar CSV", "Salvar Excel", "Salvar lista (CSV)"):
        next(b for b in at.button if b.label == rotulo).click().run()
        assert not at.exception, at.exception
    feitos = sorted(os.listdir(tmp_path / "e"))
    assert [os.path.splitext(f)[1] for f in feitos].count(".pdf") == 1
    assert len(feitos) == 5 and any(f.endswith(".xlsx") for f in feitos)
