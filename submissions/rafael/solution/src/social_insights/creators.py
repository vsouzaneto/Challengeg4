"""Creator × results: does who posts matter? Variance share (ICC), spread vs. pure chance, persistence and an honest ranking."""
import numpy as np
import pandas as pd
from scipy import stats

SEED = 42
KEY = "creator_id"
METRICS = ["views", "likes", "comments_count"]
NULL_DRAWS = 200
TOP_SHARE = 0.10


def identity_check(df: pd.DataFrame) -> pd.DataFrame:
    """Which column identifies a creator? Posts per value and how often a name is shared by different ids."""
    rows = []
    for col in ["creator_id", "creator_name"]:
        counts = df[col].value_counts()
        rows.append({"coluna": col, "valores únicos": df[col].nunique(), "posts por valor (mediana)": counts.median(),
                     "valores com 2+ posts": int((counts >= 2).sum())})
    table = pd.DataFrame(rows).set_index("coluna")
    names = df.groupby("creator_name")[KEY].nunique()
    table.loc["creator_name", "ids diferentes por nome (máx.)"] = names.max()
    table.loc["creator_id", "nomes diferentes por id (mediana)"] = df.groupby(KEY)["creator_name"].nunique().median()
    return table


def variance_share(df: pd.DataFrame, metrics: list[str] = METRICS) -> pd.DataFrame:
    """One-way ANOVA per metric and ICC(1): share of the variation that belongs to the creator (0 = none)."""
    rows = []
    for m in metrics:
        groups = [g.values for _, g in df.groupby(KEY)[m]]
        f, p = stats.f_oneway(*groups)
        n, k = len(df), len(groups)
        n0 = (n - sum(len(g) ** 2 for g in groups) / n) / (k - 1)
        rows.append({"métrica": m, "creators": k, "F": f, "p_value": p, "ICC (% da variação ligada ao creator)": max((f - 1) / (f + n0 - 1), 0) * 100})
    return pd.DataFrame(rows).set_index("métrica")


def spread_vs_chance(df: pd.DataFrame, metric: str = "views", draws: int = NULL_DRAWS, seed: int = SEED) -> dict:
    """Observed spread of creator averages vs. the spread obtained by randomly reassigning posts to creators."""
    rng = np.random.default_rng(seed)
    observed = df.groupby(KEY)[metric].mean()
    values, keys = df[metric].values, df[KEY].values
    null_sd = np.array([pd.Series(rng.permutation(values)).groupby(keys).mean().std() for _ in range(draws)])
    return {"desvio observado": observed.std(), "desvio esperado por acaso": null_sd.mean(),
            "p_value": (np.sum(null_sd >= observed.std()) + 1) / (draws + 1), "medias": observed.values,
            "medias_acaso": pd.Series(rng.permutation(values)).groupby(keys).mean().values}


def persistence(df: pd.DataFrame, metric: str = "views", top_share: float = TOP_SHARE) -> dict:
    """Do the best creators of the first half of the period stay on top in the second half?"""
    data = df.sort_values("post_date")
    first = data["post_date"] < data["post_date"].median()
    halves = pd.concat([data[first].groupby(KEY)[metric].mean(), data[~first].groupby(KEY)[metric].mean()], axis=1, keys=["1º ano", "2º ano"]).dropna()
    top1 = halves["1º ano"] >= halves["1º ano"].quantile(1 - top_share)
    top2 = halves["2º ano"] >= halves["2º ano"].quantile(1 - top_share)
    rho, p = stats.spearmanr(halves["1º ano"], halves["2º ano"])
    stay = (top1 & top2).sum()
    return {"creators": len(halves), "top no 1º ano": int(top1.sum()), "continuaram no top": int(stay),
            "% que continuou": stay / top1.sum() * 100, "% esperado por acaso": top_share * 100,
            "p (continuou acima do acaso)": stats.binomtest(int(stay), int(top1.sum()), top_share, alternative="greater").pvalue,
            "ρ 1º × 2º ano": rho, "p_value ρ": p, "tabela": halves}


def leaderboard(df: pd.DataFrame, metric: str = "views", n: int = 10) -> pd.DataFrame:
    """Top creators by raw average vs. an honest average shrunk toward the overall mean (empirical Bayes)."""
    g = df.groupby(KEY)[metric].agg(["mean", "size", "var"])
    overall, within = df[metric].mean(), g["var"].mean()
    between = max(g["mean"].var() - (within / g["size"]).mean(), 0)  # true creator-to-creator variance (≈ 0 if none)
    weight = between / (between + within / g["size"]) if between > 0 else pd.Series(0.0, index=g.index)
    g["média ajustada"] = overall + weight * (g["mean"] - overall)
    g["peso do histórico (%)"] = weight * 100
    top = g.sort_values("mean", ascending=False).head(n)
    return top.rename(columns={"mean": "média bruta", "size": "posts"})[["posts", "média bruta", "média ajustada", "peso do histórico (%)"]]
