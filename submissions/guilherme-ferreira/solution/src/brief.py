"""Brief de segunda: os números da semana e os grupos que se destacaram, ou não."""
import pandas as pd

from src.celulas import comparar_com_resto
from src.formato import percentual_br

TOTAL = "total"


COLUNAS_DESTAQUES = ["dimensao", "valor", "n", "media", "media_resto", "lift", "ic_inf", "ic_sup", "p", "p_ajustado", "classe", "posicao"]


def semana_padrao(semanas):
    """A semana mais recente cujo domingo não passa da data do último post; se nenhuma terminou, a mais recente."""
    ultimo_dia = pd.to_datetime(semanas["ultimo_post"]).max().normalize()
    inicios = pd.to_datetime(semanas["semana"])
    terminadas = inicios[inicios + pd.Timedelta(days=6) <= ultimo_dia]
    return pd.Timestamp((terminadas if len(terminadas) else inicios).max())


def indicadores_semana(semanas, semana, custo_por_post):
    """Posts e parcela patrocinada; entre os patrocinados, as parcelas sem fit, com divulgação implícita
    e em parceria de um post só; e o gasto estimado nas práticas a parar (posts com algum problema x custo)."""
    linha = semanas.loc[pd.to_datetime(semanas["semana"]) == pd.Timestamp(semana)].iloc[0]
    posts = int(linha["posts"])
    patrocinados = int(linha["patrocinados"])

    def sobre_patrocinados(coluna):
        return float(linha[coluna]) / patrocinados if patrocinados else 0.0

    return {
        "posts": posts,
        "patrocinados": patrocinados / posts if posts else 0.0,
        "sem_fit": sobre_patrocinados("sem_fit"),
        "implicita": sobre_patrocinados("implicita"),
        "um_post_so": sobre_patrocinados("um_post_so"),
        "posts_com_problema": int(linha["algum_problema"]),
        "gasto": int(linha["algum_problema"]) * custo_por_post,
    }


def destaques_semana(semanas_grupos, semana, quantos=3):
    """Os `quantos` grupos acima e abaixo do resto da semana, com a classe da regra de sinal.
    Cada grupo é comparado com os outros posts da mesma semana, com a correção entre todos os grupos."""
    da_semana = semanas_grupos[pd.to_datetime(semanas_grupos["semana"]) == pd.Timestamp(semana)]
    total = da_semana[da_semana["dimensao"] == TOTAL].iloc[0]
    # Um grupo que é a semana inteira não tem com quem se comparar.
    comparaveis = (da_semana["dimensao"] != TOTAL) & (da_semana["n"] < total["n"])
    grupos = da_semana[comparaveis][["dimensao", "valor", "n", "media", "var"]].reset_index(drop=True)
    if grupos.empty:
        return pd.DataFrame(columns=COLUNAS_DESTAQUES)
    tabela = (
        comparar_com_resto(grupos, total["n"], total["media"], total["var"])
        .dropna(subset=["lift"])
        .sort_values("lift", ascending=False)
    )
    acima = tabela.head(quantos)
    abaixo = tabela.iloc[len(acima):].tail(quantos).iloc[::-1]  # nunca repete um grupo de cima
    return pd.concat([acima.assign(posicao="acima"), abaixo.assign(posicao="abaixo")], ignore_index=True)


def veredito(destaques):
    """Uma frase para o Head sobre os destaques da semana."""
    sinais = destaques[destaques["classe"] == "sinal"].drop_duplicates(["dimensao", "valor"])
    if sinais.empty:
        return "Nenhum grupo virou sinal: não mude o mix por causa disso."
    partes = [f"{linha.valor} ({percentual_br(linha.lift, 1, sinal=True)})" for linha in sinais.itertuples()]
    return "Virou sinal: " + ", ".join(partes) + ". Confirme com um teste antes de mudar o mix."
