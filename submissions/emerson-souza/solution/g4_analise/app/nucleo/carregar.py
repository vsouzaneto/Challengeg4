"""Carrega as tabelas de uma sessao ja com os nomes do contrato (De/Para aplicado) e tipos padronizados."""

import pandas as pd

from . import depara, leitura
from .contratos import MODULOS

VERDADEIRO = {"true", "1", "sim", "s", "yes", "y", "t", "verdadeiro"}


def para_booleano(serie):
    if serie.dtype == bool:
        return serie
    return serie.astype(str).str.strip().str.lower().isin(VERDADEIRO)


def para_data(serie):
    return pd.to_datetime(serie, errors="coerce", format="mixed")


def para_numero(serie):
    return pd.to_numeric(serie, errors="coerce")


def tabelas_da_sessao(sessao, ler=leitura.ler):
    """{tabela: DataFrame com colunas no padrao do sistema}. Tabelas nao enviadas ficam de fora."""
    modulo = MODULOS[sessao["modulo"]]
    saida = {}
    for t in modulo.tabelas:
        caminho = sessao["arquivos"].get(t.nome)
        if not caminho:
            continue
        mapa = {k: v for k, v in sessao["mapeamento"].get(t.nome, {}).items() if v}
        saida[t.nome] = depara.aplicar(ler(caminho), mapa)
    return saida
