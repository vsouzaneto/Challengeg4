"""Métricas definidas antes de olhar os resultados."""
import numpy as np
import pandas as pd

FAIXAS = ["nano", "micro", "mid", "macro"]
# nano: menos de 10 mil seguidores; micro: 10 a 50 mil; mid: 50 a 500 mil; macro: 500 mil ou mais
LIMITES_FAIXA = [0, 10_000, 50_000, 500_000, np.inf]


def _por_view(numerador, views):
    return (numerador / views).where(views > 0)


def engajamento(df):
    """(likes + shares + comentários) / views. Sem views, fica indefinido (NaN)."""
    return _por_view(df["likes"] + df["shares"] + df["comments_count"], df["views"])


def taxa_conversa(df):
    """Comentários por view."""
    return _por_view(df["comments_count"], df["views"])


def taxa_compartilhamento(df):
    """Shares por view."""
    return _por_view(df["shares"], df["views"])


def faixa_creator(seguidores):
    return pd.cut(seguidores, LIMITES_FAIXA, right=False, labels=FAIXAS)


def adicionar_metricas(df):
    """Cópia do dado com as métricas e a faixa do creator."""
    novo = df.copy()
    novo["engajamento"] = engajamento(df)
    novo["taxa_conversa"] = taxa_conversa(df)
    novo["taxa_compartilhamento"] = taxa_compartilhamento(df)
    novo["faixa_creator"] = faixa_creator(df["follower_count"])
    return novo
