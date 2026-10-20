"""Exploratory insight discovery: "pockets" with unusual hit rates, ranked by evidence, and top-1% similarity.

Every pocket (attribute value, numeric window or pair of values known before posting) gets its top-5% hit rate.
Evidence tiers: robust (FDR on full data) > replicated (found in the first half of the period, same direction and
one-sided p < 0.05 in the second half; ~5% of null pockets replicate by chance) > exploratory (p < 0.05 on full data).
Replicated and exploratory pockets are prioritized hypotheses for A/B tests, not proven effects.
"""
from itertools import combinations

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

from .questions import ALPHA

TOP_Q = 0.95
TOP1_Q = 0.99
MIN_N = 200
NULL_DRAWS = 300
SEED = 42
CATEGORICAL = ["platform", "content_type", "content_category", "language", "is_sponsored", "sponsor_category",
               "disclosure_type", "disclosure_location", "audience_gender_distribution", "audience_age_distribution",
               "audience_location", "weekday", "daypart", "follower_tier", "length_bin", "n_hashtags", "month"]
NUMERIC = ["content_length", "follower_count", "hour", "caption_words"]
PAIR_FEATURES = ["platform", "content_type", "content_category", "language", "is_sponsored", "follower_tier",
                 "length_bin", "daypart", "weekday", "audience_gender_distribution", "audience_age_distribution", "audience_location"]
MAX_WINDOW_DECILES = 3


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["month"] = out["post_date"].dt.month_name()
    for col in CATEGORICAL:
        out[col] = out[col].astype(str)
    return out


def pocket_masks(df: pd.DataFrame, min_n: int = MIN_N, exclude: tuple[str, ...] = ()) -> dict[tuple[str, str], np.ndarray]:
    """(dimension, value) → boolean mask, for single values, numeric decile windows and value pairs."""
    pockets = {}
    for col in [c for c in CATEGORICAL if c not in exclude]:
        for value, idx in df.groupby(col).indices.items():
            pockets[(col, value)] = idx
    for col in NUMERIC:
        edges = np.unique(df[col].quantile(np.linspace(0, 1, 11)).values)
        for width in range(1, MAX_WINDOW_DECILES + 1):
            for start in range(len(edges) - width):
                lo, hi = edges[start], edges[start + width]
                inside = (df[col] >= lo) & ((df[col] < hi) if start + width < len(edges) - 1 else (df[col] <= hi))
                pockets[(f"{col} (janela)", f"{lo:,.0f}–{hi:,.0f}")] = np.flatnonzero(inside.values)
    for a, b in combinations([c for c in PAIR_FEATURES if c not in exclude], 2):
        for (va, vb), idx in df.groupby([a, b]).indices.items():
            pockets[(f"{a} × {b}", f"{va} · {vb}")] = idx
    masks = {}
    for key, idx in pockets.items():
        if min_n <= len(idx) <= len(df) - min_n:  # needs a "rest" group to compare against
            mask = np.zeros(len(df), dtype=bool)
            mask[idx] = True
            masks[key] = mask
    return masks


def _rate_test(hit: np.ndarray, mask: np.ndarray) -> tuple[float, float, float]:
    """Pocket hit rate, lift vs. the rest and two-sided z-test p-value (pocket vs. rest)."""
    n1, n2 = mask.sum(), (~mask).sum()
    p1, p2 = hit[mask].mean(), hit[~mask].mean()
    pooled = hit.mean()
    se = np.sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2))
    z = (p1 - p2) / se if se > 0 else 0.0
    return p1, p1 / p2 if p2 > 0 else np.nan, 2 * stats.norm.sf(abs(z))


def scan_pockets(df: pd.DataFrame, target: str, top_q: float = TOP_Q, min_n: int = MIN_N, exclude: tuple[str, ...] = ()) -> pd.DataFrame:
    """All pockets for one metric, with full-data stats and the split-half replication check."""
    data = prepare(df).reset_index(drop=True)
    threshold = data[target].quantile(top_q)
    hit = (data[target] >= threshold).values
    first_half = (data["post_date"] < data["post_date"].median()).values
    masks = pocket_masks(data, min_n, exclude)
    rows = []
    for (dimension, value), mask in masks.items():
        rate, lift, p = _rate_test(hit, mask)
        stats_a = _rate_test(hit[first_half], mask[first_half]) if mask[first_half].sum() >= min_n // 2 else (np.nan,) * 3
        stats_b = _rate_test(hit[~first_half], mask[~first_half]) if mask[~first_half].sum() >= min_n // 2 else (np.nan,) * 3
        rows.append({"alvo": target, "dimensão": dimension, "bolsão": value, "posts": int(mask.sum()),
                     "taxa top 5% (%)": rate * 100, "lift": lift, "views/métrica média vs. resto (%)":
                     (data.loc[mask, target].mean() / data.loc[~mask, target].mean() - 1) * 100,
                     "p_value": p, "lift 1ª metade": stats_a[1], "p 1ª metade": stats_a[2],
                     "lift 2ª metade": stats_b[1], "p 2ª metade": stats_b[2]})
    table = pd.DataFrame(rows)
    table["p_value"] = table["p_value"].fillna(1.0)
    table["q_value"] = multipletests(table["p_value"], method="fdr_bh")[1]
    found_a = table["p 1ª metade"] < ALPHA
    same_direction = np.sign(table["lift 1ª metade"] - 1) == np.sign(table["lift 2ª metade"] - 1)
    table["replicou"] = found_a & same_direction & (table["p 2ª metade"] / 2 < ALPHA)  # one-sided in the 2nd half
    table["evidência"] = np.select(
        [table["q_value"] < ALPHA, table["replicou"], table["p_value"] < ALPHA],
        ["robusta (FDR)", "replicada (2 metades)", "exploratória"], default="—")
    return table.sort_values(["evidência", "p_value"], ascending=[False, True], ignore_index=True)


def replication_summary(table: pd.DataFrame) -> dict:
    """How many first-half discoveries replicate vs. chance (5%: one-sided α in the discovered direction), with a binomial p."""
    found = int((table["p 1ª metade"] < ALPHA).sum())
    replicated = int(table["replicou"].sum())
    return {"bolsões testados": len(table), "p<0,05 nos dados completos": int((table["p_value"] < ALPHA).sum()),
            "esperado por acaso": round(len(table) * ALPHA), "descobertos na 1ª metade": found, "replicaram na 2ª metade": replicated,
            "taxa de replicação (%)": replicated / max(found, 1) * 100, "replicação esperada por acaso (%)": ALPHA * 100,
            "p (replicação acima do acaso)": stats.binomtest(replicated, max(found, 1), ALPHA, alternative="greater").pvalue,
            "robustos (FDR)": int((table["q_value"] < ALPHA).sum())}


def insight_cards(table: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Plain-language sentences for the strongest pockets (replicated first, then exploratory)."""
    metric_names = {"views": "views", "likes": "likes", "comments_count": "comentários", "shares": "shares"}
    picked = table[table["evidência"] != "—"].head(n)
    rows = []
    for _, r in picked.iterrows():
        direction = "mais" if r["lift"] > 1 else "menos"
        rows.append({"evidência": r["evidência"], "insight": (
            f"{r['dimensão']} = {r['bolsão']}: {r['taxa top 5% (%)']:.1f}% dos {r['posts']:,} posts chegam ao top 5% de "
            f"{metric_names.get(r['alvo'], r['alvo'])} ({r['lift']:.2f}x, {direction} que o resto). "
            f"1ª metade {r['lift 1ª metade']:.2f}x · 2ª metade {r['lift 2ª metade']:.2f}x · q = {r['q_value']:.2f}"),
            "como validar": "teste A/B ou acompanhamento nos próximos posts"})
    return pd.DataFrame(rows)


# ---------- top 1% ----------

def top_mask(df: pd.DataFrame, target: str, q: float = TOP1_Q) -> pd.Series:
    return df[target] >= df[target].quantile(q)


def top_profile(df: pd.DataFrame, target: str, q: float = TOP1_Q) -> pd.DataFrame:
    """Share of each pre-publication value among top posts vs. all posts (lift) with Fisher p-values and BH."""
    data = prepare(df)
    top = top_mask(data, target, q)
    rows = []
    for col in CATEGORICAL:
        share_top = data.loc[top, col].value_counts(normalize=True)
        share_all = data[col].value_counts(normalize=True)
        counts_top = data.loc[top, col].value_counts()
        for value in share_all.index:
            k = int(counts_top.get(value, 0))
            n_val = int((data[col] == value).sum())
            table = [[k, int(top.sum()) - k], [n_val - k, len(data) - n_val - (int(top.sum()) - k)]]
            rows.append({"atributo": col, "valor": value, "% no top": share_top.get(value, 0) * 100, "% na base": share_all[value] * 100,
                         "lift": share_top.get(value, 0) / share_all[value], "posts no top": k, "p_value": stats.fisher_exact(table)[1]})
    table = pd.DataFrame(rows)
    table["q_value"] = multipletests(table["p_value"], method="fdr_bh")[1]
    return table.sort_values("p_value", ignore_index=True)


def top_numeric_profile(df: pd.DataFrame, target: str, q: float = TOP1_Q) -> pd.DataFrame:
    """Top vs. rest on numeric pre-publication variables, with BH q-values and the same test in each half of the period."""
    top = top_mask(df, target, q)
    first_half = df["post_date"] < df["post_date"].median()
    rows = []
    for col in NUMERIC:
        u, p = stats.mannwhitneyu(df.loc[top, col], df.loc[~top, col])
        halves = [stats.mannwhitneyu(df.loc[top & h, col], df.loc[~top & h, col]).pvalue for h in (first_half, ~first_half)]
        rows.append({"variável": col, "mediana top 1%": df.loc[top, col].median(), "mediana demais": df.loc[~top, col].median(),
                     "efeito (rank-biserial)": 2 * u / (top.sum() * (~top).sum()) - 1, "p_value": p,
                     "p 1ª metade": halves[0], "p 2ª metade": halves[1]})
    table = pd.DataFrame(rows).set_index("variável")
    table["q_value"] = multipletests(table["p_value"], method="fdr_bh")[1]
    return table


def _onehot(df: pd.DataFrame) -> np.ndarray:
    return pd.get_dummies(prepare(df)[CATEGORICAL]).values.astype(np.int32)


def mean_similarity(X: np.ndarray) -> float:
    """Mean share of matching attributes between all pairs of rows (simple matching), in O(n·d)."""
    n, features = len(X), len(CATEGORICAL)
    col_sums = X.sum(axis=0).astype(float)
    return float((col_sums @ col_sums - n * features) / (n * (n - 1) * features))


def similarity_test(df: pd.DataFrame, top: pd.Series, draws: int = NULL_DRAWS, seed: int = SEED) -> dict:
    """Are top posts more alike than random sets of the same size? (permutation p-value)."""
    X = _onehot(df)
    mask = top.values
    observed = mean_similarity(X[mask])
    rng = np.random.default_rng(seed)
    null = np.array([mean_similarity(X[rng.choice(len(X), mask.sum(), replace=False)]) for _ in range(draws)])
    return {"similaridade média no top (%)": observed * 100, "similaridade em sorteios (%)": null.mean() * 100,
            "p_value": (np.sum(null >= observed) + 1) / (draws + 1), "null": null * 100}


def creator_concentration(df: pd.DataFrame, top: pd.Series, draws: int = NULL_DRAWS, seed: int = SEED) -> dict:
    """Do top posts concentrate in a few creators? Creators with ≥ 2 top posts vs. random sets of the same size."""
    creators = df["creator_id"].values
    observed = int((pd.Series(creators[top.values]).value_counts() >= 2).sum())
    rng = np.random.default_rng(seed)
    null = np.array([(pd.Series(creators[rng.choice(len(df), top.sum(), replace=False)]).value_counts() >= 2).sum() for _ in range(draws)])
    return {"creators com ≥2 posts no top": observed, "esperado por acaso": null.mean(), "p_value": (np.sum(null >= observed) + 1) / (draws + 1)}


def top_overlap(df: pd.DataFrame, metrics: list[str], q: float = TOP1_Q) -> pd.DataFrame:
    """How many posts are top-1% in two metrics at once, vs. the count expected if metrics were independent."""
    tops = {m: top_mask(df, m, q) for m in metrics}
    rows = []
    for a, b in combinations(metrics, 2):
        both = int((tops[a] & tops[b]).sum())
        expected = tops[a].mean() * tops[b].mean() * len(df)
        rows.append({"par": f"{a} & {b}", "posts top nas duas": both, "esperado se independentes": expected,
                     "p_value": stats.binomtest(both, len(df), tops[a].mean() * tops[b].mean()).pvalue})
    return pd.DataFrame(rows).set_index("par")


# ---------- per platform ----------

def scan_by_platform(df: pd.DataFrame, target: str, platforms: list[str] | None = None, **kw) -> pd.DataFrame:
    """scan_pockets inside each platform (top 5% recomputed per platform; platform itself not used as an attribute)."""
    platforms = platforms or sorted(df["platform"].unique())
    tables = [scan_pockets(df[df["platform"] == p], target, exclude=("platform",), **kw).assign(plataforma=p) for p in platforms]
    return pd.concat(tables, ignore_index=True)


def platform_summary(tables: pd.DataFrame) -> pd.DataFrame:
    """Replication summary per (platform, metric)."""
    return pd.DataFrame({key: replication_summary(g) for key, g in tables.groupby(["plataforma", "alvo"])}).T.rename_axis(["plataforma", "alvo"])


def daypart_top_rate(df: pd.DataFrame, target: str, q: float = TOP1_Q, by: str = "platform") -> pd.DataFrame:
    """% of posts reaching the top (computed within each `by` group) per daypart, plus a chi² p-value per group."""
    rows = []
    for key, g in df.groupby(by):
        top = g[target] >= g[target].quantile(q)
        rates = top.groupby(g["daypart"], observed=True).mean() * 100
        p = stats.chi2_contingency(pd.crosstab(g["daypart"], top))[1]
        rows.append({by: key, **rates.to_dict(), "p (qui²)": p,
                     "hora mediana top": g.loc[top, "hour"].median(), "hora mediana demais": g.loc[~top, "hour"].median(),
                     "p (Mann-Whitney hora)": stats.mannwhitneyu(g.loc[top, "hour"], g.loc[~top, "hour"]).pvalue})
    table = pd.DataFrame(rows).set_index(by)
    table["q (hora)"] = multipletests(table["p (Mann-Whitney hora)"], method="fdr_bh")[1]
    return table
