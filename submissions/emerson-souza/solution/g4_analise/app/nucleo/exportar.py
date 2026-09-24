"""
Salvar arquivos e exportar resultados.

O botao de download do navegador nao funciona dentro da janela propria (pywebview). Como o sistema roda no
computador do usuario, o proprio Python grava o arquivo em Downloads/G4 Analise e mostra o caminho.
"""

import io
import re
import os
import subprocess
import sys
from datetime import datetime

import pandas as pd


def pasta_de_saida():
    pasta = os.environ.get("G4_EXPORTAR")
    if not pasta:
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        if os.path.isdir(downloads):
            pasta = os.path.join(downloads, "G4 Analise")
        else:
            raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            pasta = os.path.join(raiz, "exportados")
    os.makedirs(pasta, exist_ok=True)
    return pasta


def salvar(dados, nome_arquivo):
    """Grava bytes (ou texto) em pasta_de_saida(), com data e hora no nome para nunca sobrescrever."""
    base, ext = os.path.splitext(nome_arquivo)
    caminho = os.path.join(pasta_de_saida(), f"{base}_{datetime.now():%Y-%m-%d_%H%M%S}{ext}")
    if isinstance(dados, str):
        dados = dados.encode("utf-8")
    with open(caminho, "wb") as f:
        f.write(dados)
    return caminho


def abrir_pasta(pasta):
    try:
        if sys.platform.startswith("win"):
            os.startfile(pasta)  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.Popen(["open", pasta])
        else:
            subprocess.Popen(["xdg-open", pasta])
        return True
    except Exception:  # noqa: BLE001
        return False


def botao_salvar(onde, rotulo, gerar, nome_arquivo, key=None):
    """Botao que gera o arquivo SO no clique (gerar = bytes, texto ou funcao) e grava no computador."""
    import streamlit as st
    k = key or f"salvar_{nome_arquivo}"
    icone = {".pdf": ":material/picture_as_pdf:", ".md": ":material/description:", ".xlsx": ":material/table_view:",
             ".csv": ":material/table_view:"}.get(os.path.splitext(nome_arquivo)[1].lower(), ":material/download:")
    if onde.button(rotulo, key=k, icon=icone):
        with st.spinner("Gerando o arquivo..."):
            dados = gerar() if callable(gerar) else gerar
            st.session_state[f"{k}_ok"] = salvar(dados, nome_arquivo)
    caminho = st.session_state.get(f"{k}_ok")
    if caminho:
        onde.success(f"Salvo em: {caminho}")
        if onde.button("Abrir a pasta", key=f"{k}_abrir", icon=":material/folder_open:"):
            if not abrir_pasta(os.path.dirname(caminho)):
                onde.info(f"Abra manualmente: {os.path.dirname(caminho)}")


# ---------------------------------------------------------------- exportar tudo

def _limpar(df):
    d = df.copy()
    for c in d.columns:
        if d[c].dtype == object and d[c].map(lambda x: isinstance(x, (list, tuple, set, dict))).any():
            d[c] = d[c].map(lambda x: ", ".join(map(str, x)) if isinstance(x, (list, tuple, set)) else str(x))
        if isinstance(d[c].dtype, pd.DatetimeTZDtype):
            d[c] = d[c].dt.tz_localize(None)
    return d


def tabela_principal(modulo, r):
    """Uma linha por item analisado (conta, chamado, deal ou post), com todas as colunas calculadas."""
    if modulo == "churn":
        return r["mestra"].reset_index()
    if modulo == "suporte":
        return r["chamados"].reset_index(drop=True)
    if modulo == "leads":
        d = r["deals"].copy()
        cols = [c for c in ("score", "faixa", "lista", "parado", "valor_esperado", "motivos", "conta_do_score", "proxima_acao")
                if c in r["abertos"]]
        return d.join(r["abertos"][cols]).reset_index(drop=True)
    if modulo == "midia":
        return r["posts"].reset_index(drop=True)
    raise ValueError(modulo)


def csv_principal(modulo, r):
    # ; e virgula decimal: abre direto no Excel em portugues
    return _limpar(tabela_principal(modulo, r)).to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")


def _tabelas(obj, prefixo=""):
    """Todas as tabelas (DataFrames) dentro do resultado da analise, com um nome legivel."""
    if isinstance(obj, pd.DataFrame):
        yield prefixo or "tabela", obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("premissas",):
                continue
            yield from _tabelas(v, f"{prefixo}_{k}" if prefixo else str(k))


def excel_completo(modulo, r):
    buf = io.BytesIO()
    usados = set()
    with pd.ExcelWriter(buf, engine="openpyxl") as xl:
        principal = _limpar(tabela_principal(modulo, r))
        principal.to_excel(xl, sheet_name="dados_analisados", index=False)
        usados.add("dados_analisados")
        for nome, df in _tabelas(r):
            if nome in ("mestra", "chamados", "deals", "posts", "abertos", "historico") or df.empty:
                continue
            nome = re.sub(r"[\[\]:*?/\\']", "", nome).strip() or "tabela"
            aba = nome[:31]
            i = 2
            while aba in usados:
                aba = f"{nome[:28]}_{i}"
                i += 1
            usados.add(aba)
            _limpar(df).to_excel(xl, sheet_name=aba, index=not isinstance(df.index, pd.RangeIndex))
    return buf.getvalue()
