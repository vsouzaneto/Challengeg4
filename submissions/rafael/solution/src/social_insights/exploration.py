"""Bivariate exploration: correlations, group medians with effect sizes, binned (non-linear) comparisons."""
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

ALPHA = 0.05


def correlations(df: pd.DataFrame, features: list[str], targets: list[str]) -> pd.DataFrame:
    """Pearson and Spearman (coefficient + p-value) of each feature against each target."""
    rows = []
    for t in targets:
        for f in features:
            if f == t:
                continue
            pr, pp = stats.pearsonr(df[f], df[t])
            sr, sp = stats.spearmanr(df[f], df[t])
            rows.append({"alvo": t, "variável": f, "pearson": pr, "p_pearson": pp, "spearman": sr, "p_spearman": sp})
    table = pd.DataFrame(rows)
    table["q_spearman"] = multipletests(table["p_spearman"], method="fdr_bh")[1]
    return table


def group_stats(df: pd.DataFrame, by: str, target: str) -> pd.DataFrame:
    """Median, IQR and mean per group, with median indexed to the overall median (100 = typical post)."""
    g = df.groupby(by, observed=True)[target]
    table = pd.DataFrame({"n": g.size(), "mediana": g.median(), "p25": g.quantile(0.25), "p75": g.quantile(0.75), "média": g.mean()})
    table["índice mediana"] = table["mediana"] / df[target].median() * 100
    return table


def kruskal_effect(df: pd.DataFrame, by: str, target: str) -> dict:
    """Kruskal-Wallis p-value and epsilon² effect size (0 = none, 0.01 small, 0.08 medium, 0.26 large)."""
    groups = [x.values for _, x in df.groupby(by, observed=True)[target]]
    h, p = stats.kruskal(*groups)
    return {"variável": by, "alvo": target, "H": h, "p_value": p, "epsilon²": h / (len(df) - 1)}


def categorical_tests(df: pd.DataFrame, features: list[str], targets: list[str]) -> pd.DataFrame:
    table = pd.DataFrame([kruskal_effect(df, f, t) for t in targets for f in features])
    table["q_value"] = multipletests(table["p_value"], method="fdr_bh")[1]
    table["significativo"] = table["q_value"] < ALPHA
    return table.sort_values("epsilon²", ascending=False, ignore_index=True)


def bin_series(values: pd.Series, n_bins: int = 6) -> pd.Series:
    """Quantile bins with readable labels; falls back to the raw value for low-cardinality columns."""
    if values.nunique() <= n_bins + 2:
        return values.astype(str)
    binned = pd.qcut(values, n_bins, duplicates="drop")
    return binned.map(lambda iv: f"{max(iv.left, values.min()):,.0f}–{iv.right:,.0f}").astype(str).where(binned.notna())


def compare_numeric(df: pd.DataFrame, top: pd.Series, columns: list[str]) -> pd.DataFrame:
    """Top vs. rest on numeric columns: medians, Mann-Whitney p and rank-biserial effect size (−1..1)."""
    rows = []
    for c in columns:
        a, b = df.loc[top, c], df.loc[~top, c]
        u, p = stats.mannwhitneyu(a, b)
        rows.append({"variável": c, "mediana top": a.median(), "mediana demais": b.median(),
                     "p_value": p, "efeito (rank-biserial)": 2 * u / (len(a) * len(b)) - 1})
    table = pd.DataFrame(rows)
    table["q_value"] = multipletests(table["p_value"], method="fdr_bh")[1]
    return table


def spurious_ratio_demo(df: pd.DataFrame, rng_seed: int = 0) -> pd.DataFrame:
    """Show that X/followers correlates with followers even when X is random (shared-denominator artifact)."""
    rng = np.random.default_rng(rng_seed)
    random_metric = rng.permutation(df["likes"].values)
    return pd.DataFrame({
        "likes/seguidor × seguidores": [stats.spearmanr(df["likes"] / df["follower_count"], df["follower_count"])[0]],
        "likes EMBARALHADOS/seguidor × seguidores": [stats.spearmanr(random_metric / df["follower_count"], df["follower_count"])[0]],
        "likes × seguidores": [stats.spearmanr(df["likes"], df["follower_count"])[0]],
    }, index=["Spearman ρ"]).T


def engagement_rate_by_tier(df: pd.DataFrame) -> pd.DataFrame:
    """Median interactions per follower vs. per view, and median views, per creator tier.

    Per follower, small creators look far better only because views are flat across tiers (shared-denominator artifact)."""
    rates = df.assign(per_follower=df["interactions"] / df["follower_count"], per_view=df["interactions"] / df["views"])
    return (rates.groupby("follower_tier", observed=True)
            .agg(posts=("views", "size"), per_follower=("per_follower", "median"), per_view=("per_view", "median"),
                 views=("views", "median"))
            .rename(columns={"per_follower": "interações por seguidor (mediana)", "per_view": "interações por view (mediana)",
                             "views": "views (mediana)"}))


def engagement_by_quarter(df: pd.DataFrame, target: str = "eng_rate_views") -> tuple[pd.DataFrame, dict]:
    """Mean engagement per calendar quarter, plus a Kruskal-Wallis test across quarters (seasonality check)."""
    quarters = df.assign(trimestre=df["post_date"].dt.to_period("Q").astype(str))
    table = quarters.groupby("trimestre")[target].agg(posts="size", engajamento="mean")
    return table, kruskal_effect(quarters, "trimestre", target)
