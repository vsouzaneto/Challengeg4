"""Temporal backtest metrics (docs/specs/scoring-spec.md sections 7 and 8), pandas on the driver.

Port of ``analysis/_common.py`` / ``analysis/10_backtest.py``. Input: one pandas frame per cut
with the rules output joined to ``gold/labels`` (outcome realised after the cut). Outcome columns
are read here **only** to evaluate; this module never feeds a feature.

Conventions (mirroring the prototype):
- probabilistic metrics (Brier, AUC-PR, AUC-ROC, lift, calibration) use ``p_win``;
- ranking metrics the seller experiences (precision@k per agent, revenue captured in the
  top 20%) use ``priority_score``;
- ``by_signal`` keeps the full row for ``p_win``, ``expected_value`` and ``priority_score``.
- bootstrap: 2000 paired resamples, fixed seed; rows sorted by ``opportunity_id`` first so
  the resampling is reproducible run to run.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

RNG_SEED = 20171231
N_BOOT = 2000
CALIBRATION_BINS = 5
TOP_FRACTION = 0.20

#: Section 7 acceptance thresholds.
ACCEPT_BRIER_MAX = 0.245
ACCEPT_MCE_MAX = 0.06
ACCEPT_REVENUE_VS_RANDOM = 1.5
ACCEPT_SPEARMAN_MAX = 0.9

Metric = Callable[[np.ndarray, np.ndarray], float]


class AcceptanceError(RuntimeError):
    """A section-7 acceptance threshold was not met."""


# --- ranking metrics ------------------------------------------------------------------------------


def _order_desc(s: np.ndarray) -> np.ndarray:
    return np.lexsort((np.arange(len(s)), -np.asarray(s, dtype=float)))


def auc_roc(y: np.ndarray, s: np.ndarray) -> float:
    y = np.asarray(y, dtype=float)
    r = pd.Series(s).rank(method="average").to_numpy()
    n1 = y.sum()
    n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return float("nan")
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def auc_pr(y: np.ndarray, s: np.ndarray) -> float:
    """Average precision with stable tie-breaking (same as the prototype)."""
    y = np.asarray(y, dtype=float)
    ys = y[_order_desc(s)]
    tp = np.cumsum(ys)
    precision = tp / np.arange(1, len(ys) + 1)
    n_pos = ys.sum()
    return float((precision * ys).sum() / n_pos) if n_pos > 0 else float("nan")


def brier(y: np.ndarray, p: np.ndarray) -> float:
    return float(np.mean((np.asarray(p, dtype=float) - np.asarray(y, dtype=float)) ** 2))


def lift_top_decile(y: np.ndarray, s: np.ndarray) -> float:
    y = np.asarray(y, dtype=float)
    n = max(1, int(np.ceil(len(y) * 0.10)))
    base = y.mean()
    return float(y[_order_desc(s)[:n]].mean() / base) if base > 0 else float("nan")


def precision_at_k(y: np.ndarray, s: np.ndarray, k: int) -> float:
    y = np.asarray(y, dtype=float)
    k = min(k, len(y))
    return float(y[_order_desc(s)[:k]].mean()) if k > 0 else float("nan")


def revenue_captured_top(v: np.ndarray, s: np.ndarray, frac: float = TOP_FRACTION) -> float:
    """Share of realised revenue (Won close values) in the top ``frac`` of the ranking."""
    v = np.asarray(v, dtype=float)
    n = max(1, int(np.ceil(len(v) * frac)))
    total = v.sum()
    return float(v[_order_desc(s)[:n]].sum() / total) if total > 0 else float("nan")


def top_k_per_agent_mask(s: np.ndarray, agents: np.ndarray, k: int) -> np.ndarray:
    """Boolean mask of the rows in each agent's top ``k`` by score (all agents)."""
    codes = np.asarray(pd.factorize(agents)[0])
    n = len(codes)
    order = np.lexsort((np.arange(n), -np.asarray(s, dtype=float), codes))
    a_sorted = codes[order]
    starts = np.r_[0, np.flatnonzero(np.diff(a_sorted)) + 1]
    counts = np.diff(np.r_[starts, n])
    pos = np.arange(n) - np.repeat(starts, counts)
    mask = np.zeros(n, dtype=bool)
    mask[order[pos < k]] = True
    return mask


def revenue_within(
    value: np.ndarray, days_to_close: np.ndarray, selected: np.ndarray, horizon: int
) -> tuple[float, float]:
    """(R$ closed within ``horizon`` days in ``selected`` rows, share of all such revenue)."""
    v = np.asarray(value, dtype=float)
    soon = np.nan_to_num(np.asarray(days_to_close, dtype=float), nan=np.inf) <= horizon
    captured = float(v[selected & soon].sum())
    total = float(v[soon].sum())
    return captured, (captured / total if total > 0 else float("nan"))


def per_agent_precision(y: np.ndarray, s: np.ndarray, agents: np.ndarray, k: int) -> float:
    """Mean precision@k over agents with >= ``k`` labelled deals (vectorised for the bootstrap)."""
    y = np.asarray(y, dtype=float)
    codes = (
        agents if np.issubdtype(np.asarray(agents).dtype, np.integer) else pd.factorize(agents)[0]
    )
    codes = np.asarray(codes)
    n = len(y)
    if n == 0:
        return float("nan")
    order = np.lexsort((np.arange(n), -np.asarray(s, dtype=float), codes))
    a_sorted, y_sorted = codes[order], y[order]
    starts = np.r_[0, np.flatnonzero(np.diff(a_sorted)) + 1]
    counts = np.diff(np.r_[starts, n])
    pos = np.arange(n) - np.repeat(starts, counts)
    top = pos < k
    eligible = counts >= k
    if not eligible.any():
        return float("nan")
    hits = np.bincount(a_sorted[top], weights=y_sorted[top], minlength=int(codes.max()) + 1)
    group_ids = a_sorted[starts][eligible]
    return float(np.mean(hits[group_ids] / k))


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ra = pd.Series(a).rank().to_numpy()
    rb = pd.Series(b).rank().to_numpy()
    if ra.std() == 0 or rb.std() == 0:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def calibration_bins(
    y: np.ndarray, p: np.ndarray, bins: int = CALIBRATION_BINS
) -> list[dict[str, Any]]:
    df = pd.DataFrame({"y": np.asarray(y, dtype=float), "p": np.asarray(p, dtype=float)})
    df["bin"] = pd.qcut(df["p"].rank(method="first"), bins, labels=False)
    out: list[dict[str, Any]] = []
    for _, g in df.groupby("bin", sort=True):
        out.append(
            {
                "bin": int(g["bin"].iloc[0]),
                "p_low": round(float(g["p"].min()), 4),
                "p_high": round(float(g["p"].max()), 4),
                "predicted": round(float(g["p"].mean()), 4),
                "actual": round(float(g["y"].mean()), 4),
                "count": int(len(g)),
            }
        )
    return out


def mean_calibration_error(bins: list[dict[str, Any]]) -> float:
    if not bins:
        return float("nan")
    return float(np.mean([abs(b["actual"] - b["predicted"]) for b in bins]))


# --- bootstrap ------------------------------------------------------------------------------------


def _bootstrap_indices(n: int, n_boot: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.integers(0, n, size=(n_boot, n))


def bootstrap_ci(stat: Callable[[np.ndarray], float], idx: np.ndarray) -> tuple[float, float]:
    boots = np.array([stat(row) for row in idx])
    return float(np.nanpercentile(boots, 2.5)), float(np.nanpercentile(boots, 97.5))


# --- one cut --------------------------------------------------------------------------------------

REQUIRED_COLUMNS = (
    "opportunity_id",
    "sales_agent",
    "sales_price",
    "days_in_engaging",
    "product_rate",
    "p_win",
    "expected_value",
    "priority_score",
    "label",
    "realized_value",
)

BASELINES = ("random", "price", "price_alive", "newest", "oldest", "base_rate")
REVENUE_HORIZONS_DAYS = (14, 30)
TOP_PER_AGENT = 10
LATE_WINDOW = (120, 138)  # ages where the hazard peaks; concentration of the top 5 is reported
SIGNALS = ("p_win", "expected_value", "priority_score")


@dataclass
class CutEvaluation:
    cut: str
    backtest: dict[str, Any]
    baselines: dict[str, dict[str, Any]]
    by_signal: dict[str, dict[str, Any]]
    pessimistic: dict[str, dict[str, float]]
    shadow: dict[str, Any] | None = None
    accepted: list[dict[str, Any]] = field(default_factory=list)


def _candidate_row(
    y: np.ndarray,
    v: np.ndarray,
    agents: np.ndarray,
    s: np.ndarray,
    idx: np.ndarray,
    probabilistic: bool,
    days_to_close: np.ndarray | None = None,
) -> dict[str, Any]:
    ap_lo, ap_hi = bootstrap_ci(lambda i: auc_pr(y[i], s[i]), idx)
    rc_lo, rc_hi = bootstrap_ci(lambda i: revenue_captured_top(v[i], s[i]), idx)
    p10_lo, p10_hi = bootstrap_ci(lambda i: per_agent_precision(y[i], s[i], agents[i], 10), idx)
    row: dict[str, Any] = {
        "auc_pr": round(auc_pr(y, s), 4),
        "auc_pr_ci": [round(ap_lo, 4), round(ap_hi, 4)],
        "auc_roc": round(auc_roc(y, s), 4),
        "lift_top_decile": round(lift_top_decile(y, s), 4),
        "precision_at_10": round(per_agent_precision(y, s, agents, 10), 4),
        "precision_at_10_ci": [round(p10_lo, 4), round(p10_hi, 4)],
        "precision_at_25": round(per_agent_precision(y, s, agents, 25), 4),
        "revenue_capture_top20": round(revenue_captured_top(v, s), 4),
        "revenue_capture_top20_ci": [round(rc_lo, 4), round(rc_hi, 4)],
    }
    if probabilistic:
        bins = calibration_bins(y, s)
        row["brier"] = round(brier(y, s), 4)
        row["calibration_bins"] = bins
        row["mean_calibration_error"] = round(mean_calibration_error(bins), 4)
    if days_to_close is not None:
        n_top = max(1, int(np.ceil(len(s) * TOP_FRACTION)))
        top20 = np.zeros(len(s), dtype=bool)
        top20[_order_desc(s)[:n_top]] = True
        top_agent = top_k_per_agent_mask(s, agents, TOP_PER_AGENT)
        for h in REVENUE_HORIZONS_DAYS:
            for label, mask in (("top20", top20), (f"top{TOP_PER_AGENT}_agent", top_agent)):
                captured, share = revenue_within(v, days_to_close, mask, h)
                row[f"revenue_{h}d_{label}"] = round(captured, 2)
                row[f"revenue_{h}d_{label}_share"] = round(share, 4)
    return row


def evaluate_cut(
    frame: pd.DataFrame,
    cut: str,
    *,
    zombie_days: int = 138,
    seed: int = RNG_SEED,
    n_boot: int = N_BOOT,
) -> CutEvaluation:
    """Evaluate one cut. ``frame`` = rules output + labels for every deal open at the cut
    (``label`` NaN when censored). An optional ``p_model`` column adds the shadow-model row."""
    missing = set(REQUIRED_COLUMNS) - set(frame.columns)
    if missing:
        raise KeyError(f"evaluation frame lacks {sorted(missing)}")
    df = frame.sort_values("opportunity_id").reset_index(drop=True)
    labelled = df["label"].notna()
    lab = df[labelled].reset_index(drop=True)
    y = lab["label"].to_numpy(dtype=float)
    v = lab["realized_value"].fillna(0.0).to_numpy(dtype=float)
    agents = pd.factorize(lab["sales_agent"])[0]
    idx = _bootstrap_indices(len(lab), n_boot, seed)
    rng = np.random.default_rng(seed)
    days_lab = lab["days_in_engaging"].to_numpy(dtype=float)
    # "price excluding stalled deals": stalled (> zombie_days) go to the bottom, by price
    price_alive = np.where(
        days_lab > zombie_days,
        -1.0 - 1.0 / (1.0 + lab["sales_price"].to_numpy(dtype=float)),
        lab["sales_price"].to_numpy(dtype=float),
    )
    dtc = lab["days_to_close"].to_numpy(dtype=float) if "days_to_close" in lab.columns else None

    candidates: dict[str, tuple[np.ndarray, bool]] = {
        "random": (rng.random(len(lab)), False),
        "price": (lab["sales_price"].to_numpy(dtype=float), False),
        "price_alive": (price_alive, False),
        "newest": (-lab["days_in_engaging"].to_numpy(dtype=float), False),
        "oldest": (lab["days_in_engaging"].to_numpy(dtype=float), False),
        "base_rate": (lab["product_rate"].to_numpy(dtype=float), True),
        "p_win": (lab["p_win"].to_numpy(dtype=float), True),
        "expected_value": (lab["expected_value"].to_numpy(dtype=float), False),
        "priority_score": (lab["priority_score"].to_numpy(dtype=float), False),
    }
    rows = {
        name: _candidate_row(y, v, agents, s, idx, prob, dtc)
        for name, (s, prob) in candidates.items()
    }

    zombie = df["days_in_engaging"].notna() & (df["days_in_engaging"] > zombie_days)
    zombies_closed = int((zombie & labelled).sum())
    zombies_won = int((zombie & (df["label"] == 1.0)).sum())
    rho = spearman(df["priority_score"].to_numpy(), df["sales_price"].to_numpy())

    p_win_row, score_row = rows["p_win"], rows["priority_score"]
    late = top5_late_share(df, zombie_days)
    backtest: dict[str, Any] = {
        **{k: v_ for k, v_ in score_row.items() if k.startswith("revenue_") and "d_" in k},
        "top5_agent_share_120_138": late,
        "n_open": int(len(df)),
        "n_labeled": int(labelled.sum()),
        "n_censored": int((~labelled).sum()),
        "base_rate": round(float(y.mean()), 4),
        "brier": p_win_row["brier"],
        "auc_pr": p_win_row["auc_pr"],
        "auc_pr_ci": p_win_row["auc_pr_ci"],
        "auc_roc": p_win_row["auc_roc"],
        "lift_top_decile": p_win_row["lift_top_decile"],
        "precision_at_10": score_row["precision_at_10"],
        "precision_at_10_ci": score_row["precision_at_10_ci"],
        "precision_at_25": score_row["precision_at_25"],
        "revenue_capture_top20": score_row["revenue_capture_top20"],
        "revenue_capture_top20_ci": score_row["revenue_capture_top20_ci"],
        "mean_calibration_error": p_win_row["mean_calibration_error"],
        "calibration_bins": p_win_row["calibration_bins"],
        "spearman_score_price": round(rho, 4),
        "zombies_at_cut": int(zombie.sum()),
        "zombies_closed_after": zombies_closed,
        "zombies_won_after": zombies_won,
        "ranking_metrics_use": "priority_score",
        "probabilistic_metrics_use": "p_win",
    }

    # pessimistic sensitivity: censored -> Lost with value 0
    y_p = df["label"].fillna(0.0).to_numpy(dtype=float)
    pess_cands = {
        "random": np.random.default_rng(seed).random(len(df)),
        "price": df["sales_price"].to_numpy(dtype=float),
        "newest": -df["days_in_engaging"].to_numpy(dtype=float),
        "oldest": df["days_in_engaging"].to_numpy(dtype=float),
        "base_rate": df["product_rate"].to_numpy(dtype=float),
        "p_win": df["p_win"].to_numpy(dtype=float),
        "priority_score": df["priority_score"].to_numpy(dtype=float),
    }
    pessimistic = {
        k: {"auc_pr": round(auc_pr(y_p, s), 4), "auc_roc": round(auc_roc(y_p, s), 4)}
        for k, s in pess_cands.items()
    }

    shadow: dict[str, Any] | None = None
    if "p_model" in lab.columns and lab["p_model"].notna().all():
        pm = lab["p_model"].to_numpy(dtype=float)
        shadow = _candidate_row(y, v, agents, pm, idx, True)

    return CutEvaluation(
        cut=cut,
        backtest=backtest,
        baselines={k: rows[k] for k in BASELINES},
        by_signal={k: rows[k] for k in SIGNALS},
        pessimistic=pessimistic,
        shadow=shadow,
    )


def top5_late_share(frame: pd.DataFrame, zombie_days: int = 138, k: int = 5) -> float:
    """Share of the per-agent top ``k`` (by priority_score, all open deals) aged 120-138 days.

    The hazard peaks late in the cycle, so the score concentrates the top of every queue in
    that window; reported so nobody mistakes it for "old deals close more".
    """
    mask = top_k_per_agent_mask(
        frame["priority_score"].to_numpy(dtype=float), frame["sales_agent"].to_numpy(), k
    )
    days = frame["days_in_engaging"].to_numpy(dtype=float)
    late = (days >= LATE_WINDOW[0]) & (days <= min(LATE_WINDOW[1], zombie_days))
    return round(float(late[mask].mean()), 4) if mask.any() else float("nan")


# --- acceptance (section 7) -----------------------------------------------------------------------


def acceptance_checks(evaluation: CutEvaluation) -> list[dict[str, Any]]:
    b, rnd = evaluation.backtest, evaluation.baselines["random"]
    checks = [
        {
            "check": "brier_p_win <= 0.245",
            "value": b["brier"],
            "passed": b["brier"] <= ACCEPT_BRIER_MAX,
        },
        {
            "check": "mean_calibration_error <= 0.06",
            "value": b["mean_calibration_error"],
            "passed": b["mean_calibration_error"] <= ACCEPT_MCE_MAX,
        },
        {
            "check": "revenue_top20 >= 1.5 x random and CI low > random",
            "value": [b["revenue_capture_top20"], rnd["revenue_capture_top20"]],
            "passed": bool(
                b["revenue_capture_top20"]
                >= ACCEPT_REVENUE_VS_RANDOM * rnd["revenue_capture_top20"]
                and b["revenue_capture_top20_ci"][0] > rnd["revenue_capture_top20"]
            ),
        },
        {
            "check": "spearman(priority_score, sales_price) < 0.9",
            "value": b["spearman_score_price"],
            "passed": b["spearman_score_price"] < ACCEPT_SPEARMAN_MAX,
        },
        {
            "check": "zombies at cut that closed after (report; expected 0)",
            "value": b["zombies_closed_after"],
            "passed": True,
        },
    ]
    evaluation.accepted = checks
    return checks


def assert_accepted(evaluations: list[CutEvaluation]) -> None:
    failed = [
        f"{e.cut}: {c['check']} (value={c['value']})"
        for e in evaluations
        for c in (e.accepted or acceptance_checks(e))
        if not c["passed"]
    ]
    if failed:
        raise AcceptanceError("acceptance thresholds not met:\n  " + "\n  ".join(failed))


__all__ = [
    "ACCEPT_BRIER_MAX",
    "BASELINES",
    "N_BOOT",
    "REQUIRED_COLUMNS",
    "RNG_SEED",
    "SIGNALS",
    "AcceptanceError",
    "CutEvaluation",
    "acceptance_checks",
    "assert_accepted",
    "auc_pr",
    "auc_roc",
    "brier",
    "calibration_bins",
    "evaluate_cut",
    "lift_top_decile",
    "top5_late_share",
    "top_k_per_agent_mask",
    "mean_calibration_error",
    "per_agent_precision",
    "precision_at_k",
    "revenue_captured_top",
    "spearman",
]
