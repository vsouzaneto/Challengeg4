"""Validação do método por simulação.

Planta efeitos conhecidos numa cópia do dado e verifica se o método os encontra. Nenhum
número da análise sai daqui: a simulação só mostra do que o método é capaz.
"""
import numpy as np
import pandas as pd

from src.celulas import mapa_celulas
from src.estatistica import ALFA, LIMIAR, N_MINIMO
from src.metricas import engajamento

INTERACOES = ["likes", "shares", "comments_count"]


def plantar_efeito(df, mascara, efeito):
    """Cópia do dado com likes, shares e comentários multiplicados por (1 + efeito) nas linhas marcadas."""
    copia = df.copy()
    for coluna in INTERACOES:
        novo = (copia.loc[mascara, coluna] * (1 + efeito)).round()
        copia.loc[mascara, coluna] = novo.astype(copia[coluna].dtype)
    return copia


def _mapa(df, dimensoes, **regra):
    return mapa_celulas(df.assign(engajamento=engajamento(df)), dimensoes, **regra)


def _na_celula(df, dimensoes, celula):
    return np.logical_and.reduce([df[d].to_numpy() == celula[d] for d in dimensoes])


def validar_metodo(df, efeitos, dimensoes, repeticoes=200, semente=42, limiar=LIMIAR, n_min=N_MINIMO, alfa=ALFA):
    """Para cada efeito, repete: sorteia uma célula com posts suficientes, planta o efeito nela,
    refaz o mapa e anota a classe que a célula plantada recebeu e quantas outras viraram sinal."""
    regra = {"limiar": limiar, "n_min": n_min, "alfa": alfa}
    base = df[dimensoes + INTERACOES + ["views"]]
    mapa_base = _mapa(base, dimensoes, **regra)
    elegiveis = mapa_base.loc[mapa_base["n"] >= n_min, dimensoes].reset_index(drop=True)
    rng = np.random.default_rng(semente)
    rodadas = []
    for efeito in efeitos:
        for rodada in range(repeticoes):
            celula = elegiveis.iloc[rng.integers(len(elegiveis))]
            plantado = plantar_efeito(base, _na_celula(base, dimensoes, celula), efeito)
            mapa = _mapa(plantado, dimensoes, **regra)
            plantada = _na_celula(mapa, dimensoes, celula)
            linha = mapa[plantada].iloc[0]
            rodadas.append(
                {
                    "efeito": efeito,
                    "rodada": rodada,
                    **{d: celula[d] for d in dimensoes},
                    "n": int(linha["n"]),
                    "lift_medido": linha["lift"],
                    "classe": linha["classe"],
                    "falsos_positivos": int(((mapa["classe"] == "sinal") & ~plantada).sum()),
                }
            )
    return pd.DataFrame(rodadas)


def resumir_validacao(rodadas):
    """Uma linha por efeito plantado: com que frequência virou sinal, virou "abaixo do
    limiar", o lift medido em média e quantas outras células viraram sinal por engano."""
    return (
        rodadas.assign(
            sinal=rodadas["classe"] == "sinal",
            abaixo=rodadas["classe"] == "abaixo do limiar",
        )
        .groupby("efeito")
        .agg(
            rodadas=("rodada", "count"),
            taxa_sinal=("sinal", "mean"),
            taxa_abaixo_do_limiar=("abaixo", "mean"),
            lift_medido_medio=("lift_medido", "mean"),
            falsos_positivos_por_rodada=("falsos_positivos", "mean"),
        )
        .reset_index()
        .sort_values("efeito", ascending=False, ignore_index=True)
    )
