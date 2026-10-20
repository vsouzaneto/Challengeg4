"""Deep dive on four relations with views: content_category, content_description, follower_count, is_sponsored.

Each function returns an Answer with effect sizes, confidence intervals and the minimum detectable effect (MDE):
a null result only means "no effect" when the MDE is small enough to have caught a business-relevant one.
"""
from itertools import combinations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score
from statsmodels.stats.multitest import multipletests

from . import nlp
from .questions import ALPHA, STRATA, Answer, stratified_difference

TARGET = "views"
Z_POWER = stats.norm.ppf(1 - ALPHA / 2) + stats.norm.ppf(0.80)  # 80% power, two-sided α = 5% → ≈ 2.80
SEED = 42
MAX_TERMS = 5_000
RIDGE_ALPHAS = [1.0, 10.0, 100.0]


# ---------- power ----------

def mde_two_groups(sd: float, n1: int, n2: int) -> float:
    """Smallest mean difference detectable with 80% power (two-sided, α = 5%)."""
    return Z_POWER * sd * np.sqrt(1 / n1 + 1 / n2)


def mde_correlation(n: int) -> float:
    """Smallest correlation detectable with 80% power (Fisher z approximation)."""
    return float(np.tanh(Z_POWER / np.sqrt(n - 3)))


def _mean_ci(values: pd.Series) -> tuple[float, float, float]:
    m, se = values.mean(), values.std() / np.sqrt(len(values))
    return m, m - 1.96 * se, m + 1.96 * se


# ---------- 1. content_category × views ----------

def category_vs_views(df: pd.DataFrame, target: str = TARGET) -> Answer:
    overall_sd = df[target].std()
    rows = []
    for cat, g in df.groupby("content_category"):
        m, lo, hi = _mean_ci(g[target])
        rows.append({"categoria": cat, "posts": len(g), "média": m, "IC95 inf": lo, "IC95 sup": hi, "mediana": g[target].median(),
                     "p10": g[target].quantile(0.1), "p90": g[target].quantile(0.9)})
    table = pd.DataFrame(rows).set_index("categoria")
    h, p = stats.kruskal(*[g[target].values for _, g in df.groupby("content_category")])

    pairs = []
    for a, b in combinations(table.index, 2):
        va, vb = df.loc[df.content_category == a, target], df.loc[df.content_category == b, target]
        pairs.append({"par": f"{a} vs {b}", "diferença (views)": va.mean() - vb.mean(), "diferença (%)": (va.mean() / vb.mean() - 1) * 100,
                      "p_value": stats.ttest_ind(va, vb, equal_var=False).pvalue, "MDE (views)": mde_two_groups(overall_sd, len(va), len(vb))})
    pairs = pd.DataFrame(pairs)
    pairs["q_value"] = multipletests(pairs["p_value"], method="fdr_bh")[1]

    within = df.pivot_table(target, "platform", "content_category", aggfunc="mean")
    within = within.div(within.mean(axis=1), axis=0) * 100 - 100
    spread = table["média"].max() - table["média"].min()
    mde = pairs["MDE (views)"].max()
    verdict = (f"Categoria não muda as views: diferença máxima de {spread:.1f} views ({spread / df[target].mean():.3%}) entre categorias "
               f"(Kruskal p={p:.2f}, ε²={h / (len(df) - 1):.5f}). Os dados detectariam diferenças a partir de ~{mde:.0f} views "
               f"({mde / df[target].mean():.2%}), então um efeito de negócio relevante (ex.: 5%) teria aparecido.")
    return Answer("content_category × views", verdict, table,
                  {"Comparações par a par": pairs, "Dentro de cada plataforma (% vs. média da plataforma)": within})


# ---------- 2. content_description × views ----------

def description_features(df: pd.DataFrame) -> pd.DataFrame:
    text = df["content_description"].fillna("")
    return pd.DataFrame({"palavras": text.str.split().str.len(), "caracteres": text.str.len(),
                         "sentimento": nlp.sentiment(text).fillna(0),
                         "tem pergunta": text.str.contains(r"\?"), "tem exclamação": text.str.contains("!")}, index=df.index)


def tfidf_cv_r2(texts: pd.Series, y: pd.Series, folds: int = 5) -> dict:
    """Can the words of the caption predict views? Ridge on TF-IDF (uni+bigrams), CV R² (0 = no better than the mean)."""
    X = TfidfVectorizer(tokenizer=nlp.tokenize, lowercase=False, token_pattern=None, ngram_range=(1, 2), min_df=5,
                        max_features=MAX_TERMS).fit_transform(texts.fillna(""))
    scores = {alpha: cross_val_score(Ridge(alpha=alpha, solver="sparse_cg"), X, y, cv=folds, scoring="r2") for alpha in RIDGE_ALPHAS}
    best = max(scores, key=lambda a: scores[a].mean())
    return {"vocabulário": X.shape[1], "alpha": best, "R² médio": scores[best].mean(), "R² desvio": scores[best].std()}


def description_vs_views(df: pd.DataFrame, target: str = TARGET) -> Answer:
    feats = description_features(df)
    numeric = []
    for col in ["palavras", "caracteres", "sentimento"]:
        rho, p = stats.spearmanr(feats[col], df[target])
        numeric.append({"característica": col, "ρ Spearman": rho, "p_value": p, "MDE ρ": mde_correlation(len(df))})
    for col in ["tem pergunta", "tem exclamação"]:
        if feats[col].nunique() < 2:  # no variation → nothing to test
            continue
        a, b = df.loc[feats[col], target], df.loc[~feats[col], target]
        numeric.append({"característica": col, "ρ Spearman": np.nan, "diferença (views)": a.mean() - b.mean() if len(a) else np.nan,
                        "p_value": stats.ttest_ind(a, b, equal_var=False).pvalue if len(a) > 1 else np.nan,
                        "MDE (views)": mde_two_groups(df[target].std(), len(a), len(b)) if len(a) else np.nan, "posts com": len(a)})
    numeric = pd.DataFrame(numeric).set_index("característica")

    top, bottom = df[target] >= df[target].quantile(0.9), df[target] <= df[target].quantile(0.1)
    keywords = nlp.log_odds_keywords(df.loc[top, "content_description"].fillna(""), df.loc[bottom, "content_description"].fillna(""), top_n=10)
    model = tfidf_cv_r2(df["content_description"], df[target])
    by_length = df.groupby(pd.qcut(feats["palavras"], 5, duplicates="drop"), observed=True)[target].agg(["size", "mean", "median"])
    by_length.index = by_length.index.astype(str)

    significant_words = int((keywords["z"].abs() > 1.96).sum())
    verdict = (f"A legenda não muda as views. Tamanho e sentimento têm |ρ| ≤ {numeric['ρ Spearman'].abs().max():.3f} "
               f"(detectável a partir de {mde_correlation(len(df)):.3f}). {significant_words} palavras distinguem posts de muitas e poucas views "
               f"(|z| > 1,96), e um modelo de texto (TF-IDF + Ridge, {model['vocabulário']:,} termos) tem R² = {model['R² médio']:.4f}. "
               "Os textos são frases aleatórias, sem relação com o tema do post.")
    return Answer("content_description × views", verdict, numeric,
                  {"Palavras mais típicas: top 10% vs. bottom 10% de views": keywords,
                   "Modelo de texto (TF-IDF + Ridge)": pd.DataFrame([model]),
                   "Views por quintil de tamanho da legenda (palavras)": by_length})


# ---------- 3. follower_count × views ----------

def followers_vs_views(df: pd.DataFrame, target: str = TARGET) -> Answer:
    x, y = df["follower_count"], df[target]
    rho, p_rho = stats.spearmanr(x, y)
    r, p_r = stats.pearsonr(x, y)
    ols = sm.OLS(y, sm.add_constant(x / 100_000)).fit()
    loglog = sm.OLS(np.log(y), sm.add_constant(np.log(x))).fit()
    slope, (s_lo, s_hi) = ols.params.iloc[1], ols.conf_int().iloc[1]
    elast, (e_lo, e_hi) = loglog.params.iloc[1], loglog.conf_int().iloc[1]
    stats_table = pd.DataFrame({
        "valor": [rho, r, slope, elast, mde_correlation(len(df))],
        "IC95 inf": [np.nan, np.nan, s_lo, e_lo, np.nan], "IC95 sup": [np.nan, np.nan, s_hi, e_hi, np.nan],
        "p_value": [p_rho, p_r, ols.pvalues.iloc[1], loglog.pvalues.iloc[1], np.nan],
    }, index=["ρ Spearman", "r Pearson", "views a mais por +100 mil seguidores", "elasticidade (log-log)", "MDE ρ (80% de poder)"])
    deciles = df.groupby(pd.qcut(x, 10), observed=True)[target].agg(["size", "mean", "median"])
    deciles.index = [f"{iv.left:,.0f}–{iv.right:,.0f}" for iv in deciles.index]
    views_per_follower = (y / x).describe(percentiles=[0.1, 0.5, 0.9]).to_frame("views por seguidor")
    verdict = (f"Seguidores não trazem views: ρ = {rho:.4f} (detectável a partir de {mde_correlation(len(df)):.3f}). "
               f"Cada +100 mil seguidores somam {slope:+.2f} views (IC95 {s_lo:+.2f} a {s_hi:+.2f}), e a elasticidade é {elast:.4f}, ou seja, "
               f"dobrar a base muda as views em {(2 ** elast - 1):+.3%}. Um creator de 5 mil e um de 1 milhão têm a mesma mediana de views. "
               "Nas redes reais, a elasticidade costuma ficar entre 0,5 e 1, então isso é atípico.")
    return Answer("follower_count × views", verdict, stats_table,
                  {"Views por decil de seguidores": deciles, "Views por seguidor (alcance relativo)": views_per_follower})


# ---------- 4. is_sponsored × views ----------

def sponsorship_vs_views(df: pd.DataFrame, target: str = TARGET) -> Answer:
    sponsored = df["is_sponsored"].astype(bool)
    a, b = df.loc[sponsored, target], df.loc[~sponsored, target]
    diff = a.mean() - b.mean()
    se = np.sqrt(a.var() / len(a) + b.var() / len(b))
    raw = {"diferença (views)": diff, "IC95 inf": diff - 1.96 * se, "IC95 sup": diff + 1.96 * se, "diferença (%)": diff / b.mean() * 100,
           "p_value": stats.ttest_ind(a, b, equal_var=False).pvalue, "MDE (views)": mde_two_groups(df[target].std(), len(a), len(b))}
    strat = stratified_difference(df, sponsored, target, STRATA)
    overview = pd.DataFrame({"bruta": raw, "estratificada (plataforma × formato × categoria × porte)": {
        "diferença (views)": strat["diferença"], "IC95 inf": strat["IC95 inf"], "IC95 sup": strat["IC95 sup"],
        "diferença (%)": strat["diferença (%)"], "p_value": strat["p_value"], "MDE (views)": raw["MDE (views)"]}}).T

    rows = []
    for dim in ["follower_tier", "platform", "content_category", "sponsor_category", "disclosure_type"]:
        for value, g in df.groupby(dim, observed=True):
            if dim in ("sponsor_category", "disclosure_type"):
                t, c = g[target], b  # sponsored subgroup vs. all organic
                if value in ("Not sponsors", "none"):
                    continue
            else:
                t, c = g.loc[g.is_sponsored.astype(bool), target], g.loc[~g.is_sponsored.astype(bool), target]
            if len(t) < 30 or len(c) < 30:
                continue
            d = t.mean() - c.mean()
            s = np.sqrt(t.var() / len(t) + c.var() / len(c))
            rows.append({"condição": f"{dim} = {value}", "patrocinados": len(t), "diferença (views)": d,
                         "IC95 inf": d - 1.96 * s, "IC95 sup": d + 1.96 * s, "p_value": stats.ttest_ind(t, c, equal_var=False).pvalue})
    by_condition = pd.DataFrame(rows)
    by_condition["q_value"] = multipletests(by_condition["p_value"], method="fdr_bh")[1]
    verdict = (f"Patrocínio não traz views: {diff:+.1f} views ({raw['diferença (%)']:+.3f}%, IC95 {raw['IC95 inf']:+.1f} a {raw['IC95 sup']:+.1f}); "
               f"estratificado: {strat['diferença']:+.1f} views. Os dados detectariam diferenças a partir de ~{raw['MDE (views)']:.1f} views "
               f"({raw['MDE (views)'] / b.mean():.3%}). {int((by_condition['q_value'] < ALPHA).sum())} de {len(by_condition)} condições "
               "(porte, plataforma, categoria, patrocinador, disclosure) com efeito.")
    return Answer("is_sponsored × views", verdict, overview, {"Por condição": by_condition.sort_values("diferença (views)", ascending=False)})


def focus_all(df: pd.DataFrame) -> list[Answer]:
    return [category_vs_views(df), description_vs_views(df), followers_vs_views(df), sponsorship_vs_views(df)]
