"""Defines "top posts" per metric and measures which attributes are over-represented among them (lift)."""
from itertools import combinations

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

TOP_QUANTILE = 0.90
ALPHA = 0.05


def flag_top(df: pd.DataFrame, metric: str, by: str | None = None, quantile: float = TOP_QUANTILE) -> pd.Series:
    """True for posts at or above the metric's quantile (within each `by` group, if given)."""
    values = df[metric]
    threshold = values.groupby(df[by]).transform("quantile", quantile) if by else values.quantile(quantile)
    return values >= threshold


def top_overlap(df: pd.DataFrame, metrics: list[str], by: str | None = None) -> pd.DataFrame:
    """Jaccard overlap between the top sets of each pair of metrics."""
    flags = {m: flag_top(df, m, by) for m in metrics}
    return pd.DataFrame([[(flags[a] & flags[b]).sum() / (flags[a] | flags[b]).sum() for b in metrics] for a in metrics],
                        index=metrics, columns=metrics)


def _lift_rows(df: pd.DataFrame, top: pd.Series, keys: pd.Series, label: str, min_count: int) -> list[dict]:
    rows, base_rate = [], top.mean()
    for value, members in keys.groupby(keys, observed=True).groups.items():
        n = len(members)
        if n < min_count:
            continue
        hits = int(top.loc[members].sum())
        table = [[hits, n - hits], [int(top.sum()) - hits, len(top) - n - (int(top.sum()) - hits)]]
        rows.append({"feature": label, "value": str(value), "n": n, "top_rate": hits / n,
                     "lift": (hits / n) / base_rate, "p_value": stats.chi2_contingency(table)[1]})
    return rows


def _with_fdr(rows: list[dict]) -> pd.DataFrame:
    table = pd.DataFrame(rows)
    if table.empty:
        return table
    table["q_value"] = multipletests(table["p_value"], method="fdr_bh")[1]
    table["significant"] = table["q_value"] < ALPHA
    return table.sort_values("lift", ascending=False, ignore_index=True)


def lift_table(df: pd.DataFrame, top: pd.Series, features: list[str], min_count: int = 100) -> pd.DataFrame:
    """Lift of each single attribute value among top posts, with Benjamini-Hochberg q-values."""
    rows = [row for f in features for row in _lift_rows(df, top, df[f].astype(str), f, min_count)]
    return _with_fdr(rows)


def pair_lift_table(df: pd.DataFrame, top: pd.Series, features: list[str], min_count: int = 200) -> pd.DataFrame:
    """Association rules of size 2: (attribute A = a, attribute B = b) → top post."""
    rows = []
    for a, b in combinations(features, 2):
        keys = df[a].astype(str) + " & " + df[b].astype(str)
        rows += _lift_rows(df, top, keys, f"{a} & {b}", min_count)
    return _with_fdr(rows)


def summarize_significant(table: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Top-n rows that survive FDR correction (empty frame means: no real driver)."""
    if table.empty:
        return table
    return table[table["significant"]].head(n)


def expected_false_positives(table: pd.DataFrame, alpha: float = ALPHA) -> float:
    """How many raw p < alpha we would expect from pure chance — the "insights" an uncorrected analysis would report."""
    return float(np.round(len(table) * alpha, 1))
