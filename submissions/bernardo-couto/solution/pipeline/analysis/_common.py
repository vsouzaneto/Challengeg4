"""Shared helpers for the analysis scripts (pandas only; independent from the Spark pipeline).

Everything is anchored on SNAPSHOT_DATE or an explicit ``as_of`` cut. No wall clock.
``close_value``/``close_date`` are read ONLY to build outcomes and point-in-time history
(``compute_history(closed, as_of)``); they are never joined onto the scored deals as features.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

SNAPSHOT_DATE = pd.Timestamp("2017-12-31")
BACKTEST_CUTS = (pd.Timestamp("2017-06-30"), pd.Timestamp("2017-09-30"))
ZOMBIE_DAYS = 138  # max observed cycle (Won and Lost)
PRIOR_STRENGTH = 20.0  # Bayesian smoothing "a"

HERE = Path(__file__).resolve().parent
SOLUTION_DIR = HERE.parents[1]
RAW_DIR = SOLUTION_DIR / "data" / "raw"
DOCS_DIR = SOLUTION_DIR.parent / "docs"
FIG_DIR = DOCS_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

RNG_SEED = 20171231


# --------------------------------------------------------------------------- loading


def load_raw() -> dict[str, pd.DataFrame]:
    pipeline = pd.read_csv(RAW_DIR / "sales_pipeline.csv", parse_dates=["engage_date", "close_date"])
    accounts = pd.read_csv(RAW_DIR / "accounts.csv")
    products = pd.read_csv(RAW_DIR / "products.csv")
    teams = pd.read_csv(RAW_DIR / "sales_teams.csv")
    return {"pipeline": pipeline, "accounts": accounts, "products": products, "teams": teams}


def clean(raw: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Conform names (pipeline 'GTXPro' -> catalogue 'GTX Pro', sector typo), join dimensions."""
    p = raw["pipeline"].copy()
    p["product"] = p["product"].replace({"GTXPro": "GTX Pro"})
    acc = raw["accounts"].copy()
    acc["sector"] = acc["sector"].replace({"technolgy": "technology"})
    df = (
        p.merge(raw["products"], on="product", how="left", validate="m:1")
        .merge(acc, on="account", how="left", validate="m:1")
        .merge(raw["teams"], on="sales_agent", how="left", validate="m:1")
    )
    assert df["sales_price"].notna().all(), "product join lost rows"
    assert df["manager"].notna().all(), "team join lost rows"
    df["account_known"] = df["account"].notna()
    df["is_closed"] = df["deal_stage"].isin(["Won", "Lost"])
    df["won"] = np.where(df["deal_stage"] == "Won", 1.0, np.where(df["deal_stage"] == "Lost", 0.0, np.nan))
    df["cycle_days"] = (df["close_date"] - df["engage_date"]).dt.days
    return df


def load_clean() -> pd.DataFrame:
    return clean(load_raw())


# --------------------------------------------------------------------------- statistics


def wilson(k: float, n: float, z: float = 1.96) -> tuple[float, float, float]:
    """Wilson score interval. Returns (p_hat, lo, hi)."""
    if n <= 0:
        return (np.nan, np.nan, np.nan)
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (p, centre - half, centre + half)


def smooth_rate(k: float, n: float, p0: float, a: float = PRIOR_STRENGTH) -> float:
    """Bayesian shrinkage of a win rate towards prior p0 with pseudo-count a."""
    return (k + a * p0) / (n + a)


def bootstrap_ci(
    values: np.ndarray, stat, n_boot: int = 2000, seed: int = RNG_SEED, **kw
) -> tuple[float, float, float]:
    """Percentile bootstrap of ``stat(sample, **kw)``. Returns (point, lo, hi)."""
    rng = np.random.default_rng(seed)
    values = np.asarray(values)
    n = len(values)
    point = stat(values, **kw)
    boots = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, n, n)
        boots[b] = stat(values[idx], **kw)
    return (point, float(np.nanpercentile(boots, 2.5)), float(np.nanpercentile(boots, 97.5)))


def bootstrap_paired(
    y: np.ndarray, s: np.ndarray, metric, n_boot: int = 2000, seed: int = RNG_SEED, **kw
) -> tuple[float, float, float]:
    """Bootstrap of metric(y, s) resampling rows jointly."""
    rng = np.random.default_rng(seed)
    n = len(y)
    point = metric(y, s, **kw)
    boots = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, n, n)
        boots[b] = metric(y[idx], s[idx], **kw)
    return (point, float(np.nanpercentile(boots, 2.5)), float(np.nanpercentile(boots, 97.5)))


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ra = pd.Series(a).rank().to_numpy()
    rb = pd.Series(b).rank().to_numpy()
    if ra.std() == 0 or rb.std() == 0:
        return np.nan
    return float(np.corrcoef(ra, rb)[0, 1])


def cramers_v(x: pd.Series, y: pd.Series) -> float:
    ct = pd.crosstab(x, y).to_numpy().astype(float)
    n = ct.sum()
    expected = np.outer(ct.sum(1), ct.sum(0)) / n
    chi2 = ((ct - expected) ** 2 / expected).sum()
    k = min(ct.shape) - 1
    return float(np.sqrt(chi2 / (n * k))) if k > 0 else np.nan


# --------------------------------------------------------------------------- ranking metrics


def auc_roc(y: np.ndarray, s: np.ndarray) -> float:
    """Mann-Whitney AUC with tie handling."""
    y = np.asarray(y, dtype=float)
    r = pd.Series(s).rank(method="average").to_numpy()
    n1 = y.sum()
    n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return np.nan
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def auc_pr(y: np.ndarray, s: np.ndarray) -> float:
    """Average precision (area under precision-recall, step interpolation). Ties broken stably."""
    y = np.asarray(y, dtype=float)
    order = np.lexsort((np.arange(len(s)), -np.asarray(s)))
    ys = y[order]
    tp = np.cumsum(ys)
    k = np.arange(1, len(ys) + 1)
    precision = tp / k
    n_pos = ys.sum()
    if n_pos == 0:
        return np.nan
    return float((precision * ys).sum() / n_pos)


def brier(y: np.ndarray, p: np.ndarray) -> float:
    return float(np.mean((np.asarray(p) - np.asarray(y)) ** 2))


def lift_top_decile(y: np.ndarray, s: np.ndarray) -> float:
    y = np.asarray(y, dtype=float)
    n = max(1, int(np.ceil(len(y) * 0.10)))
    order = np.lexsort((np.arange(len(s)), -np.asarray(s)))
    base = y.mean()
    return float(y[order[:n]].mean() / base) if base > 0 else np.nan


def precision_at_k(y: np.ndarray, s: np.ndarray, k: int) -> float:
    y = np.asarray(y, dtype=float)
    order = np.lexsort((np.arange(len(s)), -np.asarray(s)))
    k = min(k, len(y))
    return float(y[order[:k]].mean()) if k > 0 else np.nan


def revenue_captured_top(y_value: np.ndarray, s: np.ndarray, frac: float = 0.20) -> float:
    """Share of realized revenue (sum of close_value of Won) that lands in the top ``frac`` by score."""
    y_value = np.asarray(y_value, dtype=float)
    n = max(1, int(np.ceil(len(y_value) * frac)))
    order = np.lexsort((np.arange(len(s)), -np.asarray(s)))
    total = y_value.sum()
    return float(y_value[order[:n]].sum() / total) if total > 0 else np.nan


def calibration_table(y: np.ndarray, p: np.ndarray, bins: int = 5) -> pd.DataFrame:
    df = pd.DataFrame({"y": y, "p": p})
    df["bin"] = pd.qcut(df["p"].rank(method="first"), bins, labels=False)
    out = df.groupby("bin").agg(n=("y", "size"), p_mean=("p", "mean"), y_rate=("y", "mean"))
    out["gap"] = out["y_rate"] - out["p_mean"]
    return out.reset_index()


# --------------------------------------------------------------------------- point-in-time history


def survival_curve(closed: pd.DataFrame, max_day: int = ZOMBIE_DAYS) -> pd.DataFrame:
    """P(Won | still open after d days) from closed deals only (no censoring needed:
    every closed deal has a cycle). d ranges 0..max_day."""
    cyc = closed["cycle_days"].to_numpy()
    won = closed["won"].to_numpy()
    rows = []
    for d in range(0, max_day + 1):
        alive = cyc > d
        n = alive.sum()
        k = won[alive].sum()
        p, lo, hi = wilson(k, n)
        rows.append({"d": d, "n_alive": int(n), "won_alive": int(k), "p_win_given_alive": p, "lo": lo, "hi": hi})
    return pd.DataFrame(rows)


def compute_history(closed: pd.DataFrame, as_of: pd.Timestamp) -> dict[str, pd.DataFrame | float]:
    """Aggregates from deals with close_date <= as_of only. This is the single leakage gate.

    Returns dict with: p0 (global win rate), by_product, by_agent, by_agent_product, by_sector,
    by_account, value_ratio (median close_value/sales_price of Won per product), survival, won_cycle_quantiles.
    """
    h = closed[(closed["is_closed"]) & (closed["close_date"] <= as_of)].copy()  # leakage-ok: history gate
    p0 = float(h["won"].mean())

    def grp(cols):
        g = h.groupby(cols, dropna=False)["won"].agg(n="size", k="sum").reset_index()
        g["rate_raw"] = g["k"] / g["n"]
        g["rate_smooth"] = smooth_rate(g["k"], g["n"], p0)
        return g

    won = h[h["won"] == 1.0]
    ratio = (won["close_value"] / won["sales_price"]).groupby(won["product"]).median().rename("value_ratio").reset_index()  # leakage-ok: EV multiplier from history only
    q = won["cycle_days"].quantile([0.25, 0.5, 0.75, 0.9]).to_dict()
    return {
        "as_of": as_of,
        "n_closed": len(h),
        "p0": p0,
        "by_product": grp(["product"]),
        "by_agent": grp(["sales_agent"]),
        "by_agent_product": grp(["sales_agent", "product"]),
        "by_sector": grp(["sector"]),
        "by_account": grp(["account"]),
        "value_ratio": ratio,
        "survival": survival_curve(h),
        "won_cycle_quantiles": q,
    }


def open_at(df: pd.DataFrame, as_of: pd.Timestamp) -> pd.DataFrame:
    """Engaging-type deals open at ``as_of``: engage_date <= as_of and (close_date > as_of or null).

    Adds ``days_in_engaging`` (as_of - engage_date), ``label`` (1 Won / 0 Lost / NaN censored),
    ``realized_value`` (close_value if Won after as_of, 0 otherwise; NaN if censored).
    Prospecting deals have no dates and are returned separately by ``prospecting_at``.
    """
    m = (df["engage_date"].notna()) & (df["engage_date"] <= as_of) & (
        df["close_date"].isna() | (df["close_date"] > as_of)  # leakage-ok: defines open set at as_of
    )
    o = df[m].copy()
    o["days_in_engaging"] = (as_of - o["engage_date"]).dt.days
    o["label"] = o["won"]  # NaN when still open at snapshot (censored)
    o["realized_value"] = np.where(o["label"] == 1.0, o["close_value"], 0.0)  # leakage-ok: outcome for evaluation
    o.loc[o["label"].isna(), "realized_value"] = np.nan
    return o


def agent_load_at(df: pd.DataFrame, as_of: pd.Timestamp) -> pd.Series:
    """Open deals per agent at as_of (Engaging-type only; Prospecting has no date)."""
    return open_at(df, as_of).groupby("sales_agent").size().rename("open_load")


# --------------------------------------------------------------------------- numpy logistic regression


def fit_logreg(X: np.ndarray, y: np.ndarray, l2: float = 1.0, iters: int = 500, lr: float = 0.1) -> np.ndarray:
    """L2-regularised logistic regression by gradient descent (no sklearn). Intercept unpenalised.
    X must be standardised; returns weights of shape (p+1,) with intercept first."""
    n, p = X.shape
    Xb = np.hstack([np.ones((n, 1)), X])
    w = np.zeros(p + 1)
    for _ in range(iters):
        z = Xb @ w
        pr = 1 / (1 + np.exp(-z))
        grad = Xb.T @ (pr - y) / n
        grad[1:] += l2 * w[1:] / n
        w -= lr * grad
    return w


def predict_logreg(X: np.ndarray, w: np.ndarray) -> np.ndarray:
    Xb = np.hstack([np.ones((X.shape[0], 1)), X])
    return 1 / (1 + np.exp(-(Xb @ w)))


# --------------------------------------------------------------------------- output


def md_table(df: pd.DataFrame, floatfmt: str = "{:.3f}") -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(str(c) for c in cols) + " |", "|" + "---|" * len(cols)]
    for _, row in df.iterrows():
        cells = []
        for c in cols:
            v = row[c]
            if isinstance(v, float):
                cells.append("" if np.isnan(v) else floatfmt.format(v))
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_md(name: str, sections: list[tuple[str, str]]) -> Path:
    path = FIG_DIR / name
    body = "\n\n".join(f"## {title}\n\n{content}" for title, content in sections)
    path.write_text(body + "\n", encoding="utf-8")
    return path
