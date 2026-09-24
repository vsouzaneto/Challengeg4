"""Layer-2 candidate check: numpy logistic regression (no sklearn) on a point-in-time training frame.

Training frame for cut T: for each month-end m < T, deals open at m whose outcome is known by T
(close_date <= T). Features are computed with history <= m. Evaluate on deals open at T with
realised outcome. Compared against the rules layer and the trivial baselines from 10_backtest.py.
GBT cannot be run without a tree library here; the experiment plan is specified in docs/specs.

Run: cd solution/pipeline && uv run python analysis/20_model_candidates.py
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from _common import (
    BACKTEST_CUTS,
    ZOMBIE_DAYS,
    auc_pr,
    auc_roc,
    bootstrap_paired,
    brier,
    calibration_table,
    compute_history,
    fit_logreg,
    load_clean,
    md_table,
    open_at,
    predict_logreg,
    smooth_rate,
    write_md,
)
from rules import Weights, score_rules

df = load_clean()
closed_all = df[df["is_closed"]]
PRODUCTS = sorted(df["product"].unique())
sections: list[tuple[str, str]] = []


def features_at(m: pd.Timestamp) -> tuple[pd.DataFrame, dict]:
    """Point-in-time feature frame for deals open at m (history <= m only)."""
    hist = compute_history(closed_all, m)
    o = open_at(df, m)
    p0 = hist["p0"]
    load = o.groupby("sales_agent").size().rename("open_load")
    o = o.merge(load, left_on="sales_agent", right_index=True, how="left")
    f = pd.DataFrame(index=o.index)
    ag = o[["sales_agent"]].merge(hist["by_agent"][["sales_agent", "n", "k"]], on="sales_agent", how="left")
    f["agent_rate"] = smooth_rate(ag["k"].fillna(0), ag["n"].fillna(0), p0).to_numpy()
    ap = o[["sales_agent", "product"]].merge(hist["by_agent_product"][["sales_agent", "product", "n", "k"]], on=["sales_agent", "product"], how="left")
    f["agent_product_rate"] = smooth_rate(ap["k"].fillna(0), ap["n"].fillna(0), p0).to_numpy()
    pr = o[["product"]].merge(hist["by_product"][["product", "n", "k"]], on="product", how="left")
    f["product_rate"] = smooth_rate(pr["k"].fillna(0), pr["n"].fillna(0), p0).to_numpy()
    surv = hist["survival"].set_index("d")["p_win_given_alive"]
    d = o["days_in_engaging"].clip(upper=ZOMBIE_DAYS).astype(int)
    f["survival_rate"] = surv.reindex(d).fillna(p0).to_numpy()
    f["days"] = o["days_in_engaging"].to_numpy(dtype=float)
    f["log_days"] = np.log1p(f["days"])
    f["is_zombie"] = (o["days_in_engaging"] > ZOMBIE_DAYS).astype(float).to_numpy()
    f["log_price"] = np.log1p(o["sales_price"].to_numpy(dtype=float))
    f["account_known"] = o["account"].notna().astype(float).to_numpy()
    f["log_revenue"] = np.log1p(o["revenue"].fillna(0).to_numpy(dtype=float))
    f["open_load"] = o["open_load"].fillna(0).to_numpy(dtype=float)
    f["engage_month_sin"] = np.sin(2 * np.pi * o["engage_date"].dt.month.to_numpy() / 12)
    f["engage_month_cos"] = np.cos(2 * np.pi * o["engage_date"].dt.month.to_numpy() / 12)
    for p in PRODUCTS:
        f[f"prod_{p}"] = (o["product"] == p).astype(float).to_numpy()
    f["label"] = o["label"].to_numpy()
    f["close_date_"] = o["close_date"].to_numpy()  # leakage-ok: only to filter label-known-by-T rows, dropped before fit
    f["realized_value"] = o["realized_value"].to_numpy()
    return f, hist


# account_* features are FORBIDDEN as predictors (data-engineer finding, confirms H3): 100% of
# labelled deals have an account vs ~32% of still-open ones, so account_known encodes "already
# closed", never "will close". They are kept in the frame only for the "with account" contrast run.
FEATURE_SETS = {
    "LR · só regras-features (agent, agent×prod, product, survival)": ["agent_rate", "agent_product_rate", "product_rate", "survival_rate"],
    "LR · + idade, preço, carga (sem conta)": ["agent_rate", "agent_product_rate", "product_rate", "survival_rate", "log_days", "is_zombie", "log_price", "open_load"],
    "LR · + conta (PROIBIDO; só contraste)": ["agent_rate", "agent_product_rate", "product_rate", "survival_rate", "log_days", "is_zombie", "log_price", "open_load", "account_known", "log_revenue"],
    "LR · + sazonalidade engage_month": ["agent_rate", "agent_product_rate", "product_rate", "survival_rate", "log_days", "is_zombie", "log_price", "open_load", "engage_month_sin", "engage_month_cos"],
    "LR · só idade": ["log_days", "survival_rate"],
}

rows = []
coef_rows = []
for T in BACKTEST_CUTS:
    cuts = [m for m in pd.date_range("2017-03-31", T - pd.Timedelta(days=1), freq="ME")]
    frames = []
    for m in cuts:
        f, _ = features_at(m)
        f = f[(f["label"].notna()) & (f["close_date_"] <= T)]  # leakage-ok: label must be known by T
        f["cut"] = m
        frames.append(f)
    train = pd.concat(frames, ignore_index=True)
    test, hist_T = features_at(T)
    test = test[test["label"].notna()].reset_index(drop=True)
    y_tr = train["label"].to_numpy(dtype=float)
    y_te = test["label"].to_numpy(dtype=float)
    print(f"\n=== T={T.date()} train rows={len(train)} (cuts={len(cuts)}, won_rate={y_tr.mean():.3f}) test rows={len(test)} (won_rate={y_te.mean():.3f})")

    # rules for reference on the same test rows
    o_T = open_at(df, T)
    load = o_T.groupby("sales_agent").size().rename("open_load")
    o_T = o_T.merge(load, left_on="sales_agent", right_index=True, how="left")
    closed_hist = closed_all[closed_all["close_date"] <= T]  # leakage-ok: history gate
    sc = score_rules(o_T, hist_T, closed_hist, Weights())
    lab = o_T["label"].notna().to_numpy()
    p_rules = sc.loc[lab, "p_win"].to_numpy()
    ap, lo, hi = bootstrap_paired(y_te, p_rules, auc_pr)
    rows.append({"T": T.date(), "candidato": "regras · p_win", "AUC-PR": ap, "IC95": f"[{lo:.3f}, {hi:.3f}]", "AUC-ROC": auc_roc(y_te, p_rules), "Brier": brier(y_te, p_rules)})

    for name, cols in FEATURE_SETS.items():
        X_tr = train[cols].to_numpy(dtype=float)
        X_te = test[cols].to_numpy(dtype=float)
        mu, sd = X_tr.mean(0), X_tr.std(0) + 1e-9
        w = fit_logreg((X_tr - mu) / sd, y_tr, l2=5.0, iters=2000, lr=0.2)
        p_te = predict_logreg((X_te - mu) / sd, w)
        ap, lo, hi = bootstrap_paired(y_te, p_te, auc_pr)
        rows.append({"T": T.date(), "candidato": name, "AUC-PR": ap, "IC95": f"[{lo:.3f}, {hi:.3f}]", "AUC-ROC": auc_roc(y_te, p_te), "Brier": brier(y_te, p_te)})
        if name == "LR · + idade, preço, carga (sem conta)":
            for c, coef in zip(cols, w[1:]):
                coef_rows.append({"T": T.date(), "feature": c, "coef_std": coef})
        # blend
        for alpha in (0.5,):
            p_bl = alpha * p_rules + (1 - alpha) * p_te
            rows.append({"T": T.date(), "candidato": f"blend {alpha:.1f}·regras + {1-alpha:.1f}·({name.split('·')[1].strip()[:20]})", "AUC-PR": auc_pr(y_te, p_bl), "IC95": "", "AUC-ROC": auc_roc(y_te, p_bl), "Brier": brier(y_te, p_bl)})
    # calibration of the fuller LR
    cols = FEATURE_SETS["LR · + idade, preço, carga (sem conta)"]
    X_tr = train[cols].to_numpy(dtype=float)
    X_te = test[cols].to_numpy(dtype=float)
    mu, sd = X_tr.mean(0), X_tr.std(0) + 1e-9
    w = fit_logreg((X_tr - mu) / sd, y_tr, l2=5.0, iters=2000, lr=0.2)
    p_te = predict_logreg((X_te - mu) / sd, w)
    cal = calibration_table(y_te, p_te, 5)
    print("LR calibration\n", cal.to_string(index=False))
    sections.append((f"Calibração LR (+ idade, preço, carga, sem conta) · T={T.date()}", md_table(cal)))

res = pd.DataFrame(rows)
print("\n", res.to_string(index=False))
coefs = pd.DataFrame(coef_rows).pivot(index="feature", columns="T", values="coef_std").reset_index()
print("\ncoefficients (standardised)\n", coefs.to_string(index=False))
sections.insert(0, ("Candidatos de modelo vs regras (AUC-PR nos deals abertos em T com desfecho)", md_table(res)))
sections.insert(1, ("Coeficientes padronizados da LR (+ idade, preço, carga, sem conta)", md_table(coefs)))
    # account_known share: labelled vs censored, per cut (why account_* is forbidden)
acc_rows = []
for T in BACKTEST_CUTS:
    o = open_at(df, T)
    acc_rows.append({"T": T.date(), "account_known · com desfecho": o.loc[o["label"].notna(), "account"].notna().mean(), "account_known · censurados": o.loc[o["label"].isna(), "account"].notna().mean()})
sections.insert(2, ("account_known entre deals com desfecho vs censurados (por que é proibido como feature)", md_table(pd.DataFrame(acc_rows))))
out = write_md("20_model_candidates.md", sections)
print(f"\nwrote {out}")
