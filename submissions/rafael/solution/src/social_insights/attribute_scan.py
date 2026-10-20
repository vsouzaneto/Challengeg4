"""Scans every attribute of the dataset against each target metric with the test that fits its type.

All effects are reported on one scale — share of the target's variance explained (%) — plus a business effect
(% gap: best vs. worst group, or top vs. bottom quintile), the minimum detectable gap in the same unit (MDE) and
Benjamini-Hochberg q-values across the whole scan.
"""
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

from .focus import mde_two_groups, tfidf_cv_r2
from .questions import ALPHA

TARGETS = ["views", "likes", "comments_count"]
CATEGORICAL = ["platform", "content_type", "content_category", "language", "is_sponsored", "disclosure_type",
               "disclosure_location", "sponsor_category", "audience_gender_distribution", "audience_age_distribution",
               "audience_location", "follower_tier", "length_bin", "daypart", "weekday", "month", "url_tld", "url_https"]
NUMERIC = ["follower_count", "content_length", "n_hashtags", "hour", "post_day", "caption_words",
           "comment_sentences", "views", "likes", "shares", "comments_count"]
HIGH_CARDINALITY = ["creator_id"]
TEXT = ["content_description", "hashtags", "comments_text"]
SKIPPED = {
    "content_id": "identificador único por post (sem grupos para comparar)",
    "id": "sequencial na ordem cronológica: equivale a post_day (testado)",
    "creator_name": "muda a cada post do mesmo creator (~10 nomes por creator_id)",
    "sponsor_name": "1,2 post por patrocinador em média (grupos pequenos demais)",
    "content_url": "texto de URL gerado; testado via url_tld e url_https",
    "interactions / eng_rate_views": "derivados das próprias métricas-alvo (vazamento)",
}
QUINTILES = 5


def attribute_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Adds the derived attributes used by the scan."""
    out = df.copy()
    out["post_day"] = (out["post_date"] - out["post_date"].min()).dt.days
    out["month"] = out["post_date"].dt.month_name()
    out["url_tld"] = out["content_url"].str.extract(r"\.([a-z]+)/?$")[0].fillna("outro")
    out["url_https"] = out["content_url"].str.startswith("https")
    out["comment_sentences"] = out["comments_text"].fillna("").str.count(r"[.!?](\s|$)")
    out["hashtags"] = out["hashtags"].fillna("").str.replace(",", " ")
    return out


def _categorical(df: pd.DataFrame, col: str, target: str) -> dict:
    groups = df.groupby(col, observed=True)[target]
    values = [g.values for _, g in groups]
    _, p = stats.kruskal(*values) if len(values) > 1 else (np.nan, 1.0)
    means, sizes = groups.mean(), groups.size()
    eta2 = (sizes * (means - df[target].mean()) ** 2).sum() / ((df[target] - df[target].mean()) ** 2).sum()
    mde = mde_two_groups(df[target].std(), sizes.min(), sizes.max()) / df[target].mean() * 100
    return {"tipo": "categórico", "teste": "Kruskal-Wallis", "grupos": len(sizes), "variância explicada (%)": eta2 * 100,
            "efeito de negócio (%)": (means.max() / means.min() - 1) * 100,
            "leitura do efeito": f"melhor {means.idxmax()} vs. pior {means.idxmin()}", "MDE (%)": mde, "p_value": p}


def _numeric(df: pd.DataFrame, col: str, target: str) -> dict:
    x = df[col].astype(float)
    rho, p = stats.spearmanr(x, df[target])
    bins = pd.qcut(x.rank(method="first"), QUINTILES, labels=False)
    q_means = df.groupby(bins)[target].mean()
    return {"tipo": "numérico", "teste": "Spearman", "grupos": np.nan, "variância explicada (%)": rho ** 2 * 100,
            "efeito de negócio (%)": (q_means.iloc[-1] / q_means.iloc[0] - 1) * 100,
            "leitura do efeito": f"ρ = {rho:+.4f} (quintil mais alto vs. mais baixo)",
            "MDE (%)": mde_two_groups(df[target].std(), len(df) // QUINTILES, len(df) // QUINTILES) / df[target].mean() * 100,
            "p_value": p}


def _high_cardinality(df: pd.DataFrame, col: str, target: str) -> dict:
    """One-way ANOVA; effect = η² above what chance alone gives with k groups ((k−1)/(n−1))."""
    groups = [g.values for _, g in df.groupby(col)[target]]
    f, p = stats.f_oneway(*groups)
    k, n = len(groups), len(df)
    eta2 = f * (k - 1) / (f * (k - 1) + (n - k))
    chance = (k - 1) / (n - 1)
    spread = df.groupby(col)[target].mean().quantile([0.1, 0.9])
    return {"tipo": "alta cardinalidade", "teste": "ANOVA (η² − acaso)", "grupos": k,
            "variância explicada (%)": max(eta2 - chance, 0) * 100, "efeito de negócio (%)": (spread.iloc[1] / spread.iloc[0] - 1) * 100,
            "leitura do efeito": f"η² = {eta2:.3f} vs. {chance:.3f} esperado por acaso (p90/p10 das médias por grupo)",
            "MDE (%)": np.nan, "p_value": p}


def _text(df: pd.DataFrame, col: str, target: str) -> dict:
    try:
        model = tfidf_cv_r2(df[col].fillna(""), df[target])
    except ValueError:  # empty vocabulary → nothing to learn from
        model = {"vocabulário": 0, "R² médio": 0.0, "R² desvio": np.inf}
    # CV R² across folds: one-sided t-test of "R² > 0".
    t = model["R² médio"] / (model["R² desvio"] / np.sqrt(5) + 1e-12)
    return {"tipo": "texto", "teste": "TF-IDF + Ridge (R² validação cruzada)", "grupos": model["vocabulário"],
            "variância explicada (%)": max(model["R² médio"], 0) * 100, "efeito de negócio (%)": np.nan,
            "leitura do efeito": f"R² = {model['R² médio']:+.4f} ({model['vocabulário']:,} termos)", "MDE (%)": np.nan,
            "p_value": float(stats.t.sf(t, df=4))}


SCANNERS = [(CATEGORICAL, _categorical), (NUMERIC, _numeric), (HIGH_CARDINALITY, _high_cardinality), (TEXT, _text)]


def scan(df: pd.DataFrame, targets: list[str] = TARGETS) -> pd.DataFrame:
    """Every attribute × every target. Rows where attribute == target are skipped."""
    frame = attribute_frame(df)
    rows = []
    for target in targets:
        for columns, scanner in SCANNERS:
            for col in columns:
                if col == target:
                    continue
                rows.append({"atributo": col, "alvo": target, **scanner(frame, col, target)})
    table = pd.DataFrame(rows)
    table["p_value"] = table["p_value"].fillna(1.0)  # constant attribute → untestable, never "significant"
    table["q_value"] = multipletests(table["p_value"], method="fdr_bh")[1]
    table["significativo"] = table["q_value"] < ALPHA
    return table.sort_values(["alvo", "variância explicada (%)"], ascending=[True, False], ignore_index=True)


def skipped_attributes() -> pd.DataFrame:
    return pd.Series(SKIPPED, name="motivo").rename_axis("atributo").to_frame()


def summary_matrix(table: pd.DataFrame, value: str = "variância explicada (%)") -> pd.DataFrame:
    """Attribute × target matrix of the chosen column (for heatmaps)."""
    return table.pivot(index="atributo", columns="alvo", values=value)


def group_profile(df: pd.DataFrame, col: str, target: str) -> pd.DataFrame:
    """Mean ± 95% CI of the target per group (categorical) or per quintile (numeric)."""
    frame = attribute_frame(df)
    keys = frame[col] if col in CATEGORICAL else pd.qcut(frame[col].rank(method="first"), QUINTILES,
                                                          labels=[f"Q{i}" for i in range(1, QUINTILES + 1)])
    g = frame.groupby(keys, observed=True)[target].agg(["size", "mean", "sem"])
    g["IC95"] = 1.96 * g["sem"]
    return g.drop(columns="sem")
