import numpy as np
import pandas as pd
import pytest

from src.celulas import comparar_com_resto, mapa_celulas
from src.estatistica import comparar

DIMENSOES = ["plataforma", "formato"]


def posts_sinteticos():
    """Quatro células de 60 posts, uma delas 20% acima, e uma célula de 5 posts."""
    rng = np.random.default_rng(3)
    celulas = [("A", "x", 60, 0.24), ("A", "y", 60, 0.20), ("B", "x", 60, 0.20), ("B", "y", 60, 0.20), ("B", "z", 5, 0.20)]
    partes = [
        pd.DataFrame({"plataforma": p, "formato": f, "engajamento": rng.normal(media, 0.005, n)})
        for p, f, n, media in celulas
    ]
    return pd.concat(partes, ignore_index=True)


def test_mapa_celulas_so_marca_como_sinal_a_celula_com_efeito_grande():
    mapa = mapa_celulas(posts_sinteticos(), DIMENSOES).set_index(DIMENSOES)

    assert mapa["classe"].to_dict() == {
        ("A", "x"): "sinal",
        ("A", "y"): "abaixo do limiar",
        ("B", "x"): "abaixo do limiar",
        ("B", "y"): "abaixo do limiar",
        ("B", "z"): "poucos posts",
    }
    assert mapa.loc[("A", "x"), "lift"] == pytest.approx(0.20, abs=0.01)


def test_mapa_celulas_compara_cada_celula_com_o_resto_dos_posts():
    df = posts_sinteticos()
    na_celula = (df["plataforma"] == "A") & (df["formato"] == "y")
    esperado = comparar(df.loc[na_celula, "engajamento"], df.loc[~na_celula, "engajamento"])

    linha = mapa_celulas(df, DIMENSOES).set_index(DIMENSOES).loc[("A", "y")]

    assert linha["n"] == 60
    assert linha["lift"] == pytest.approx(esperado["lift"], rel=1e-9)
    assert linha["p"] == pytest.approx(esperado["p"], rel=1e-6)
    assert linha["ic_inf"] == pytest.approx(esperado["ic_inf"], rel=1e-6)
    assert linha["ic_sup"] == pytest.approx(esperado["ic_sup"], rel=1e-6)


def test_comparar_com_resto_a_partir_de_resumos_bate_com_comparar():
    df = posts_sinteticos()
    resumo = df.groupby(DIMENSOES)["engajamento"].agg(n="count", media="mean", var="var").reset_index()
    valores = df["engajamento"]

    tabela = comparar_com_resto(resumo, len(valores), valores.mean(), valores.var()).set_index(DIMENSOES)

    na_celula = (df["plataforma"] == "B") & (df["formato"] == "x")
    esperado = comparar(df.loc[na_celula, "engajamento"], df.loc[~na_celula, "engajamento"])
    assert tabela.loc[("B", "x"), "lift"] == pytest.approx(esperado["lift"], rel=1e-9)
    assert tabela.loc[("B", "x"), "p"] == pytest.approx(esperado["p"], rel=1e-6)
    assert tabela.loc[("B", "x"), "ic_sup"] == pytest.approx(esperado["ic_sup"], rel=1e-6)
