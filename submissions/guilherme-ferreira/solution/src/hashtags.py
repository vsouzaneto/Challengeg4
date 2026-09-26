"""Hashtags: cada hashtag comparada com os posts que não a usam."""
import pandas as pd

from src.estatistica import ALFA, LIMIAR, N_MINIMO, classificar, comparar

COLUNAS = ["hashtag", "n", "media", "media_base", "lift", "ic_inf", "ic_sup", "p"]


def comparar_hashtags(df, metrica="engajamento", minimo=100, limiar=LIMIAR, n_min=N_MINIMO, alfa=ALFA):
    """Para cada hashtag usada em pelo menos `minimo` posts, compara a métrica dos posts que a
    usam com a dos que não usam e aplica a regra de sinal, corrigindo para todas as hashtags testadas."""
    pares = df["hashtags"].dropna().str.split(",").explode().str.strip()
    pares = pares[pares != ""].rename("hashtag").rename_axis("post").reset_index().drop_duplicates()
    contagem = pares["hashtag"].value_counts()
    testadas = pares[pares["hashtag"].isin(contagem[contagem >= minimo].index)]

    valores = df[metrica].astype("float64")
    linhas = []
    for hashtag, posts in testadas.groupby("hashtag")["post"]:
        com = valores.index.isin(posts)
        linhas.append({"hashtag": hashtag, **comparar(valores[com], valores[~com])})
    return classificar(pd.DataFrame(linhas, columns=COLUNAS), limiar, n_min, alfa)
