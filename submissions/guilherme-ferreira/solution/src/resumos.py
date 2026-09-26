"""Resumos pequenos que o Radar lê. O CSV bruto nunca sai da máquina de quem roda o script."""
import pandas as pd

from src.celulas import mapa_celulas
from src.laudo import indice_dispersao, usa_escrita_nao_latina, variacao_seguidores
from src.patrocinio import FIT_PATROCINIO, marcar_fit

DIMENSOES_CELULA = ["platform", "content_category", "content_type"]
DIMENSOES_GRUPO = ["platform", "content_type", "content_category"]
OBJETIVOS = {
    "engajamento": "engajamento",
    "alcance": "views",
    "conversa": "taxa_conversa",
    "compartilhamento": "taxa_compartilhamento",
}
LINGUAS_NAO_LATINAS = ["Chinese", "Japanese", "Hindi"]


def semana(datas):
    """Segunda-feira (00:00) da semana de cada data."""
    return datas.dt.to_period("W-SUN").dt.start_time


def marcar_problemas(df):
    """Por post: patrocinado sem fit, com divulgação implícita, só nas hashtags, em parceria de um
    post só (o patrocinador aparece uma vez em todo o histórico) e com pelo menos um dos três
    problemas (sem fit, implícita, um post só). Posts orgânicos ficam False em tudo."""
    patrocinado = df["is_sponsored"].astype(bool)
    posts_por_patrocinador = df.loc[patrocinado, "sponsor_name"].value_counts()
    marcas = pd.DataFrame(
        {
            "sem_fit": marcar_fit(df).eq(False).fillna(False).astype(bool),
            "implicita": patrocinado & (df["disclosure_type"] == "implicit"),
            "so_hashtag": patrocinado & (df["disclosure_location"] == "hashtags"),
            "um_post_so": patrocinado & (df["sponsor_name"].map(posts_por_patrocinador) == 1),
        },
        index=df.index,
    )
    marcas["algum_problema"] = marcas["sem_fit"] | marcas["implicita"] | marcas["um_post_so"]
    return marcas


def resumo_semanas(df):
    """Uma linha por semana: dias com post, data do último post, posts, patrocinados e quantos
    patrocinados têm cada problema."""
    base = marcar_problemas(df).astype(int).assign(
        semana=semana(df["post_date"]),
        dia=df["post_date"].dt.normalize(),
        data=df["post_date"],
        posts=1,
        patrocinados=df["is_sponsored"].astype(int),
    )
    tabela = base.groupby("semana").agg(
        dias=("dia", "nunique"),
        ultimo_post=("data", "max"),
        posts=("posts", "sum"),
        patrocinados=("patrocinados", "sum"),
        sem_fit=("sem_fit", "sum"),
        implicita=("implicita", "sum"),
        so_hashtag=("so_hashtag", "sum"),
        um_post_so=("um_post_so", "sum"),
        algum_problema=("algum_problema", "sum"),
    )
    return tabela.reset_index()


def resumo_semanas_grupos(df, metrica="engajamento"):
    """Por semana e grupo (cada valor de plataforma, formato e categoria): posts, média e variância
    da métrica. Uma linha 'total' por semana guarda os números de todos os posts da semana."""
    base = df.assign(semana=semana(df["post_date"]), _valor=df[metrica].astype("float64"))
    partes = [
        base.groupby(["semana", coluna], observed=True)["_valor"]
        .agg(n="count", media="mean", var="var")
        .reset_index()
        .rename(columns={coluna: "valor"})
        .assign(dimensao=coluna)
        for coluna in DIMENSOES_GRUPO
    ]
    total = (
        base.groupby("semana")["_valor"].agg(n="count", media="mean", var="var").reset_index()
        .assign(dimensao="total", valor="total")
    )
    return pd.concat(partes + [total], ignore_index=True)[["semana", "dimensao", "valor", "n", "media", "var"]]


def resumo_celulas(df):
    """O mapa de células de cada objetivo, empilhado, com a coluna 'objetivo'."""
    return pd.concat(
        [mapa_celulas(df, DIMENSOES_CELULA, metrica=coluna).assign(objetivo=nome) for nome, coluna in OBJETIVOS.items()],
        ignore_index=True,
    )


def resumo_laudo(df):
    """Os números que a tela Saúde do dado mostra, como pares chave e valor."""
    patrocinados = df[df["is_sponsored"].astype(bool)]
    marcas = marcar_problemas(df).loc[patrocinados.index]
    seguidores = variacao_seguidores(df)
    parcela_conteudo = df["content_category"].value_counts(normalize=True)
    fit_sorteio = patrocinados["sponsor_category"].map(
        lambda s: parcela_conteudo.reindex(sorted(FIT_PATROCINIO.get(s, set())), fill_value=0).sum()
    ).mean()
    por_patrocinador = patrocinados["sponsor_name"].value_counts()
    lingua = df[df["language"].isin(LINGUAS_NAO_LATINAS)]
    valores = {
        "posts": len(df),
        "indice_views": indice_dispersao(df["views"]),
        "indice_likes": indice_dispersao(df["likes"]),
        "indice_shares": indice_dispersao(df["shares"]),
        "indice_comentarios": indice_dispersao(df["comments_count"]),
        "creators": len(seguidores),
        "creators_seguidores_variam": (seguidores["razao"] > 1).mean(),
        "razao_seguidores_mediana": seguidores["razao"].median(),
        "corr_seguidores_views": df["follower_count"].corr(df["views"]),
        "patrocinados": len(patrocinados),
        "fit": 1 - marcas["sem_fit"].mean(),
        "fit_sorteio": fit_sorteio,
        "implicita": marcas["implicita"].mean(),
        "so_hashtag": marcas["so_hashtag"].mean(),
        "patrocinadores": len(por_patrocinador),
        "patrocinadores_um_post": (por_patrocinador == 1).mean(),
        "posts_lingua_nao_latina": len(lingua),
        "posts_lingua_com_escrita": int(lingua["content_description"].map(usa_escrita_nao_latina).sum()),
    }
    valores.update({f"formato_{k}": v for k, v in df["content_type"].value_counts(normalize=True).items()})
    valores.update({f"categoria_{k}": v for k, v in df["content_category"].value_counts(normalize=True).items()})
    return pd.DataFrame({"chave": list(valores), "valor": [float(v) for v in valores.values()]})
