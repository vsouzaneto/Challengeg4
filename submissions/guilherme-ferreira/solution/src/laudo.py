"""Contas do laudo do dado: testes simples que mostram se o arquivo tem sinal."""
import re

import pandas as pd

# Kana e ideogramas (chinês, japonês), hangul (coreano) e devanágari (hindi)
_ESCRITA_NAO_LATINA = re.compile(
    r"[぀-ヿ㐀-䶿一-鿿가-힯ऀ-ॿ]"
)


def indice_dispersao(valores) -> float:
    """Variância dividida pela média. Perto de 1, o número se comporta como um sorteio
    (Poisson) em torno de um valor fixo: não sobra variação para mais nada explicar."""
    serie = pd.Series(valores, dtype="float64")
    return serie.var(ddof=1) / serie.mean()


def variacao_seguidores(df) -> pd.DataFrame:
    """Por creator: menor e maior número de seguidores entre os posts e a razão maior/menor."""
    tabela = df.groupby("creator_id")["follower_count"].agg(minimo="min", maximo="max")
    tabela["razao"] = tabela["maximo"] / tabela["minimo"]
    return tabela


def proporcao_esperada_uniforme(limites, minimo, maximo) -> list:
    """Parcela de cada faixa se o valor fosse sorteado por igual entre minimo e maximo."""
    total = maximo - minimo
    return [
        max(0, min(fim, maximo) - max(inicio, minimo)) / total
        for inicio, fim in zip(limites[:-1], limites[1:])
    ]


def usa_escrita_nao_latina(texto) -> bool:
    """True se o texto tem algum caractere chinês, japonês, coreano ou hindi."""
    return isinstance(texto, str) and bool(_ESCRITA_NAO_LATINA.search(texto))
