import math

import pandas as pd
import pytest

from src.metricas import (
    adicionar_metricas,
    engajamento,
    faixa_creator,
    taxa_compartilhamento,
    taxa_conversa,
)


def posts(**colunas):
    return pd.DataFrame(colunas)


def test_engajamento_soma_likes_shares_comentarios_sobre_views():
    df = posts(likes=[100], shares=[20], comments_count=[30], views=[1000])

    assert engajamento(df).iloc[0] == pytest.approx(0.15)


def test_engajamento_sem_views_fica_indefinido():
    df = posts(likes=[5], shares=[0], comments_count=[0], views=[0])

    assert math.isnan(engajamento(df).iloc[0])


def test_taxas_separam_conversa_de_compartilhamento():
    df = posts(likes=[100], shares=[20], comments_count=[30], views=[1000])

    assert taxa_conversa(df).iloc[0] == pytest.approx(0.03)
    assert taxa_compartilhamento(df).iloc[0] == pytest.approx(0.02)


@pytest.mark.parametrize(
    "seguidores, faixa",
    [
        (1_000, "nano"),
        (9_999, "nano"),
        (10_000, "micro"),
        (49_999, "micro"),
        (50_000, "mid"),
        (499_999, "mid"),
        (500_000, "macro"),
        (999_998, "macro"),
    ],
)
def test_faixa_creator_nos_limites(seguidores, faixa):
    assert faixa_creator(pd.Series([seguidores])).iloc[0] == faixa


def test_adicionar_metricas_nao_altera_o_original():
    df = posts(likes=[100], shares=[20], comments_count=[30], views=[1000], follower_count=[20_000])

    novo = adicionar_metricas(df)

    assert "engajamento" not in df.columns
    assert novo.loc[0, "engajamento"] == pytest.approx(0.15)
    assert novo.loc[0, "faixa_creator"] == "micro"
