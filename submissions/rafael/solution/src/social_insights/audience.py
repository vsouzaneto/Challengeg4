"""Audience profile per content attribute: who watches each kind of post, and who engages most."""
import numpy as np
import pandas as pd
from scipy import stats

RESIDUAL_THRESHOLD = 3.0  # |adjusted residual| > 3 ≈ p < 0.003 per cell


def audience_mix(df: pd.DataFrame, by: str, audience_col: str) -> pd.DataFrame:
    """Row-normalized share of each audience segment within each value of `by`."""
    return pd.crosstab(df[by], df[audience_col], normalize="index")


def adjusted_residuals(df: pd.DataFrame, by: str, audience_col: str) -> tuple[pd.DataFrame, float, float]:
    """Haberman adjusted residuals (cell over/under-representation), Cramér's V and chi² p-value."""
    table = pd.crosstab(df[by], df[audience_col])
    chi2, p, _, expected = stats.chi2_contingency(table, correction=False)
    n = table.values.sum()
    row = table.sum(axis=1).values[:, None] / n
    col = table.sum(axis=0).values[None, :] / n
    residuals = (table - expected) / np.sqrt(expected * (1 - row) * (1 - col))
    cramers_v = np.sqrt(chi2 / (n * (min(table.shape) - 1)))
    return residuals, float(cramers_v), float(p)


def association_summary(df: pd.DataFrame, by_cols: list[str], audience_cols: list[str]) -> pd.DataFrame:
    """Cramér's V and p-value for each (content attribute × audience attribute) pair."""
    rows = []
    for by in by_cols:
        for aud in audience_cols:
            _, v, p = adjusted_residuals(df, by, aud)
            rows.append({"content": by, "audience": aud, "cramers_v": v, "p_value": p})
    return pd.DataFrame(rows).sort_values("cramers_v", ascending=False, ignore_index=True)


def strongest_cells(df: pd.DataFrame, by: str, audience_col: str, threshold: float = RESIDUAL_THRESHOLD) -> pd.DataFrame:
    """Cells whose adjusted residual exceeds the threshold (real over/under-representation)."""
    residuals, _, _ = adjusted_residuals(df, by, audience_col)
    long = residuals.stack().rename("residual").reset_index()
    return long[long["residual"].abs() > threshold].sort_values("residual", ascending=False)


def engagement_by_segment(df: pd.DataFrame, by: str, audience_col: str, metric: str) -> pd.DataFrame:
    """Mean metric per (content value × audience segment), indexed to the content value's mean (100 = average)."""
    means = df.pivot_table(metric, by, audience_col, observed=True)
    return (means.div(df.groupby(by, observed=True)[metric].mean(), axis=0) * 100).round(2)


def interaction_pvalues(df: pd.DataFrame, by: str, audience_col: str, metric: str) -> pd.Series:
    """Within each content value, does the audience segment change the metric? (Kruskal-Wallis p)."""
    return df.groupby(by, observed=True).apply(
        lambda g: stats.kruskal(*[x[metric].values for _, x in g.groupby(audience_col)]).pvalue
    ).rename("p_value")
