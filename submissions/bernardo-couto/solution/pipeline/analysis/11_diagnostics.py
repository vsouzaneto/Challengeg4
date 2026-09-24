"""Follow-up diagnostics after 10_backtest.py showed no p_win candidate beats random.

1. Simplified rules (p_win = product base rate only; agent/agent-product informative) vs default,
   on priority_score metrics + Spearman(score, price) at the snapshot (invariant < 0.9).
2. Quarter-end timing: among deals open at T with realised outcome, win rate by whether they closed
   in a quarter-end month (diagnostic only; close month is not a feature).
3. "Newest first" decomposition: AUC-ROC among live deals (<= 138 d) vs the zombie effect.

Run: cd solution/pipeline && uv run python analysis/11_diagnostics.py
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from _common import (
    BACKTEST_CUTS,
    SNAPSHOT_DATE,
    ZOMBIE_DAYS,
    auc_pr,
    auc_roc,
    bootstrap_paired,
    brier,
    compute_history,
    load_clean,
    md_table,
    open_at,
    precision_at_k,
    revenue_captured_top,
    spearman,
    wilson,
    write_md,
)
from rules import Weights, score_rules

df = load_clean()
closed_all = df[df["is_closed"]]
sections: list[tuple[str, str]] = []

SIMPLE = Weights(agent=0.0, agent_product=0.0, survival=0.0, sector=0.0)
VARIANTS = {"padrão (agente + agente×produto + sobrevivência)": Weights(), "simplificado (p_win = taxa-base do produto; zumbi penalizado)": SIMPLE, "simplificado + w_p reduzido (25/50/25)": Weights(agent=0, agent_product=0, survival=0, w_p=25, w_v=50, w_u=25)}


def frame(T):
    hist = compute_history(closed_all, T)
    ch = closed_all[closed_all["close_date"] <= T]  # leakage-ok: history gate
    o = open_at(df, T)
    o = o.merge(o.groupby("sales_agent").size().rename("open_load"), left_on="sales_agent", right_index=True, how="left")
    return o, hist, ch


# 1. simplified variants
rows = []
for name, w in VARIANTS.items():
    for T in BACKTEST_CUTS:
        o, hist, ch = frame(T)
        sc = score_rules(o, hist, ch, w)
        lab = o["label"].notna().to_numpy()
        y = o.loc[lab, "label"].to_numpy()
        v = o.loc[lab, "realized_value"].to_numpy()
        p = sc.loc[lab, "p_win"].to_numpy()
        s = sc.loc[lab, "priority_score"].to_numpy()
        rc, lo, hi = bootstrap_paired(v, s, revenue_captured_top)
        rows.append({"variante": name, "T": T.date(), "AUC-PR p_win": auc_pr(y, p), "Brier p_win": brier(y, p), "AUC-ROC score": auc_roc(y, s), "receita top20% (score)": rc, "IC95": f"[{lo:.3f}, {hi:.3f}]", "Spearman(score,preço)": spearman(s, o.loc[lab, "sales_price"].to_numpy())})
    # snapshot spearman
    hist = compute_history(closed_all, SNAPSHOT_DATE)
    osn = df[df["deal_stage"].isin(["Engaging", "Prospecting"])].copy()
    osn["days_in_engaging"] = (SNAPSHOT_DATE - osn["engage_date"]).dt.days
    osn = osn.merge(osn.groupby("sales_agent").size().rename("open_load"), left_on="sales_agent", right_index=True, how="left")
    sc = score_rules(osn, hist, closed_all, w)
    rows.append({"variante": name, "T": "snapshot", "AUC-PR p_win": np.nan, "Brier p_win": np.nan, "AUC-ROC score": np.nan, "receita top20% (score)": np.nan, "IC95": "", "Spearman(score,preço)": spearman(sc["priority_score"].to_numpy(), sc["sales_price"].to_numpy())})
t1 = pd.DataFrame(rows)
print(t1.to_string(index=False))
sections.append(("Regras padrão vs simplificadas", md_table(t1)))

# 2. quarter-end timing (diagnostic)
qe_rows = []
for T in list(pd.date_range("2017-04-30", "2017-10-31", freq="ME")):
    o = open_at(df, T)
    lab = o[o["label"].notna()]
    cm = lab["close_date"].dt.month  # leakage-ok: diagnostic of outcome timing, never a feature
    is_qe = cm.isin([3, 6, 9, 12])
    p_qe = wilson(lab.loc[is_qe, "label"].sum(), is_qe.sum())
    p_n = wilson(lab.loc[~is_qe, "label"].sum(), (~is_qe).sum())
    qe_rows.append({"T": T.date(), "n": len(lab), "fecham em mês de fim de trimestre (%)": 100 * is_qe.mean(), "win rate se fecha em fim de tri": p_qe[0], "IC": f"[{p_qe[1]:.2f}, {p_qe[2]:.2f}]", "win rate se fecha em outro mês": p_n[0], "IC ": f"[{p_n[1]:.2f}, {p_n[2]:.2f}]"})
t2 = pd.DataFrame(qe_rows)
print("\n", t2.to_string(index=False))
won_qe = closed_all.loc[closed_all["won"] == 1, "close_date"].dt.month.isin([3, 6, 9, 12]).mean()
lost_qe = closed_all.loc[closed_all["won"] == 0, "close_date"].dt.month.isin([3, 6, 9, 12]).mean()
print(f"share closing in QE month: won={won_qe:.3f} lost={lost_qe:.3f}")
sections.append(("Efeito fim de trimestre (diagnóstico; mês de fechamento não é feature)", md_table(t2) + f"\n\nEntre todos os fechados: {won_qe:.1%} dos Won e {lost_qe:.1%} dos Lost fecham em mês de fim de trimestre."))

# 3. newest-first decomposition
rows3 = []
for T in BACKTEST_CUTS:
    o = open_at(df, T)
    live = o[o["days_in_engaging"] <= ZOMBIE_DAYS]
    zomb = o[o["days_in_engaging"] > ZOMBIE_DAYS]
    lab_live = live[live["label"].notna()]
    rows3.append(
        {
            "T": T.date(),
            "abertos": len(o),
            "vivos (≤138 d)": len(live),
            "zumbis (>138 d)": len(zomb),
            "zumbis com desfecho depois": int(zomb["label"].notna().sum()),
            "vivos censurados (%)": 100 * live["label"].isna().mean(),
            "AUC-ROC 'mais novo' entre vivos com desfecho": auc_roc(lab_live["label"].to_numpy(), -lab_live["days_in_engaging"].to_numpy(dtype=float)),
            "AUC-ROC 'mais novo' entre vivos, censurado=Lost": auc_roc(live["label"].fillna(0).to_numpy(), -live["days_in_engaging"].to_numpy(dtype=float)),
        }
    )
t3 = pd.DataFrame(rows3)
print("\n", t3.to_string(index=False))
sections.append(("Decomposição do baseline 'mais novo primeiro'", md_table(t3)))

out = write_md("11_diagnostics.md", sections)
print(f"\nwrote {out}")

# 4. weight grid for the simplified rules: find weights that keep Spearman(score, price) < 0.9
#    on the backtest frames without injecting the (noise) p_win adjustments.
grid_rows = []
for wp, wv, wu in [(45, 35, 20), (30, 40, 30), (25, 35, 40), (20, 30, 50), (30, 30, 40)]:
    w = Weights(agent=0, agent_product=0, survival=0, w_p=wp, w_v=wv, w_u=wu)
    row = {"w_p/w_v/w_u": f"{wp}/{wv}/{wu}"}
    for T in BACKTEST_CUTS:
        o, hist, ch = frame(T)
        sc = score_rules(o, hist, ch, w)
        lab = o["label"].notna().to_numpy()
        s = sc.loc[lab, "priority_score"].to_numpy()
        row[f"Spearman {T.date()}"] = spearman(s, o.loc[lab, "sales_price"].to_numpy())
        row[f"receita top20% {T.date()}"] = revenue_captured_top(o.loc[lab, "realized_value"].to_numpy(), s)
        row[f"P@10 agente {T.date()}"] = np.mean([precision_at_k(g["label"].to_numpy(), g["_s"].to_numpy(), 10) for _, g in o[lab].assign(_s=s).groupby("sales_agent") if len(g) >= 10])
    sc = score_rules(osn, compute_history(closed_all, SNAPSHOT_DATE), closed_all, w)
    row["Spearman snapshot"] = spearman(sc["priority_score"].to_numpy(), sc["sales_price"].to_numpy())
    row["tier A snapshot"] = int((sc["priority_score"] >= 75).sum())
    grid_rows.append(row)
t4 = pd.DataFrame(grid_rows)
print("\n", t4.to_string(index=False))
sections.append(("Grade de pesos (regras simplificadas)", md_table(t4)))
write_md("11_diagnostics.md", sections)

# 5. zombie queue at the snapshot: nominal value at risk, by manager, and the ordering inside the queue.
hist_s = compute_history(closed_all, SNAPSHOT_DATE)
scz = score_rules(osn, hist_s, closed_all, Weights())
z = scz[scz["is_zombie"]].copy()
live = scz[(~scz["is_zombie"]) & (scz["deal_stage"] == "Engaging")]
q_rows = [{"fila": "zumbis (> 138 d)", "n": len(z), "valor nominal (preço × razão)": z["ev_gross"].sum(), "valor esperado (× p_win)": z["expected_value"].sum(), "idade mediana": z["days_in_engaging"].median(), "com conta (%)": 100 * z["account"].notna().mean()},
          {"fila": "Engaging vivos (≤ 138 d)", "n": len(live), "valor nominal (preço × razão)": live["ev_gross"].sum(), "valor esperado (× p_win)": live["expected_value"].sum(), "idade mediana": live["days_in_engaging"].median(), "com conta (%)": 100 * live["account"].notna().mean()}]
t5 = pd.DataFrame(q_rows)
by_mgr = z.groupby("manager").agg(n=("ev_gross", "size"), valor_nominal=("ev_gross", "sum"), idade_mediana=("days_in_engaging", "median")).reset_index().sort_values("valor_nominal", ascending=False)
by_month = z.groupby(z["engage_date"].dt.to_period("M").astype(str)).size().rename("n").reset_index().rename(columns={"engage_date": "engage_month"})
print("\n", t5.to_string(index=False)); print(by_mgr.to_string(index=False)); print(by_month.to_string(index=False))
# ordering inside the queue: score is value-driven (urgency constant 0.2); check monotonicity with value and age
print("spearman(score, ev_gross) zombies:", spearman(z["priority_score"].to_numpy(), z["ev_gross"].to_numpy()), " spearman(score, age):", spearman(z["priority_score"].to_numpy(), z["days_in_engaging"].to_numpy()))
sections.append(("Fila de zumbis no snapshot (valor nominal em risco)", md_table(t5, "{:.0f}") + "\n\nPor manager:\n\n" + md_table(by_mgr, "{:.0f}") + "\n\nPor mês de engajamento:\n\n" + md_table(by_month) + f"\n\nDentro da fila o score ordena por valor (Spearman(score, valor nominal) = {spearman(z['priority_score'].to_numpy(), z['ev_gross'].to_numpy()):.3f}); a idade não entra (Spearman(score, idade) = {spearman(z['priority_score'].to_numpy(), z['days_in_engaging'].to_numpy()):.3f}). Proposta: desempate por idade crescente (zumbi mais novo primeiro), porque é o mais provável de ainda existir."))
write_md("11_diagnostics.md", sections)
