"""Temporal walk-forward backtest of the rules layer vs mandatory baselines (H9).

For each cut T: history = closed deals with close_date <= T; open_T = engage_date <= T and
(close_date > T or null). Score open_T with rules; evaluate on deals whose outcome is realised
after T (censored = still open at snapshot, reported separately + pessimistic sensitivity).

Run: cd solution/pipeline && uv run python analysis/10_backtest.py
Outputs: docs/figures/10_backtest.md, docs/figures/backtest_*.png
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import (
    BACKTEST_CUTS,
    FIG_DIR,
    RNG_SEED,
    SNAPSHOT_DATE,
    auc_pr,
    auc_roc,
    bootstrap_paired,
    brier,
    calibration_table,
    compute_history,
    lift_top_decile,
    load_clean,
    md_table,
    open_at,
    precision_at_k,
    revenue_captured_top,
    spearman,
    write_md,
)
from rules import Weights, score_rules

C1, C2, C3, INK2, SURFACE, GRID = "#2a78d6", "#eb6834", "#1baf7a", "#52514e", "#fcfcfb", "#e6e5e1"
plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "grid.color": GRID, "axes.grid": True, "axes.spines.top": False, "axes.spines.right": False, "font.size": 10})

MONTHLY_CUTS = list(pd.date_range("2017-04-30", "2017-10-31", freq="ME"))
sections: list[tuple[str, str]] = []
df = load_clean()
closed_all = df[df["is_closed"]]


def build_frame(T: pd.Timestamp) -> tuple[pd.DataFrame, dict, pd.DataFrame]:
    hist = compute_history(closed_all, T)
    closed_hist = closed_all[closed_all["close_date"] <= T]  # leakage-ok: history gate at T
    o = open_at(df, T)
    load = o.groupby("sales_agent").size().rename("open_load")
    o = o.merge(load, left_on="sales_agent", right_index=True, how="left")
    return o, hist, closed_hist


def candidates(o: pd.DataFrame, scored: pd.DataFrame, hist: dict) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(RNG_SEED)
    prod_rate = o[["product"]].merge(hist["by_product"][["product", "rate_smooth"]], on="product", how="left")["rate_smooth"].fillna(hist["p0"]).to_numpy()
    return {
        "aleatório": rng.random(len(o)),
        "sales_price": o["sales_price"].to_numpy(dtype=float),
        "mais novo primeiro": -o["days_in_engaging"].to_numpy(dtype=float),
        "mais antigo primeiro": o["days_in_engaging"].to_numpy(dtype=float),
        "taxa-base por produto": prod_rate,
        "regras · p_win": scored["p_win"].to_numpy(),
        "regras · expected_value": scored["expected_value"].to_numpy(),
        "regras · priority_score": scored["priority_score"].to_numpy(),
    }


def per_agent_precision(o: pd.DataFrame, s: np.ndarray, k: int) -> float:
    vals = []
    for _, g in o.assign(_s=s).groupby("sales_agent"):
        if len(g) >= k:
            vals.append(precision_at_k(g["label"].to_numpy(), g["_s"].to_numpy(), k))
    return float(np.mean(vals)) if vals else np.nan


def evaluate(o: pd.DataFrame, cands: dict[str, np.ndarray], probabilistic: set[str]) -> pd.DataFrame:
    y = o["label"].to_numpy(dtype=float)
    v = o["realized_value"].to_numpy(dtype=float)
    rows = []
    for name, s in cands.items():
        s = np.asarray(s, dtype=float)
        ap, ap_lo, ap_hi = bootstrap_paired(y, s, auc_pr)
        rc, rc_lo, rc_hi = bootstrap_paired(v, s, revenue_captured_top)
        rows.append(
            {
                "candidato": name,
                "AUC-PR": ap,
                "AUC-PR IC95": f"[{ap_lo:.3f}, {ap_hi:.3f}]",
                "AUC-ROC": auc_roc(y, s),
                "Brier": brier(y, s) if name in probabilistic else np.nan,
                "lift top decil": lift_top_decile(y, s),
                "P@10/agente": per_agent_precision(o, s, 10),
                "P@25/agente": per_agent_precision(o, s, 25),
                "receita top 20%": rc,
                "receita IC95": f"[{rc_lo:.3f}, {rc_hi:.3f}]",
            }
        )
    return pd.DataFrame(rows)


PROBABILISTIC = {"taxa-base por produto", "regras · p_win"}
summary_tables = {}
calib_frames = {}
weights_default = Weights()

for T in BACKTEST_CUTS:
    o, hist, closed_hist = build_frame(T)
    scored = score_rules(o, hist, closed_hist, weights_default)
    n_open, n_lab, n_cens = len(o), int(o["label"].notna().sum()), int(o["label"].isna().sum())
    base_rate = o["label"].mean()
    lab_mask = o["label"].notna().to_numpy()
    o_lab = o[lab_mask].reset_index(drop=True)
    scored_lab = scored[lab_mask].reset_index(drop=True)
    cands = candidates(o_lab, scored_lab, hist)
    tbl = evaluate(o_lab, cands, PROBABILISTIC)
    summary_tables[T] = tbl
    rho_price = spearman(scored["priority_score"].to_numpy(), scored["sales_price"].to_numpy())
    zomb = int(scored["is_zombie"].sum())
    print(f"\n=== T={T.date()} open={n_open} labeled={n_lab} censored={n_cens} base_rate={base_rate:.3f} zombies_at_T={zomb} spearman(score,price)={rho_price:.3f}")
    print(tbl.to_string(index=False))

    # calibration of rules p_win and product base rate
    cal = calibration_table(o_lab["label"].to_numpy(), scored_lab["p_win"].to_numpy(), 5)
    cal_b = calibration_table(o_lab["label"].to_numpy(), cands["taxa-base por produto"], 5)
    calib_frames[T] = (cal, cal_b)
    print("calibration rules p_win\n", cal.to_string(index=False))

    # pessimistic sensitivity: censored -> Lost, value 0
    o_pess = o.copy()
    o_pess["label"] = o_pess["label"].fillna(0.0)
    o_pess["realized_value"] = o_pess["realized_value"].fillna(0.0)
    scored_p = scored
    cands_p = candidates(o_pess.reset_index(drop=True), scored_p.reset_index(drop=True), hist)
    y = o_pess["label"].to_numpy()
    pess = pd.DataFrame([{"candidato": k, "AUC-PR (censurado=Lost)": auc_pr(y, v), "AUC-ROC": auc_roc(y, v)} for k, v in cands_p.items()])
    print("pessimistic\n", pess.to_string(index=False))

    sections.append(
        (
            f"Corte T = {T.date()}",
            f"Abertos em T: {n_open} · com desfecho até o snapshot: {n_lab} (taxa-base {base_rate:.3f}) · censurados (ainda abertos em {SNAPSHOT_DATE.date()}): {n_cens} · zumbis (> 138 d) em T: {zomb} · Spearman(priority_score, sales_price) = {rho_price:.3f}\n\n"
            + md_table(tbl)
            + "\n\nCalibração (5 bins) · regras p_win:\n\n"
            + md_table(cal)
            + "\n\nCalibração (5 bins) · taxa-base por produto:\n\n"
            + md_table(cal_b)
            + "\n\nSensibilidade pessimista (censurados tratados como Lost):\n\n"
            + md_table(pess),
        )
    )

# ---------------------------------------------------------------- weight variants (choose the simplest that does not lose)
variants = {
    "só produto (recomendado)": Weights(agent=0, agent_product=0, survival=0),
    "produto + sobrevivência": Weights(agent=0, agent_product=0, survival=1),
    "produto + agente": Weights(agent=1, agent_product=0, survival=0),
    "produto + agente + sobrevivência": Weights(agent=1, agent_product=0, survival=1),
    "produto + agente + agente×produto + sobrevivência": Weights(agent=1, agent_product=1, survival=1),
    "anterior + setor": Weights(agent=1, agent_product=1, survival=1, sector=1.0),
    "sobrevivência ×2": Weights(agent=1, agent_product=1, survival=2.0),
}
var_rows = []
for name, w in variants.items():
    row = {"variante": name}
    for T in BACKTEST_CUTS:
        o, hist, closed_hist = build_frame(T)
        lab = o["label"].notna().to_numpy()
        sc = score_rules(o, hist, closed_hist, w)
        y = o.loc[lab, "label"].to_numpy()
        row[f"AUC-PR {T.date()}"] = auc_pr(y, sc.loc[lab, "p_win"].to_numpy())
        row[f"Brier {T.date()}"] = brier(y, sc.loc[lab, "p_win"].to_numpy())
    var_rows.append(row)
var_tbl = pd.DataFrame(var_rows)
print("\nvariants\n", var_tbl.to_string(index=False))
sections.append(("Variantes de pesos da camada de regras (p_win)", md_table(var_tbl)))

# ---------------------------------------------------------------- monthly cuts (stability)
mon_rows = []
for T in MONTHLY_CUTS:
    o, hist, closed_hist = build_frame(T)
    lab = o["label"].notna().to_numpy()
    if lab.sum() < 100:
        continue
    sc = score_rules(o, hist, closed_hist, weights_default)
    ol = o[lab].reset_index(drop=True)
    y = ol["label"].to_numpy()
    mon_rows.append(
        {
            "T": T.date(),
            "n": int(lab.sum()),
            "taxa-base": y.mean(),
            "regras p_win": auc_pr(y, sc.loc[lab, "p_win"].to_numpy()),
            "mais novo": auc_pr(y, -ol["days_in_engaging"].to_numpy(dtype=float)),
            "mais antigo": auc_pr(y, ol["days_in_engaging"].to_numpy(dtype=float)),
            "produto": auc_pr(y, ol[["product"]].merge(hist["by_product"][["product", "rate_smooth"]], on="product", how="left")["rate_smooth"].fillna(hist["p0"]).to_numpy()),
            "preço": auc_pr(y, ol["sales_price"].to_numpy(dtype=float)),
        }
    )
mon_tbl = pd.DataFrame(mon_rows)
print("\nmonthly\n", mon_tbl.to_string(index=False))
sections.append(("Cortes mensais (AUC-PR, estabilidade)", md_table(mon_tbl)))

fig, ax = plt.subplots(figsize=(7.5, 3.6))
ax.plot(mon_tbl["T"].astype(str), mon_tbl["regras p_win"], color=C1, linewidth=2, marker="o", markersize=5, label="regras · p_win")
ax.plot(mon_tbl["T"].astype(str), mon_tbl["mais novo"], color=C2, linewidth=2, marker="o", markersize=5, label="mais novo primeiro")
ax.plot(mon_tbl["T"].astype(str), mon_tbl["mais antigo"], color=C3, linewidth=2, marker="o", markersize=5, label="mais antigo primeiro")
ax.plot(mon_tbl["T"].astype(str), mon_tbl["taxa-base"], color=INK2, linewidth=1, linestyle="--", label="taxa-base (AUC-PR do aleatório)")
ax.set_ylabel("AUC-PR")
ax.set_title("Backtest mensal · AUC-PR por corte T", loc="left", fontsize=11)
ax.legend(frameon=False, fontsize=8)
ax.tick_params(axis="x", labelsize=8)
fig.tight_layout()
fig.savefig(FIG_DIR / "backtest_monthly_aucpr.png", dpi=150)
plt.close(fig)

# calibration figure
fig, axes = plt.subplots(1, 2, figsize=(8, 3.6), sharey=True)
for ax, T in zip(axes, BACKTEST_CUTS):
    cal, cal_b = calib_frames[T]
    ax.plot([0.4, 0.9], [0.4, 0.9], color=GRID, linewidth=1)
    ax.plot(cal["p_mean"], cal["y_rate"], color=C1, marker="o", markersize=6, linewidth=2, label="regras · p_win")
    ax.plot(cal_b["p_mean"], cal_b["y_rate"], color=C2, marker="o", markersize=6, linewidth=2, label="taxa-base por produto")
    ax.set_title(f"T = {T.date()}", loc="left", fontsize=10)
    ax.set_xlabel("p_win previsto (média do bin)")
    ax.set_xlim(0.4, 0.9)
axes[0].set_ylabel("taxa real de Won")
axes[0].legend(frameon=False, fontsize=8)
fig.suptitle("Calibração em 5 bins", x=0.01, ha="left", fontsize=11)
fig.tight_layout()
fig.savefig(FIG_DIR / "backtest_calibration.png", dpi=150)
plt.close(fig)

# snapshot scoring summary (what the seller sees on 2017-12-31)
T = SNAPSHOT_DATE
hist = compute_history(closed_all, T)
open_snap = df[df["deal_stage"].isin(["Engaging", "Prospecting"])].copy()
open_snap["days_in_engaging"] = (T - open_snap["engage_date"]).dt.days
load = open_snap.groupby("sales_agent").size().rename("open_load")
open_snap = open_snap.merge(load, left_on="sales_agent", right_index=True, how="left")
sc = score_rules(open_snap, hist, closed_all, weights_default)
from rules import tiers_absolute

sc["tier"] = tiers_absolute(sc["priority_score"].to_numpy(), sc["confidence"].to_numpy())
snap = sc.groupby(["deal_stage", "is_zombie"]).agg(n=("p_win", "size"), p_win_mean=("p_win", "mean"), score_mean=("priority_score", "mean"), ev_sum=("expected_value", "sum")).reset_index()
tiers = sc.groupby("tier").agg(n=("p_win", "size"), score_min=("priority_score", "min"), score_max=("priority_score", "max"), zombies=("is_zombie", "sum"), prospecting=("deal_stage", lambda s: int((s == "Prospecting").sum()))).reset_index()
conf = sc["confidence"].value_counts().rename_axis("confidence").reset_index(name="n")
print("\nsnapshot\n", snap.to_string(index=False), "\n", tiers.to_string(index=False), "\n", conf.to_string(index=False))
print("spearman(score, price) snapshot:", spearman(sc["priority_score"].to_numpy(), sc["sales_price"].to_numpy()))
print("NaN scores:", int(sc["priority_score"].isna().sum()))
sections.append(("Snapshot 2017-12-31 · o que o vendedor veria", md_table(snap, "{:.2f}") + "\n\nTiers absolutos (A ≥ 75, B ≥ 55, C ≥ 35):\n\n" + md_table(tiers, "{:.1f}") + "\n\nConfiança:\n\n" + md_table(conf) + f"\n\nSpearman(priority_score, sales_price) = {spearman(sc['priority_score'].to_numpy(), sc['sales_price'].to_numpy()):.3f}; scores NaN: {int(sc['priority_score'].isna().sum())}."))

# example deals for the doc: top A alive with account, a zombie, a prospecting
ex = pd.concat(
    [
        sc[(~sc["is_zombie"]) & (sc["deal_stage"] == "Engaging") & sc["account"].notna()].sort_values("priority_score", ascending=False).head(1),
        sc[sc["is_zombie"]].sort_values("priority_score", ascending=False).head(1),
        sc[sc["deal_stage"] == "Prospecting"].sort_values("priority_score", ascending=False).head(1),
    ]
)
ex_out = ex[["opportunity_id", "sales_agent", "product", "account", "deal_stage", "days_in_engaging", "p_win", "expected_value", "urgency", "priority_score", "tier", "confidence"]].copy()
print("\nexamples\n", ex_out.to_string(index=False))
for _, r in ex.iterrows():
    print(r["opportunity_id"], [(x["code"], x["direction"], round(x["weight"], 3), x["n"], None if pd.isna(x["value"]) else round(x["value"], 3)) for x in r["reasons"]])
sections.append(("Deals-exemplo (snapshot)", md_table(ex_out, "{:.2f}") + "\n\n" + "\n".join(f"- `{r['opportunity_id']}`: " + "; ".join(f"{x['code']}({x['direction']}, w={x['weight']:.3f}, n={x['n']}, v={'' if pd.isna(x['value']) else round(x['value'], 3)})" for x in r["reasons"]) for _, r in ex.iterrows())))

out = write_md("10_backtest.md", sections)
print(f"\nwrote {out}")
