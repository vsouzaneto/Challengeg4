"""Leitura dos resumos do Radar, com mensagem clara quando faltam."""
import os
from pathlib import Path

import pandas as pd
import streamlit as st

COLUNAS = {
    "laudo.csv": ["chave", "valor"],
    "simulacao.csv": ["efeito", "rodadas", "taxa_sinal", "taxa_abaixo_do_limiar", "lift_medido_medio", "falsos_positivos_por_rodada"],
    "celulas.csv": ["objetivo", "platform", "content_category", "content_type", "n", "lift", "ic_inf", "ic_sup", "p_ajustado", "classe"],
    "semanas.csv": ["semana", "dias", "ultimo_post", "posts", "patrocinados", "sem_fit", "implicita", "so_hashtag", "um_post_so", "algum_problema"],
    "semanas_grupos.csv": ["semana", "dimensao", "valor", "n", "media", "var"],
}
COMO_GERAR = "Rode `python solution/gerar_resumos.py` na pasta da submissão."


class ResumoAusente(Exception):
    """O resumo não existe ou não tem as colunas esperadas."""


def pasta_resumos():
    return Path(os.environ.get("RADAR_RESUMOS", Path(__file__).resolve().parent / "resumos"))


def ler_resumo(nome, pasta=None):
    caminho = Path(pasta or pasta_resumos()) / nome
    if not caminho.exists():
        raise ResumoAusente(f"O resumo {nome} não foi encontrado. {COMO_GERAR}")
    tabela = pd.read_csv(caminho)
    faltando = [coluna for coluna in COLUNAS[nome] if coluna not in tabela.columns]
    if faltando:
        raise ResumoAusente(f"O resumo {nome} não tem as colunas {', '.join(faltando)}. {COMO_GERAR}")
    for coluna in ("semana", "ultimo_post"):
        if coluna in tabela.columns:
            tabela[coluna] = pd.to_datetime(tabela[coluna])
    return tabela


@st.cache_data(show_spinner=False)
def _ler_com_cache(nome, pasta):
    return ler_resumo(nome, pasta)


def carregar_resumos(*nomes):
    """Os resumos pedidos, ou None depois de mostrar o erro na tela."""
    try:
        return [_ler_com_cache(nome, str(pasta_resumos())) for nome in nomes]
    except ResumoAusente as erro:
        st.error(str(erro))
        return None
