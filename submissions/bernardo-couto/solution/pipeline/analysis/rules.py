"""Prototype of the rules layer (layer 1) in pandas. Pure functions; the ML engineer ports them.

score = f(p_win, expected_value, urgency). Every adjustment emits a reason code from the shared
``ReasonCode`` enum. Weights are named so the backtest can vary them.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from _common import PRIOR_STRENGTH, ZOMBIE_DAYS, smooth_rate

MAX_LIST_PRICE = 26768.0  # GTK 500, normalises the value axis


@dataclass(frozen=True)
class Weights:
    # log-odds multipliers on p_win adjustments (1.0 = take the historical shift at face value)
    # Defaults = recommended configuration after 10_backtest/11_diagnostics: no historical
    # adjustment has out-of-time signal (AUC-ROC ~0.5), so they are informative (weight 0).
    agent: float = 0.0
    agent_product: float = 0.0
    sector: float = 0.0
    survival: float = 0.0
    zombie_p_factor: float = 0.5  # p_win multiplier when days > ZOMBIE_DAYS (not estimable; conservative)
    # priority_score additive weights (sum to 100)
    w_p: float = 25.0
    w_v: float = 35.0
    w_u: float = 40.0  # >= 40 keeps Spearman(score, price) < 0.9 (11_diagnostics grid)
    prior_a: float = PRIOR_STRENGTH
    min_group_n: int = 30  # below this the group's evidence is "small"
    overload_quantile: float = 0.75
    extra: dict = field(default_factory=dict)


def logit(p: np.ndarray) -> np.ndarray:
    p = np.clip(p, 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p))


def sigmoid(z: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-z))


def _lookup(df: pd.DataFrame, table: pd.DataFrame, keys: list[str], p0: float, a: float) -> tuple[np.ndarray, np.ndarray]:
    """Return (smoothed_rate, n) aligned to df for the group keys; unseen groups -> (p0, 0)."""
    t = table[keys + ["n", "k"]].copy()
    m = df[keys].merge(t, on=keys, how="left")
    n = m["n"].fillna(0).to_numpy(dtype=float)
    k = m["k"].fillna(0).to_numpy(dtype=float)
    return smooth_rate(k, n, p0, a), n


def hazard14(survival: pd.DataFrame, closed_hist: pd.DataFrame) -> pd.DataFrame:
    """14-day conditional win hazard: P(won and closes within (d, d+14] | still open at d)."""
    cyc = closed_hist["cycle_days"].to_numpy()
    won = closed_hist["won"].to_numpy()
    rows = []
    for d in range(0, ZOMBIE_DAYS + 1):
        alive = cyc > d
        n = alive.sum()
        win_soon = ((cyc > d) & (cyc <= d + 14) & (won == 1)).sum()
        rows.append({"d": d, "hazard14": win_soon / n if n >= 30 else np.nan})
    h = pd.DataFrame(rows)
    h["hazard14"] = h["hazard14"].ffill()
    return h


def score_rules(deals: pd.DataFrame, hist: dict, closed_hist: pd.DataFrame, w: Weights = Weights()) -> pd.DataFrame:
    """Score open deals. ``deals`` needs: product, sales_agent, account, sector, sales_price,
    deal_stage, days_in_engaging (NaN for Prospecting), open_load (agent's open deals at as_of).
    ``hist`` = compute_history(closed, as_of); ``closed_hist`` = closed deals with close_date <= as_of.
    Returns deals + p_win, expected_value, urgency, priority_score, confidence, reasons (list of dicts).
    """
    d = deals.reset_index(drop=True).copy()
    p0 = hist["p0"]
    a = w.prior_a
    n_rows = len(d)
    reasons: list[list[dict]] = [[] for _ in range(n_rows)]

    # --- product base rate
    p_prod, n_prod = _lookup(d, hist["by_product"], ["product"], p0, a)
    z = logit(p_prod)
    for i in range(n_rows):
        reasons[i].append({"code": "PRODUCT_BASE_RATE", "direction": "i", "weight": float(p_prod[i] - p0), "n": int(n_prod[i]), "value": float(p_prod[i])})

    # --- agent track record (shift vs global, in log-odds)
    p_ag, n_ag = _lookup(d, hist["by_agent"], ["sales_agent"], p0, a)
    shift_ag = w.agent * (logit(p_ag) - logit(np.full(n_rows, p0)))
    z = z + shift_ag
    for i in range(n_rows):
        reasons[i].append({"code": "AGENT_TRACK_RECORD", "direction": "+" if shift_ag[i] > 0 else "-" if shift_ag[i] < 0 else "i", "weight": float(p_ag[i] - p0), "n": int(n_ag[i]), "value": float(p_ag[i])})

    # --- agent x product fit (shift vs agent's own rate)
    p_ap, n_ap = _lookup(d, hist["by_agent_product"], ["sales_agent", "product"], p0, a)
    shift_ap = w.agent_product * (logit(p_ap) - logit(p_ag))
    z = z + shift_ap
    for i in range(n_rows):
        reasons[i].append({"code": "AGENT_PRODUCT_FIT", "direction": "+" if shift_ap[i] > 0 else "-" if shift_ap[i] < 0 else "i", "weight": float(p_ap[i] - p_ag[i]), "n": int(n_ap[i]), "value": float(p_ap[i])})

    # --- sector (only when account known)
    known = d["account"].notna().to_numpy()
    p_sec, n_sec = _lookup(d.assign(sector=d["sector"].fillna("__none__")), hist["by_sector"].assign(sector=hist["by_sector"]["sector"].fillna("__none__")), ["sector"], p0, a)
    shift_sec = np.where(known, w.sector * (logit(p_sec) - logit(np.full(n_rows, p0))), 0.0)
    z = z + shift_sec
    for i in range(n_rows):
        if known[i]:
            reasons[i].append({"code": "SECTOR_FIT", "direction": "i" if w.sector == 0 else ("+" if shift_sec[i] > 0 else "-"), "weight": float(p_sec[i] - p0) * (1 if w.sector else 0), "n": int(n_sec[i]), "value": float(p_sec[i])})
        else:
            reasons[i].append({"code": "ACCOUNT_UNKNOWN", "direction": "i", "weight": 0.0, "n": 0, "value": np.nan})

    # --- survival / zombie
    surv = hist["survival"].set_index("d")["p_win_given_alive"]
    haz = hazard14(hist["survival"], closed_hist).set_index("d")["hazard14"]
    haz_max = float(np.nanmax(haz.to_numpy())) or 1.0
    days = d["days_in_engaging"].to_numpy(dtype=float)
    is_prosp = np.isnan(days)
    is_zombie = (~is_prosp) & (days > ZOMBIE_DAYS)
    alive = (~is_prosp) & (~is_zombie)
    d_int = np.where(alive, np.nan_to_num(days, nan=0).astype(int), 0)
    s_d = surv.reindex(d_int).to_numpy()
    s_d = np.where(np.isnan(s_d), p0, s_d)
    shift_surv = np.where(alive, w.survival * (logit(s_d) - logit(np.full(n_rows, p0))), 0.0)
    z = z + shift_surv
    p_win = sigmoid(z)
    p_win = np.where(is_zombie, p_win * w.zombie_p_factor, p_win)

    urgency = np.full(n_rows, 0.5)
    h_d = haz.reindex(d_int).to_numpy()
    urgency = np.where(alive, np.nan_to_num(h_d, nan=0.0) / haz_max, urgency)
    urgency = np.where(is_zombie, 0.2, urgency)
    urgency = np.clip(urgency, 0, 1)

    for i in range(n_rows):
        if is_prosp[i]:
            reasons[i].append({"code": "PROSPECTING_NO_TIMELINE", "direction": "i", "weight": 0.0, "n": 0, "value": np.nan})
        elif is_zombie[i]:
            reasons[i].append({"code": "ZOMBIE_RISK", "direction": "-", "weight": float(p_win[i] - p_win[i] / w.zombie_p_factor), "n": int(days[i]), "value": float(days[i])})
        else:
            reasons[i].append({"code": "SURVIVAL_POSITIVE" if shift_surv[i] >= 0 else "SURVIVAL_POSITIVE", "direction": "+" if shift_surv[i] > 0 else "i", "weight": float(s_d[i] - p0), "n": int(days[i]), "value": float(s_d[i])})

    # --- expected value
    ratio = d[["product"]].merge(hist["value_ratio"], on="product", how="left")["value_ratio"].fillna(1.0).to_numpy()
    ev_gross = d["sales_price"].to_numpy(dtype=float) * ratio
    expected_value = ev_gross * p_win
    value_norm = np.log1p(ev_gross) / np.log1p(MAX_LIST_PRICE)
    price = d["sales_price"].to_numpy(dtype=float)
    for i in range(n_rows):
        if price[i] >= 4000:
            reasons[i].append({"code": "HIGH_TICKET", "direction": "+", "weight": float(w.w_v * value_norm[i]), "n": 0, "value": float(ev_gross[i])})
        elif price[i] <= 600:
            reasons[i].append({"code": "LOW_TICKET", "direction": "-", "weight": float(w.w_v * value_norm[i]), "n": 0, "value": float(ev_gross[i])})

    # --- agent overload (informative; H5 refuted)
    load = d["open_load"].fillna(0).to_numpy(dtype=float)
    thr = np.quantile(load, w.overload_quantile) if n_rows else np.inf
    for i in range(n_rows):
        if load[i] >= thr and load[i] > 0:
            reasons[i].append({"code": "AGENT_OVERLOAD", "direction": "i", "weight": 0.0, "n": int(load[i]), "value": float(load[i])})

    # --- priority score (additive, weights in points)
    p_scaled = np.clip((p_win - 0.30) / 0.50, 0, 1)  # 0.30 -> 0, 0.80 -> 1
    score = w.w_p * p_scaled + w.w_v * value_norm + w.w_u * urgency
    score = np.where(is_zombie, np.minimum(score, 49.0), score)  # zombies never tier A (tier A >= 75 absolute)
    score = np.clip(score, 0, 100)

    # --- confidence
    small = (n_ag < w.min_group_n) | (n_prod < w.min_group_n)
    conf = np.where(~known | is_prosp, "media", "alta")
    conf = np.where(small | is_zombie | (~known & is_prosp), "baixa", conf)

    d["p_win"] = p_win
    d["expected_value"] = expected_value
    d["ev_gross"] = ev_gross
    d["urgency"] = urgency
    d["priority_score"] = score
    d["confidence"] = conf
    d["is_zombie"] = is_zombie
    d["reasons"] = reasons
    return d


def tiers_absolute(score: np.ndarray, confidence: np.ndarray | None = None) -> np.ndarray:
    """A >= 75, B >= 55, C >= 35, else D. Tier A additionally requires confidence != 'baixa'
    (a Prospecting deal without account or a zombie can never be the seller's first call)."""
    t = np.select([score >= 75, score >= 55, score >= 35], ["A", "B", "C"], default="D")
    if confidence is not None:
        t = np.where((t == "A") & (confidence == "baixa"), "B", t)
    return t
