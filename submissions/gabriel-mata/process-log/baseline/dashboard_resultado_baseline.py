"""
Challenge 004 — Análise de performance de social media (pipeline reprodutível)

Uso:
    pip install pandas numpy scipy scikit-learn
    python analise_social_media.py social_media_dataset.csv

Roda, em ordem:
  1. Testes de sanidade (o dado se comporta como dado real?)
  2. Engajamento por dimensão (ANOVA + tamanho do efeito)
  3. Patrocinado vs orgânico estratificado (plataforma × categoria × formato × faixa)
  4. Validação de "top segmentos" em dados não vistos (armadilha de múltiplas comparações)
  5. Hashtags com correção de testes múltiplos (Benjamini-Hochberg)
  6. Modelo preditivo de engajamento (gradient boosting vs baseline da média)

Funciona com qualquer exportação que tenha as mesmas colunas.
"""
import sys
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

FAIXAS = [0, 10e3, 50e3, 100e3, 500e3, np.inf]
ROTULOS = ["<10K", "10K-50K", "50K-100K", "100K-500K", "500K+"]
DIMENSOES = ["platform", "content_type", "content_category", "faixa", "is_sponsored", "language",
             "audience_age_distribution", "audience_gender_distribution", "audience_location",
             "disclosure_type", "sponsor_category", "disclosure_location", "hora", "dia_semana", "n_hashtags"]


def carregar(caminho):
    df = pd.read_csv(caminho)
    df["data"] = pd.to_datetime(df["post_date"], format="mixed")
    df["interacoes"] = df.likes + df.shares + df.comments_count
    df["er"] = 100 * df.interacoes / df.views  # engajamento sobre views, nunca sobre seguidores
    df["faixa"] = pd.cut(df.follower_count, FAIXAS, labels=ROTULOS)
    df["hora"] = df.data.dt.hour
    df["dia_semana"] = df.data.dt.dayofweek
    df["n_hashtags"] = df.hashtags.fillna("").apply(lambda s: 0 if s == "" else len(s.split(",")))
    return df


def sanidade(df):
    inter = df.interacoes.sort_values().values
    testes = [
        ("Correlação likes × views", df.likes.corr(df.views), "> 0,5", lambda v: v > 0.5),
        ("Correlação log(seguidores) × log(views)", np.log10(df.follower_count).corr(np.log10(df.views)), "> 0,3", lambda v: v > 0.3),
        ("Dispersão das views (variância ÷ média)", df.views.var() / df.views.mean(), "> 10", lambda v: v > 10),
        ("% creators em uma só plataforma", 100 * (df.groupby("creator_id").platform.nunique() == 1).mean(), "> 90", lambda v: v > 90),
        ("Post percentil 1 ÷ mediana (interações)", inter[int(len(inter) * .01)] / np.median(inter), "< 0,2", lambda v: v < 0.2),
    ]
    out = pd.DataFrame([(n, round(v, 3), ref, "OK" if ok(v) else "REPROVADO") for n, v, ref, ok in testes],
                       columns=["teste", "valor", "esperado", "status"])
    return out


def por_dimensao(df):
    media = df.er.mean()
    linhas = []
    for d in DIMENSOES:
        grupos = [g.er.values for _, g in df.groupby(d, observed=True)]
        medias = df.groupby(d, observed=True).er.mean()
        F, p = stats.f_oneway(*grupos)
        linhas.append((d, len(grupos), round(100 * (medias.max() - medias.min()) / media, 2), round(p, 4),
                       medias.idxmax(), "SINAL" if p < 0.05 / len(DIMENSOES) else "ruído"))
    return pd.DataFrame(linhas, columns=["dimensao", "grupos", "dif_max_%_media", "p_valor", "melhor_grupo", "leitura"]) \
        .sort_values("dif_max_%_media", ascending=False)


def patrocinio_estratificado(df, min_n=20):
    partes = []
    for _, x in df.groupby(["platform", "content_category", "content_type", "faixa"], observed=True):
        a, b = x[x.is_sponsored].er, x[~x.is_sponsored].er
        if len(a) >= min_n and len(b) >= min_n:
            partes.append((len(x), a.mean() - b.mean(), a.var() / len(a) + b.var() / len(b)))
    r = np.array(partes)
    w = r[:, 0] / r[:, 0].sum()
    dif, ep = (w * r[:, 1]).sum(), np.sqrt((w ** 2 * r[:, 2]).sum())
    return {"diferenca_pp": round(dif, 4), "ic95": (round(dif - 1.96 * ep, 4), round(dif + 1.96 * ep, 4)), "estratos": len(r)}


def validar_top_segmentos(df, metrica="shares", repeticoes=30, top=10, min_n=30):
    seg = ["platform", "content_type", "content_category", "faixa", "audience_age_distribution"]
    lifts_desc, lifts_val, corrs = [], [], []
    for s in range(repeticoes):
        idx = np.random.default_rng(s).permutation(len(df))
        a, b = df.iloc[idx[: len(df) // 2]], df.iloc[idx[len(df) // 2:]]
        ga = a.groupby(seg, observed=True)[metrica].agg(["size", "mean"])
        gb = b.groupby(seg, observed=True)[metrica].agg(["size", "mean"])
        j = ga.join(gb, lsuffix="_a", rsuffix="_b", how="inner")
        j = j[(j.size_a >= min_n) & (j.size_b >= min_n)]
        t = j.sort_values("mean_a", ascending=False).head(top)
        lifts_desc.append(100 * (t.mean_a / a[metrica].mean() - 1).mean())
        lifts_val.append(100 * (t.mean_b / b[metrica].mean() - 1).mean())
        corrs.append(np.corrcoef(j.mean_a, j.mean_b)[0, 1])
    return {"lift_top_descoberta_%": round(np.mean(lifts_desc), 2), "lift_top_validacao_%": round(np.mean(lifts_val), 2),
            "correlacao_descoberta_validacao": round(np.mean(corrs), 3)}


def hashtags_fdr(df, min_posts=100, alfa=0.05):
    ex = df[["er", "hashtags"]].assign(tag=df.hashtags.fillna("").str.split(",")).explode("tag")
    ex = ex[ex.tag != ""]
    contagem = ex.tag.value_counts()
    tags = contagem[contagem >= min_posts].index
    p = np.array([stats.ttest_ind(ex[ex.tag == t].er, df.er).pvalue for t in tags])
    ordem = np.sort(p)
    bh = ordem <= np.arange(1, len(p) + 1) / len(p) * alfa
    return {"hashtags_testadas": len(p), "p<0,05_sem_correcao": int((p < alfa).sum()),
            "esperado_por_acaso": round(len(p) * alfa, 1), "significativas_apos_BH": int(np.max(np.where(bh)[0]) + 1) if bh.any() else 0}


def modelo_preditivo(df, alvo="er"):
    X = df[["hora", "dia_semana", "content_length", "n_hashtags"]].copy()
    X["log_seguidores"] = np.log10(df.follower_count)
    X["patrocinado"] = df.is_sponsored.astype(int)
    X["mes"] = df.data.dt.month
    cat = ["platform", "content_type", "content_category", "language", "audience_age_distribution",
           "audience_gender_distribution", "audience_location", "disclosure_type", "sponsor_category", "disclosure_location"]
    X = X.join(pd.get_dummies(df[cat]).astype(int))
    Xtr, Xte, ytr, yte = train_test_split(X, df[alvo], test_size=0.25, random_state=0)
    m = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, random_state=0).fit(Xtr, ytr)
    p = m.predict(Xte)
    return m, {"alvo": alvo, "R2_teste": round(r2_score(yte, p), 4), "MAE_modelo": round(mean_absolute_error(yte, p), 3),
               "MAE_baseline_media": round(mean_absolute_error(yte, np.full(len(yte), ytr.mean())), 3)}


if __name__ == "__main__":
    df = carregar(sys.argv[1] if len(sys.argv) > 1 else "social_media_dataset.csv")
    print(f"\n{len(df):,} posts de {df.data.min():%d/%m/%Y} a {df.data.max():%d/%m/%Y}\n")
    print("1. TESTES DE SANIDADE\n", sanidade(df).to_string(index=False), "\n")
    print("2. ENGAJAMENTO POR DIMENSÃO\n", por_dimensao(df).to_string(index=False), "\n")
    print("3. PATROCÍNIO ESTRATIFICADO\n", patrocinio_estratificado(df), "\n")
    print("4. VALIDAÇÃO DE TOP SEGMENTOS (shares)\n", validar_top_segmentos(df), "\n")
    print("5. HASHTAGS (com correção de testes múltiplos)\n", hashtags_fdr(df), "\n")
    for alvo in ["er", "shares", "views"]:
        print("6. MODELO PREDITIVO\n", modelo_preditivo(df, alvo)[1])
    print("\nLeitura: modelo só vale ser usado se R2_teste > 0,1 e MAE_modelo claramente menor que o baseline.")
