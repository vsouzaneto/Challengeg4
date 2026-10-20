"""Aggregations behind the Power BI-style dashboard: filter posts, KPI cards, breakdowns, time series, matrix, top posts."""
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

from social_insights.data import DAYPARTS, FOLLOWER_TIERS, LENGTH_BINS

FILTER_FIELDS = ["platform", "content_type", "content_category", "language", "is_sponsored", "follower_tier", "daypart",
                 "weekday", "length_bin", "audience_gender_distribution", "audience_age_distribution", "audience_location"]
DIMENSIONS = FILTER_FIELDS + ["sponsor_category", "n_hashtags", "month_name", "hour"]
METRICS = {"views": "Views", "likes": "Likes", "shares": "Compartilhamentos", "comments_count": "Comentários",
           "eng_rate": "Engajamento (%)", "top5_views": "% no top 5% de views", "top5_likes": "% no top 5% de likes",
           "top5_comments": "% no top 5% de comentários"}
TOP_Q = 0.95
ALPHA = 0.05
TOP_POSTS = 10
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
NATURAL_ORDER = {"month_name": MONTHS, "weekday": WEEKDAYS, "daypart": list(DAYPARTS), "follower_tier": list(FOLLOWER_TIERS),
                 "length_bin": list(LENGTH_BINS)}
NUMERIC_DIMENSIONS = {"hour", "n_hashtags"}


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    """Adds dashboard columns: month, engagement %, top-5% flags (as 0/100 so means read as %)."""
    out = df.copy()
    out["month"] = out["post_date"].dt.to_period("M").astype(str)
    out["month_name"] = out["post_date"].dt.month_name()
    out["eng_rate"] = out["eng_rate_views"] * 100
    for metric, col in [("views", "top5_views"), ("likes", "top5_likes"), ("comments_count", "top5_comments")]:
        out[col] = (out[metric] >= out[metric].quantile(TOP_Q)).astype(float) * 100
    for col in FILTER_FIELDS + ["sponsor_category", "n_hashtags"]:
        out[col] = out[col].astype(str)
    return out


def apply_filters(df: pd.DataFrame, filters: dict[str, list[str]] | None = None, date_from: str | None = None,
                  date_to: str | None = None) -> pd.DataFrame:
    """Keep rows matching every non-empty filter (values within a field are OR-ed) and the month range (YYYY-MM)."""
    mask = pd.Series(True, index=df.index)
    for field, values in (filters or {}).items():
        if values and field in df:
            mask &= df[field].isin([str(v) for v in values])
    if date_from:
        mask &= df["month"] >= date_from
    if date_to:
        mask &= df["month"] <= date_to
    return df[mask]


def kpis(sub: pd.DataFrame, full: pd.DataFrame) -> list[dict]:
    """KPI cards: value in the selection and % difference vs. all posts."""
    cards = [{"id": "posts", "rotulo": "Posts", "valor": len(sub), "total": len(full), "vs_total": len(sub) / len(full) * 100 if len(full) else 0}]
    for metric in ["views", "likes", "comments_count", "eng_rate", "top5_views"]:
        value, total = (sub[metric].mean() if len(sub) else np.nan), full[metric].mean()
        cards.append({"id": metric, "rotulo": METRICS[metric], "valor": value, "total": total,
                      "vs_total": (value / total - 1) * 100 if len(sub) and total else None})
    return cards


def breakdown(sub: pd.DataFrame, dimension: str, metric: str, min_posts: int = 30) -> list[dict]:
    """Mean of `metric` per group with 95% interval and a plain flag: is the group really different from the rest?"""
    rows = []
    for value, g in sub.groupby(dimension, observed=True):
        rest = sub.loc[sub[dimension] != value, metric]
        if len(g) < min_posts:
            continue
        p = stats.ttest_ind(g[metric], rest, equal_var=False).pvalue if len(rest) > 1 else 1.0
        sem = g[metric].std() / np.sqrt(len(g))
        overall = sub[metric].mean()
        rows.append({"grupo": str(value), "posts": len(g), "media": g[metric].mean(), "lo": g[metric].mean() - 1.96 * sem,
                     "hi": g[metric].mean() + 1.96 * sem, "vs_resto": (g[metric].mean() / rest.mean() - 1) * 100 if rest.mean() else 0,
                     "vs_media": (g[metric].mean() / overall - 1) * 100 if overall else 0, "p": 1.0 if np.isnan(p) else p})
    if rows:
        q = multipletests([r["p"] for r in rows], method="fdr_bh")[1]
        for r, qv in zip(rows, q):
            r["diferente"] = bool(qv < ALPHA)
    return sorted(rows, key=lambda r: _group_order(dimension, r))


def _group_order(dimension: str, row: dict):
    """Natural order for ordinal dimensions (months, tiers, hours…); highest mean first otherwise."""
    if dimension in NATURAL_ORDER and row["grupo"] in NATURAL_ORDER[dimension]:
        return NATURAL_ORDER[dimension].index(row["grupo"])
    if dimension in NUMERIC_DIMENSIONS:
        return float(row["grupo"])
    return -row["media"]


PARTIAL_MONTH_SHARE = 0.3  # months with < 30% of the typical monthly volume are partial (dataset edges)


def timeseries(sub: pd.DataFrame, metric: str) -> list[dict]:
    counts = sub["month"].value_counts()
    full = counts[counts >= PARTIAL_MONTH_SHARE * counts.median()].index
    g = sub[sub["month"].isin(full)].groupby("month")[metric].agg(["mean", "std", "size"])
    g["sem"] = g["std"] / np.sqrt(g["size"])
    return [{"mes": m, "media": r["mean"], "lo": r["mean"] - 1.96 * r["sem"], "hi": r["mean"] + 1.96 * r["sem"], "posts": int(r["size"])}
            for m, r in g.iterrows()]


def matrix(sub: pd.DataFrame, row: str, col: str, metric: str) -> dict:
    """Row × column mean, as an index (100 = average of the selection), plus post counts."""
    means = sub.pivot_table(metric, row, col, aggfunc="mean", observed=True)
    counts = sub.pivot_table(metric, row, col, aggfunc="size", observed=True)
    base = sub[metric].mean() or 1
    return {"linhas": [str(i) for i in means.index], "colunas": [str(c) for c in means.columns],
            "indice": (means / base * 100).round(2).where(means.notna(), None).values.tolist(),
            "posts": counts.fillna(0).astype(int).values.tolist()}


RANKING_METRIC = {"top5_views": "views", "top5_likes": "likes", "top5_comments": "comments_count"}


def top_posts(sub: pd.DataFrame, metric: str, n: int = TOP_POSTS) -> list[dict]:
    """Best posts of the selection, ranked by the metric itself (or by the raw metric behind a top-5% flag)."""
    rank_by = RANKING_METRIC.get(metric, metric)
    cols = ["post_date", "platform", "content_type", "content_category", "language", "is_sponsored", "follower_count", rank_by]
    top = sub.nlargest(n, rank_by)[cols].copy()
    top["post_date"] = top["post_date"].dt.strftime("%Y-%m-%d")
    return top.to_dict(orient="records")


DEFAULT_CHARTS = ["platform", "content_type", "content_category", "follower_tier", "language"]


def _without(filters: dict | None, field: str) -> dict:
    return {k: v for k, v in (filters or {}).items() if k != field}


def explore(df: pd.DataFrame, filters: dict | None = None, dimension: str = "platform", metric: str = "views",
            row: str = "platform", col: str = "content_type", date_from: str | None = None, date_to: str | None = None,
            charts: list[str] | None = None) -> dict:
    """Everything the dashboard draws for one state of the slicers.

    Each chart in `charts` is computed with every filter except its own dimension (Power BI-style cross-filtering):
    the chart keeps showing all its options, with the selected ones highlighted by the page.
    """
    charts = charts or DEFAULT_CHARTS
    if any(d not in DIMENSIONS for d in [dimension, row, col, *charts]) or metric not in METRICS:
        raise ValueError("dimensão ou métrica desconhecida")
    sub = apply_filters(df, filters, date_from, date_to)
    if sub.empty:
        return {"posts": 0, "kpis": kpis(sub, df), "breakdown": [], "graficos": {d: [] for d in charts}, "serie": [], "matriz": None, "top": []}
    graficos = {d: breakdown(apply_filters(df, _without(filters, d), date_from, date_to), d, metric) for d in charts}
    return {"posts": len(sub), "kpis": kpis(sub, df), "breakdown": breakdown(sub, dimension, metric), "graficos": graficos,
            "serie": timeseries(sub, metric), "matriz": matrix(sub, row, col, metric), "top": top_posts(sub, metric),
            "media_geral": float(sub[metric].mean()), "resumo": headline(graficos, metric)}


def headline(graficos: dict[str, list[dict]], metric: str) -> dict:
    """The strongest real difference in the current selection (or none), for the page's one-line summary."""
    real = [(d, r) for d, rows in graficos.items() for r in rows if r.get("diferente")]
    if not real:
        return {"tipo": "nenhum", "metrica": metric}
    d, r = max(real, key=lambda x: abs(x[1]["vs_media"]))
    return {"tipo": "destaque", "metrica": metric, "dimensao": d, "grupo": r["grupo"], "vs_media": r["vs_media"], "outros": len(real) - 1}


def options(df: pd.DataFrame) -> dict:
    """Slicer values and selectable dimensions/metrics."""
    return {"filtros": {f: sorted(df[f].unique().tolist(), key=_sort_key) for f in FILTER_FIELDS},
            "dimensoes": DIMENSIONS, "metricas": METRICS, "meses": sorted(df["month"].unique().tolist())}


def _sort_key(value: str):
    return (0, int(value)) if value.isdigit() else (1, value)
