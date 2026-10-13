"""OS-01 - Base amostral: descricao da base (tamanho, qualidade, distribuicoes, volume)."""

import os
import re
from pathlib import Path

import numpy as np
import pandas as pd

np.random.seed(42)

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
DATA_PATH = Path(os.environ.get("DATA_PATH", REPO_ROOT / "datasets" / "social_media_dataset.csv"))
OUT_DIR = SCRIPT_DIR.parent / "outputs" / "os01"
OUT_DIR.mkdir(parents=True, exist_ok=True)

METRICAS = ["views", "likes", "shares", "comments_count", "follower_count",
            "engajamento", "taxa_engajamento"]

SEGMENTOS = ["platform", "content_type", "content_category", "language", "is_sponsored",
             "disclosure_type", "disclosure_location", "sponsor_category",
             "audience_age_distribution", "audience_gender_distribution", "audience_location"]

FAIXA_SEG_BINS = [0, 10_000, 50_000, 100_000, 500_000, 1_000_000]
FAIXA_SEG_LABELS = ["1-10K", "10-50K", "50-100K", "100-500K", "500K-1M"]
FAIXA_DUR_BINS = [0, 30, 60, 180, np.inf]
FAIXA_DUR_LABELS = ["<30", "30-60", "60-180", ">180"]


def salvar(df, nome):
    df.to_csv(OUT_DIR / nome, index=False)
    print(f"  -> {nome} ({len(df)} linhas)")


# ---------------------------------------------------------------- carga
df = pd.read_csv(DATA_PATH)
COLS_ORIGINAIS = list(df.columns)  # secao 1 descreve a base, nao as colunas derivadas
df["post_date"] = pd.to_datetime(df["post_date"], format="%m/%d/%y %I:%M %p")
df["engajamento"] = df["likes"] + df["shares"] + df["comments_count"]
df["taxa_engajamento"] = df["engajamento"] / df["views"]
df["faixa_seguidores"] = pd.cut(df["follower_count"], bins=FAIXA_SEG_BINS,
                                labels=FAIXA_SEG_LABELS, right=True)
# faixa de duracao usa content_length e so vale para video
df["faixa_duracao"] = pd.cut(df["content_length"], bins=FAIXA_DUR_BINS,
                             labels=FAIXA_DUR_LABELS, right=True)
df.loc[df["content_type"] != "video", "faixa_duracao"] = np.nan

print(f"Base: {df.shape[0]} linhas x {df.shape[1]} colunas (origem: {DATA_PATH})")

# ---------------------------------------------------------------- 1. visao geral
print("\n[1] Visao geral")

orig = df[COLS_ORIGINAIS]

tipos = pd.DataFrame({"coluna": COLS_ORIGINAIS, "tipo": [str(t) for t in orig.dtypes]})
salvar(tipos, "01_tipos_colunas.csv")

nulos = pd.DataFrame({
    "coluna": COLS_ORIGINAIS,
    "nulos": orig.isna().sum().values,
    "pct_nulos": (orig.isna().sum().values / len(df) * 100).round(4),
})
salvar(nulos, "01_nulos_por_coluna.csv")

geral = pd.DataFrame([
    ("linhas", df.shape[0]),
    ("colunas", len(COLS_ORIGINAIS)),
    ("duplicatas_id", int(df["id"].duplicated().sum())),
    ("duplicatas_content_id", int(df["content_id"].duplicated().sum())),
    ("ids_unicos", int(df["id"].nunique())),
    ("content_ids_unicos", int(df["content_id"].nunique())),
    ("creator_ids_unicos", int(df["creator_id"].nunique())),
    ("post_date_min", df["post_date"].min()),
    ("post_date_max", df["post_date"].max()),
    ("posts_engajamento_zero", int((df["engajamento"] == 0).sum())),
    ("posts_views_zero", int((df["views"] == 0).sum())),
], columns=["indicador", "valor"])
salvar(geral, "01_visao_geral.csv")

# ---------------------------------------------------------------- 2. distribuicao das metricas
print("\n[2] Distribuicao das metricas")

linhas = []
for c in METRICAS:
    s = df[c].astype(float)
    media = s.mean()
    linhas.append({
        "metrica": c,
        "minimo": s.min(),
        "p1": s.quantile(0.01),
        "p25": s.quantile(0.25),
        "mediana": s.median(),
        "p75": s.quantile(0.75),
        "p99": s.quantile(0.99),
        "maximo": s.max(),
        "media": media,
        "desvio_padrao": s.std(),
        "coef_variacao": s.std() / media if media else np.nan,
    })
dist = pd.DataFrame(linhas)
salvar(dist, "02_distribuicao_metricas.csv")

# ---------------------------------------------------------------- 3. volume por segmento
print("\n[3] Volume por segmento")

blocos = []
for c in SEGMENTOS + ["faixa_seguidores", "faixa_duracao"]:
    # faixa_duracao so existe para video: pct relativo aos posts de video
    sub = df[df["content_type"] == "video"] if c == "faixa_duracao" else df
    vc = sub[c].value_counts(dropna=False)
    base = vc.sum()
    b = pd.DataFrame({
        "variavel": c,
        "valor": vc.index.astype(str),
        "n": vc.values,
        "pct": (vc.values / base * 100).round(4),
    })
    blocos.append(b)
volume = pd.concat(blocos, ignore_index=True)
salvar(volume, "03_volume_por_segmento.csv")

# content_length por content_type: verifica se o campo se comporta como duracao de video
cl = df.groupby("content_type")["content_length"].agg(
    n="size", minimo="min", p25=lambda s: s.quantile(0.25), mediana="median",
    p75=lambda s: s.quantile(0.75), maximo="max", media="mean", desvio="std").reset_index()
salvar(cl, "03_content_length_por_content_type.csv")

# ---------------------------------------------------------------- 4. tamanho dos cruzamentos
print("\n[4] Tamanho dos cruzamentos")

CRUZAMENTOS = {
    "A_platform_x_content_type_x_content_category_x_faixa_seguidores":
        ["platform", "content_type", "content_category", "faixa_seguidores"],
    "B_platform_x_content_category_x_faixa_seguidores_x_is_sponsored":
        ["platform", "content_category", "faixa_seguidores", "is_sponsored"],
}

resumos = []
for nome, cols in CRUZAMENTOS.items():
    g = df.groupby(cols, observed=True).size().reset_index(name="n")
    g = g[g["n"] > 0].sort_values("n", ascending=False)
    salvar(g, f"04_cruzamento_{nome[0]}_detalhe.csv")
    resumos.append({
        "cruzamento": nome,
        "combinacoes_existentes": len(g),
        "n_maior_igual_100": int((g["n"] >= 100).sum()),
        "n_entre_30_e_99": int(g["n"].between(30, 99).sum()),
        "n_menor_30": int((g["n"] < 30).sum()),
        "n_minimo": int(g["n"].min()),
        "n_mediano": float(g["n"].median()),
        "n_maximo": int(g["n"].max()),
    })
cruz = pd.DataFrame(resumos)
salvar(cruz, "04_cruzamentos_resumo.csv")

# ---------------------------------------------------------------- 5. consistencia
print("\n[5] Consistencia")

nao_patro = df[~df["is_sponsored"]]
patro = df[df["is_sponsored"]]
incons = pd.DataFrame([
    ("nao_patrocinados_total", len(nao_patro)),
    ("nao_patrocinados_com_disclosure_diferente_de_none",
     int((nao_patro["disclosure_type"] != "none").sum())),
    ("nao_patrocinados_com_sponsor_category_diferente_de_not_sponsors",
     int((nao_patro["sponsor_category"] != "Not sponsors").sum())),
    ("patrocinados_total", len(patro)),
    ("patrocinados_com_disclosure_none",
     int((patro["disclosure_type"] == "none").sum())),
], columns=["indicador", "valor"])
salvar(incons, "05_consistencia_patrocinio.csv")

# por creator: plataformas distintas e variacao de follower_count
g = df.groupby("creator_id")
creators = pd.DataFrame({
    "creator_id": g.size().index,
    "posts": g.size().values,
    "plataformas_distintas": g["platform"].nunique().values,
    "follower_min": g["follower_count"].min().values,
    "follower_max": g["follower_count"].max().values,
})
creators["follower_dif"] = creators["follower_max"] - creators["follower_min"]
salvar(creators, "05_creators_detalhe.csv")

plat_dist = creators["plataformas_distintas"].value_counts().sort_index()
salvar(pd.DataFrame({"plataformas_distintas": plat_dist.index, "creators": plat_dist.values}),
       "05_creators_plataformas_distribuicao.csv")

res_creators = pd.DataFrame([
    ("creators_total", len(creators)),
    ("creators_com_follower_count_variavel", int((creators["follower_dif"] > 0).sum())),
    ("follower_dif_minimo", int(creators["follower_dif"].min())),
    ("follower_dif_mediano", float(creators["follower_dif"].median())),
    ("follower_dif_maximo", int(creators["follower_dif"].max())),
], columns=["indicador", "valor"])
salvar(res_creators, "05_creators_resumo.csv")

# comments_text nao tem separador de comentarios: checagem dos candidatos
s_txt = df["comments_text"].dropna()
sep = pd.DataFrame([
    ("linhas_com_texto_nao_nulo", len(s_txt)),
    ("contem_pipe", int(s_txt.str.contains(r"\|", regex=True).sum())),
    ("contem_ponto_e_virgula", int(s_txt.str.contains(";", regex=False).sum())),
    ("contem_quebra_de_linha", int(s_txt.str.contains("\n", regex=False).sum())),
    ("contem_tab", int(s_txt.str.contains("\t", regex=False).sum())),
], columns=["indicador", "valor"])
salvar(sep, "05_comments_text_separadores.csv")

# comments_count vs numero de comentarios em comments_text (so medianas)
n_frases = df["comments_text"].fillna("").apply(
    lambda t: len([p for p in re.split(r"[.!?]+", t) if p.strip()]))
cmp_coment = pd.DataFrame([
    ("mediana_comments_count_todas_linhas", float(df["comments_count"].median())),
    ("mediana_comentarios_em_comments_text_todas_linhas", float(n_frases.median())),
    ("mediana_comments_count_texto_nao_nulo",
     float(df.loc[df["comments_text"].notna(), "comments_count"].median())),
    ("mediana_comentarios_em_comments_text_texto_nao_nulo",
     float(n_frases[df["comments_text"].notna()].median())),
], columns=["indicador", "valor"])
salvar(cmp_coment, "05_comments_count_vs_texto.csv")

# ---------------------------------------------------------------- 6. relacao entre metricas
print("\n[6] Relacao entre metricas")

COLS_CORR = ["follower_count", "views", "likes", "shares", "comments_count", "engajamento"]
corr = df[COLS_CORR].corr(method="spearman").round(4).reset_index().rename(
    columns={"index": "metrica"})
salvar(corr, "06_correlacao_spearman.csv")

med_faixa = df.groupby("faixa_seguidores", observed=True).agg(
    n=("id", "size"),
    mediana_views=("views", "median"),
    mediana_engajamento=("engajamento", "median"),
).reset_index()
salvar(med_faixa, "06_medianas_por_faixa_seguidores.csv")

print(f"\nPronto. Saidas em {OUT_DIR}")
