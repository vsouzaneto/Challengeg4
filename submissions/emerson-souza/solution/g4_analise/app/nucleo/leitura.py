"""Leitura de arquivos (CSV, Excel, JSON) e perfil dos dados."""

import io
import os

import pandas as pd

FORMATOS = ("csv", "xlsx", "xls", "json")


def ler(origem, nome=None):
    """Le um caminho ou um arquivo enviado pela tela. Devolve um DataFrame."""
    nome = (nome or getattr(origem, "name", None) or str(origem)).lower()
    if nome.endswith((".xlsx", ".xls")):
        return pd.read_excel(origem)
    if nome.endswith(".json"):
        return pd.read_json(origem)
    if nome.endswith(".csv"):
        return _ler_csv(origem)
    raise ValueError(f"Formato nao suportado: {nome}. Use CSV, Excel ou JSON.")


def _ler_csv(origem):
    # Tenta virgula; se vier uma coluna so, tenta ponto e virgula (padrao do Excel em portugues).
    if hasattr(origem, "read"):
        dados = origem.read()
        origem = io.BytesIO(dados if isinstance(dados, bytes) else dados.encode("utf-8"))
    df = pd.read_csv(origem)
    if df.shape[1] == 1:
        if hasattr(origem, "seek"):
            origem.seek(0)
        df2 = pd.read_csv(origem, sep=";")
        if df2.shape[1] > 1:
            return df2
    return df


def perfil(df):
    """Resumo de cada coluna: tipo, nulos, valores unicos e exemplos."""
    linhas = []
    for c in df.columns:
        s = df[c]
        linhas.append({
            "coluna": c,
            "tipo": str(s.dtype),
            "nulos": int(s.isna().sum()),
            "nulos_%": round(100 * s.isna().mean(), 1) if len(s) else 0.0,
            "unicos": int(s.nunique()),
            "exemplos": ", ".join(str(v)[:30] for v in s.dropna().unique()[:3]),
        })
    return pd.DataFrame(linhas)


def pasta_dados_desafio():
    """Onde estao os dados do desafio: variavel G4_DADOS, ou g4_analise/dados, ou ../dados."""
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    candidatos = [os.environ.get("G4_DADOS"), os.path.join(base, "dados"), os.path.join(os.path.dirname(base), "dados")]
    for c in candidatos:
        if c and os.path.isdir(c):
            return c
    return None
