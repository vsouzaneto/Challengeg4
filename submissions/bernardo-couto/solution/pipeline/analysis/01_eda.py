"""Hypothesis-driven EDA (H1-H8, H10, H11 of 00_hypotheses.md). H9 lives in 10_backtest.py.

Run: cd solution/pipeline && uv run python analysis/01_eda.py
Outputs: docs/figures/eda_*.png and docs/figures/01_eda.md (tables + verdict numbers).
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
    SNAPSHOT_DATE,
    ZOMBIE_DAYS,
    auc_roc,
    compute_history,
    cramers_v,
    load_clean,
    md_table,
    open_at,
    smooth_rate,
    spearman,
    survival_curve,
    wilson,
    write_md,
)

# Reference palette (dataviz skill), light mode.
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "axes.edgecolor": GRID,
        "axes.labelcolor": INK2,
        "xtick.color": INK2,
        "ytick.color": INK2,
        "text.color": INK,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.size": 10,
    }
)

sections: list[tuple[str, str]] = []
df = load_clean()
closed = df[df["is_closed"]].copy()
engaging = df[df["deal_stage"] == "Engaging"].copy()
engaging["days_in_engaging"] = (SNAPSHOT_DATE - engaging["engage_date"]).dt.days
p0 = closed["won"].mean()
print(f"closed={len(closed)} won_rate={p0:.4f} engaging={len(engaging)} prospecting={(df.deal_stage == 'Prospecting').sum()}")


def rate_table(g: pd.DataFrame, key: str) -> pd.DataFrame:
    rows = []
    for _, r in g.iterrows():
        p, lo, hi = wilson(r["k"], r["n"])
        rows.append({key: r[key], "n": int(r["n"]), "win_rate": p, "ci_lo": lo, "ci_hi": hi, "smoothed_a20": smooth_rate(r["k"], r["n"], p0)})
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------- H1 survival
surv = survival_curve(closed)
buckets = [0, 7, 14, 30, 45, 60, 75, 90, 105, 120, 138]
rows = []
for d in buckets:
    r = surv.loc[surv["d"] == d].iloc[0]
    rows.append({"open_after_days": d, "n_still_open": r["n_alive"], "p_win_given_open": r["p_win_given_alive"], "ci_lo": r["lo"], "ci_hi": r["hi"]})
h1 = pd.DataFrame(rows)
print("\nH1 survival\n", h1.to_string(index=False))
peak = surv.loc[surv["n_alive"] >= 100, "p_win_given_alive"].max()
peak_d = int(surv.loc[surv["p_win_given_alive"] == peak, "d"].iloc[0])
print(f"H1 peak p_win|alive = {peak:.3f} at d={peak_d}; max cycle = {closed.cycle_days.max()}")

fig, ax = plt.subplots(figsize=(7, 3.6))
ax.fill_between(surv["d"], surv["lo"], surv["hi"], color=C1, alpha=0.15, linewidth=0)
ax.plot(surv["d"], surv["p_win_given_alive"], color=C1, linewidth=2)
ax.axhline(p0, color=INK2, linewidth=1, linestyle="--")
ax.text(2, p0 + 0.01, f"taxa-base {p0:.0%}", color=INK2, fontsize=9)
ax.set_xlabel("dias em Engaging (d)")
ax.set_ylabel("P(Won | ainda aberto após d)")
ax.set_title("H1 · Sobrevivência em Engaging (deals fechados, IC 95% Wilson)", loc="left", fontsize=11)
ax.set_ylim(0.4, 1.0)
fig.tight_layout()
fig.savefig(FIG_DIR / "eda_h1_survival.png", dpi=150)
plt.close(fig)
sections.append(("H1 · P(Won | aberto após d dias)", md_table(h1) + f"\n\nPico (n≥100): {peak:.3f} em d={peak_d}. Ciclo máximo observado: {int(closed.cycle_days.max())} dias. Figura: `eda_h1_survival.png`."))

# ----------------------------------------------------------------------------- H11 snapshot ages
age = engaging["days_in_engaging"]
h11 = pd.DataFrame(
    {
        "métrica": ["n Engaging", "mín", "p25", "mediana", "p75", "máx", f"> {ZOMBIE_DAYS} d (n)", f"> {ZOMBIE_DAYS} d (%)", "≤ 90 d (n)"],
        "valor": [len(age), age.min(), age.quantile(0.25), age.median(), age.quantile(0.75), age.max(), (age > ZOMBIE_DAYS).sum(), 100 * (age > ZOMBIE_DAYS).mean(), (age <= 90).sum()],
    }
)
print("\nH11 snapshot ages\n", h11.to_string(index=False))
cens_rows = []
for T in BACKTEST_CUTS:
    o = open_at(df, T)
    cens_rows.append({"T": T.date(), "open_at_T": len(o), "labeled": int(o["label"].notna().sum()), "censored_still_open": int(o["label"].isna().sum()), "min_age_censored": int(o.loc[o["label"].isna(), "days_in_engaging"].min()) if o["label"].isna().any() else None})
h11b = pd.DataFrame(cens_rows)
print(h11b.to_string(index=False))

fig, ax = plt.subplots(figsize=(7, 3.4))
ax.hist(age, bins=range(0, 440, 14), color=C1, edgecolor=SURFACE, linewidth=0.8)
ax.axvline(ZOMBIE_DAYS, color=C2, linewidth=1.5)
ax.text(ZOMBIE_DAYS + 4, ax.get_ylim()[1] * 0.9, f"{ZOMBIE_DAYS} d = ciclo máximo histórico", color=C2, fontsize=9)
ax.set_xlabel("dias em Engaging no snapshot (2017-12-31)")
ax.set_ylabel("deals")
ax.set_title("H11 · Idade dos 1.589 deals Engaging no snapshot", loc="left", fontsize=11)
fig.tight_layout()
fig.savefig(FIG_DIR / "eda_h11_snapshot_ages.png", dpi=150)
plt.close(fig)
sections.append(("H11 · Idade do pipeline Engaging no snapshot", md_table(h11, "{:.1f}") + "\n\nCensura por corte de backtest:\n\n" + md_table(h11b) + "\n\nFigura: `eda_h11_snapshot_ages.png`."))

# ----------------------------------------------------------------------------- H2 discriminative power
hist_full = compute_history(closed, SNAPSHOT_DATE)
fac_rows = []
for name, key in [("produto", "product"), ("agente", "sales_agent"), ("setor", "sector"), ("manager", "manager"), ("escritório", "regional_office")]:
    g = hist_full[f"by_{key}"] if f"by_{key}" in hist_full else closed.groupby(key)["won"].agg(n="size", k="sum").reset_index()
    g = g.assign(rate_smooth=smooth_rate(g["k"], g["n"], p0), rate_raw=g["k"] / g["n"])
    fac_rows.append({"fator": name, "grupos": len(g), "spread_raw_pp": 100 * (g["rate_raw"].max() - g["rate_raw"].min()), "spread_smooth_a20_pp": 100 * (g["rate_smooth"].max() - g["rate_smooth"].min()), "cramers_v": cramers_v(closed[key].fillna("NA"), closed["won"])})
# temporal single-factor AUC: history <= T, evaluate on deals open at T that closed later
T = BACKTEST_CUTS[1]
hist_T = compute_history(closed, T)
o = open_at(df, T)
o = o[o["label"].notna()]
for name, key, tbl in [("produto", "product", "by_product"), ("agente", "sales_agent", "by_agent"), ("setor", "sector", "by_sector"), ("agente×produto", None, "by_agent_product")]:
    h = hist_T[tbl]
    if key is None:
        m = o.merge(h[["sales_agent", "product", "rate_smooth"]], on=["sales_agent", "product"], how="left")
    else:
        m = o.merge(h[[key, "rate_smooth"]], on=key, how="left")
    s = m["rate_smooth"].fillna(hist_T["p0"]).to_numpy()
    auc = auc_roc(m["label"].to_numpy(), s)
    for r in fac_rows:
        if r["fator"] == name:
            r[f"auc_roc_T={T.date()}"] = auc
    if name == "agente×produto":
        fac_rows.append({"fator": name, "grupos": len(h), "spread_raw_pp": np.nan, "spread_smooth_a20_pp": 100 * (h["rate_smooth"].max() - h["rate_smooth"].min()), "cramers_v": np.nan, f"auc_roc_T={T.date()}": auc})
h2 = pd.DataFrame(fac_rows)
print("\nH2 discriminative power\n", h2.to_string(index=False))
sections.append(("H2 · Poder discriminativo por fator", md_table(h2) + f"\n\nAUC calculado com histórico ≤ {T.date()} sobre {len(o)} deals abertos em T e fechados depois."))

# per-group tables for the doc
prod_t = rate_table(hist_full["by_product"].merge(df[["product", "sales_price"]].drop_duplicates(), on="product"), "product")
prod_t = prod_t.merge(df[["product", "sales_price"]].drop_duplicates(), on="product").sort_values("sales_price")
agent_t = rate_table(hist_full["by_agent"], "sales_agent").sort_values("win_rate", ascending=False)
sector_t = rate_table(hist_full["by_sector"], "sector").sort_values("win_rate", ascending=False)

fig, ax = plt.subplots(figsize=(7, 5.5))
a = agent_t.sort_values("win_rate")
ax.hlines(a["sales_agent"], a["ci_lo"], a["ci_hi"], color=C1, alpha=0.35, linewidth=2)
ax.plot(a["win_rate"], a["sales_agent"], "o", color=C1, markersize=5)
ax.axvline(p0, color=INK2, linestyle="--", linewidth=1)
ax.set_xlabel("win rate (IC 95% Wilson)")
ax.set_title("H2 · Win rate por agente (todos os fechados)", loc="left", fontsize=11)
ax.grid(axis="x")
ax.tick_params(axis="y", labelsize=7)
fig.tight_layout()
fig.savefig(FIG_DIR / "eda_h2_agent_winrate.png", dpi=150)
plt.close(fig)

# ----------------------------------------------------------------------------- H3 unknown account
closed_null = closed["account"].isna().mean()
bins = [0, 30, 60, 90, 138, 200, 300, 500]
engaging["age_bin"] = pd.cut(engaging["days_in_engaging"], bins, right=True)
h3 = engaging.groupby("age_bin", observed=True)["account_known"].agg(n="size", k="sum").reset_index()
h3[["rate", "ci_lo", "ci_hi"]] = pd.DataFrame([wilson(k, n) for k, n in zip(h3["k"], h3["n"])])
h3["age_bin"] = h3["age_bin"].astype(str)
rho_h3 = spearman(engaging["days_in_engaging"].to_numpy(), engaging["account_known"].astype(int).to_numpy())
prosp_known = df.loc[df["deal_stage"] == "Prospecting", "account_known"].mean()
print("\nH3 account_known by age\n", h3.to_string(index=False), f"\nspearman={rho_h3:.3f} closed_null={closed_null:.3f} prospecting_known={prosp_known:.3f}")
sections.append(("H3 · account_known por idade (Engaging)", md_table(h3) + f"\n\nSpearman(idade, account_known) = {rho_h3:.3f}. Conta nula entre fechados: {closed_null:.1%}. Conta conhecida em Prospecting: {prosp_known:.1%}."))

# ----------------------------------------------------------------------------- H4 seasonality
closed["engage_month"] = closed["engage_date"].dt.month
closed["close_month"] = closed["close_date"].dt.month  # leakage-ok: analysis of outcome timing only
closed["engage_year"] = closed["engage_date"].dt.year


def month_table(col):
    g = closed.groupby(col)["won"].agg(n="size", k="sum").reset_index()
    g[["rate", "ci_lo", "ci_hi"]] = pd.DataFrame([wilson(k, n) for k, n in zip(g["k"], g["n"])])
    return g


em = month_table("engage_month")
cm = month_table("close_month")
em_spread = 100 * (em["rate"].max() - em["rate"].min())
cm_spread = 100 * (cm["rate"].max() - cm["rate"].min())
qe = cm.loc[cm["close_month"].isin([3, 6, 9, 12]), "rate"].mean()
nqe = cm.loc[~cm["close_month"].isin([3, 6, 9, 12]), "rate"].mean()
# stability across years for engage months present in both
both = closed.groupby(["engage_year", "engage_month"])["won"].agg(n="size", k="sum").reset_index()
both["rate"] = both["k"] / both["n"]
piv = both.pivot(index="engage_month", columns="engage_year", values="rate")
print("\nH4 engage_month\n", em.to_string(index=False), f"\nspread={em_spread:.1f}pp")
print("H4 close_month\n", cm.to_string(index=False), f"\nspread={cm_spread:.1f}pp  quarter-end mean={qe:.3f} other={nqe:.3f}")
print(piv)
fig, axes = plt.subplots(1, 2, figsize=(9, 3.4), sharey=True)
for ax, t, col, title in [(axes[0], em, "engage_month", "mês de engajamento (utilizável)"), (axes[1], cm, "close_month", "mês de fechamento (leakage, só diagnóstico)")]:
    ax.bar(t[col], t["rate"], color=C1, width=0.7)
    ax.errorbar(t[col], t["rate"], yerr=[t["rate"] - t["ci_lo"], t["ci_hi"] - t["rate"]], fmt="none", ecolor=INK2, elinewidth=1, capsize=2)
    ax.axhline(p0, color=INK2, linestyle="--", linewidth=1)
    ax.set_xticks(range(1, 13))
    ax.set_title(title, loc="left", fontsize=10)
    ax.set_ylim(0.3, 0.9)
axes[0].set_ylabel("win rate")
fig.suptitle("H4 · Sazonalidade", x=0.01, ha="left", fontsize=11)
fig.tight_layout()
fig.savefig(FIG_DIR / "eda_h4_seasonality.png", dpi=150)
plt.close(fig)
sections.append(("H4 · Sazonalidade", "Por mês de engajamento:\n\n" + md_table(em) + f"\n\nSpread engage_month = {em_spread:.1f} pp.\n\nPor mês de fechamento (diagnóstico; não utilizável como feature):\n\n" + md_table(cm) + f"\n\nSpread close_month = {cm_spread:.1f} pp; média fim de trimestre {qe:.3f} vs outros {nqe:.3f}.\n\nEstabilidade entre anos (win rate por engage_month):\n\n" + md_table(piv.reset_index()) + "\n\nFigura: `eda_h4_seasonality.png`."))

# ----------------------------------------------------------------------------- H5 agent load
h5_rows = []
for T in BACKTEST_CUTS:
    o = open_at(df, T)
    load = o.groupby("sales_agent").size().rename("open_load")
    lab = o[o["label"].notna()]
    per_agent = lab.groupby("sales_agent")["label"].agg(n="size", k="sum").join(load)
    per_agent["rate"] = per_agent["k"] / per_agent["n"]
    q = per_agent["open_load"].quantile([0.25, 0.75])
    hi = lab[lab["sales_agent"].isin(per_agent.index[per_agent["open_load"] >= q[0.75]])]["label"].to_numpy()
    lo = lab[lab["sales_agent"].isin(per_agent.index[per_agent["open_load"] <= q[0.25]])]["label"].to_numpy()
    rng = np.random.default_rng(1)
    diffs = [rng.choice(hi, len(hi)).mean() - rng.choice(lo, len(lo)).mean() for _ in range(2000)]
    rho = spearman(per_agent["open_load"].to_numpy(), per_agent["rate"].to_numpy())
    # deal-level: load of the agent as feature vs outcome
    rho_deal = spearman(lab["sales_agent"].map(load).to_numpy(), lab["label"].to_numpy())
    h5_rows.append({"T": T.date(), "agents": len(per_agent), "load_q25": q[0.25], "load_q75": q[0.75], "rate_high_load": hi.mean(), "rate_low_load": lo.mean(), "diff_pp": 100 * (hi.mean() - lo.mean()), "diff_ci_lo_pp": 100 * np.percentile(diffs, 2.5), "diff_ci_hi_pp": 100 * np.percentile(diffs, 97.5), "spearman_agent_level": rho, "spearman_deal_level": rho_deal})
h5 = pd.DataFrame(h5_rows)
print("\nH5 agent load\n", h5.to_string(index=False))
sections.append(("H5 · Carga do agente em T vs win rate posterior", md_table(h5)))

# ----------------------------------------------------------------------------- H6 price vs win rate
rho_h6 = spearman(prod_t["sales_price"].to_numpy(), prod_t["win_rate"].to_numpy())
print("\nH6 product\n", prod_t.to_string(index=False), f"\nspearman(price, rate)={rho_h6:.3f}")
sections.append(("H6 · Win rate por produto (ordenado por preço)", md_table(prod_t[["product", "sales_price", "n", "win_rate", "ci_lo", "ci_hi", "smoothed_a20"]]) + f"\n\nSpearman(sales_price, win_rate) = {rho_h6:.3f} (7 produtos)."))

# ----------------------------------------------------------------------------- H7 account history
h7_rows = []
for T in BACKTEST_CUTS:
    hist_T = compute_history(closed, T)
    acc = hist_T["by_account"]
    acc = acc[acc["n"] >= 10]
    med = acc["rate_smooth"].median()
    hi_acc = set(acc.loc[acc["rate_smooth"] > med, "account"])
    lo_acc = set(acc.loc[acc["rate_smooth"] <= med, "account"])
    o = open_at(df, T)
    lab = o[o["label"].notna() & o["account"].notna()]
    hi = lab[lab["account"].isin(hi_acc)]["label"].to_numpy()
    lo = lab[lab["account"].isin(lo_acc)]["label"].to_numpy()
    rng = np.random.default_rng(2)
    diffs = [rng.choice(hi, len(hi)).mean() - rng.choice(lo, len(lo)).mean() for _ in range(2000)]
    # continuous: spearman between account prior rate and outcome
    m = lab.merge(acc[["account", "rate_smooth"]], on="account", how="inner")
    rho = spearman(m["rate_smooth"].to_numpy(), m["label"].to_numpy())
    auc = auc_roc(m["label"].to_numpy(), m["rate_smooth"].to_numpy())
    h7_rows.append({"T": T.date(), "accounts_n>=10": len(acc), "deals_eval": len(m), "rate_hi_hist": hi.mean(), "rate_lo_hist": lo.mean(), "diff_pp": 100 * (hi.mean() - lo.mean()), "ci_lo_pp": 100 * np.percentile(diffs, 2.5), "ci_hi_pp": 100 * np.percentile(diffs, 97.5), "spearman": rho, "auc_roc": auc})
h7 = pd.DataFrame(h7_rows)
print("\nH7 account history\n", h7.to_string(index=False))
sections.append(("H7 · Histórico da conta (≤ T) vs desfecho posterior", md_table(h7)))

# ----------------------------------------------------------------------------- H8 value ratio
won = closed[closed["won"] == 1.0].copy()
won["ratio"] = won["close_value"] / won["sales_price"]  # leakage-ok: EV multiplier calibration, Won history only
h8 = won.groupby("product")["ratio"].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95])[["count", "5%", "25%", "50%", "75%", "95%"]].reset_index()
h8["iqr"] = h8["75%"] - h8["25%"]
by_agent_ratio = won.groupby("sales_agent")["ratio"].median()
h8_agent_spread = by_agent_ratio.max() - by_agent_ratio.min()
lost_zero = (closed.loc[closed["won"] == 0, "close_value"] == 0).mean()
print("\nH8 value ratio\n", h8.to_string(index=False), f"\nagent median-ratio spread={h8_agent_spread:.3f}  lost close_value==0: {lost_zero:.3f}")
sections.append(("H8 · close_value / sales_price entre Won", md_table(h8) + f"\n\nSpread da razão mediana entre agentes: {h8_agent_spread:.3f}. Lost com close_value = 0: {lost_zero:.1%}."))

# ----------------------------------------------------------------------------- H10 account size
h10_rows = []
for col in ["revenue", "employees"]:
    c = closed[closed[col].notna()].copy()
    c["q"] = pd.qcut(c[col], 4, labels=["Q1 (menor)", "Q2", "Q3", "Q4 (maior)"])
    g = c.groupby("q", observed=True)["won"].agg(n="size", k="sum").reset_index()
    g[["rate", "ci_lo", "ci_hi"]] = pd.DataFrame([wilson(k, n) for k, n in zip(g["k"], g["n"])])
    top = c.loc[c["q"] == "Q4 (maior)", "won"].to_numpy()
    bot = c.loc[c["q"] == "Q1 (menor)", "won"].to_numpy()
    rng = np.random.default_rng(3)
    diffs = [rng.choice(top, len(top)).mean() - rng.choice(bot, len(bot)).mean() for _ in range(2000)]
    rho = spearman(c[col].to_numpy(), c["won"].to_numpy())
    for _, r in g.iterrows():
        h10_rows.append({"variável": col, "quartil": r["q"], "n": int(r["n"]), "win_rate": r["rate"], "ci_lo": r["ci_lo"], "ci_hi": r["ci_hi"]})
    h10_rows.append({"variável": col, "quartil": "Q4 − Q1 (pp, IC bootstrap)", "n": len(c), "win_rate": 100 * (top.mean() - bot.mean()), "ci_lo": 100 * np.percentile(diffs, 2.5), "ci_hi": 100 * np.percentile(diffs, 97.5)})
    h10_rows.append({"variável": col, "quartil": "Spearman(var, won)", "n": len(c), "win_rate": rho, "ci_lo": np.nan, "ci_hi": np.nan})
h10 = pd.DataFrame(h10_rows)
print("\nH10 account size\n", h10.to_string(index=False))
sections.append(("H10 · Tamanho da conta", md_table(h10)))

# per-group reference tables
sections.append(("Referência · win rate por agente", md_table(agent_t)))
sections.append(("Referência · win rate por setor", md_table(sector_t)))

out = write_md("01_eda.md", sections)
print(f"\nwrote {out}")
