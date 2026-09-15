"""Auditoria adversarial parte 3 — modelo conjunto, MRR zerado, suporte, ecologica, small-n."""
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats as sstats
import statsmodels.api as sm

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
acc = pd.read_csv(DATA / "ravenstack_accounts.csv", parse_dates=["signup_date"])
subs = pd.read_csv(DATA / "ravenstack_subscriptions.csv", parse_dates=["start_date", "end_date"])
usage = pd.read_csv(DATA / "ravenstack_feature_usage.csv", parse_dates=["usage_date"])
tickets = pd.read_csv(DATA / "ravenstack_support_tickets.csv", parse_dates=["submitted_at"])
H = lambda t: print("\n" + "=" * 78 + "\n" + t + "\n" + "=" * 78)

sub2acc = subs.set_index("subscription_id")["account_id"]
usage["account_id"] = usage["subscription_id"].map(sub2acc)
usage_tot = usage.groupby("account_id")["usage_count"].sum()
nt = tickets.groupby("account_id").size()
acc["ten"] = (pd.Timestamp("2024-12-31") - acc["signup_date"]).dt.days
acc["mrr"] = acc["account_id"].map(subs.sort_values("start_date").groupby("account_id")["mrr_amount"].last()).fillna(0)
acc["usage"] = acc["account_id"].map(usage_tot).fillna(0)
acc["n_tickets"] = acc["account_id"].map(nt).fillna(0)

H("10. EXISTE QUALQUER SINAL? logistica completa + teste de razao de verossimilhanca")
X = pd.get_dummies(acc[["industry", "country", "referral_source", "plan_tier"]], drop_first=True).astype(float)
X["seats"] = acc["seats"].astype(float); X["is_trial"] = acc["is_trial"].astype(float)
X["mrr_k"] = acc["mrr"] / 1000; X["usage_100"] = acc["usage"] / 100
X["tenure_anos"] = acc["ten"] / 365; X["n_tickets"] = acc["n_tickets"].astype(float)
X = sm.add_constant(X)
y = acc["churn_flag"].astype(int)
m1 = sm.Logit(y, X).fit(disp=0)
m0 = sm.Logit(y, np.ones((len(acc), 1))).fit(disp=0)
lr = 2 * (m1.llf - m0.llf); dfree = X.shape[1] - 1
print(f"modelo COM TUDO ({dfree} covariaveis) vs modelo so com intercepto:")
print(f"  LR chi2 = {lr:.2f}, gl = {dfree}  ->  p = {sstats.chi2.sf(lr, dfree):.4f}")
print(f"  pseudo-R2 McFadden = {1 - m1.llf/m0.llf:.4f}")
print("\ncoeficientes com p<0,10 (os unicos candidatos):")
any_ = False
for n_, c_, z_, p_ in zip(X.columns, m1.params, m1.tvalues, m1.pvalues):
    if p_ < 0.10 and n_ != "const":
        print(f"  {n_:26s} OR={np.exp(c_):5.2f}  z={z_:+.2f}  p={p_:.4f}"
              f"  (Bonferroni {dfree} testes: p={min(1,p_*dfree):.3f})")
        any_ = True
if not any_:
    print("  nenhum.")
print("\n-> o conjunto completo de covariaveis nao rejeita o nulo. Nao ha o que modelar.")

H("11. MRR = 0 — o denominador da 'concentracao'")
print(f"contas com mrr (ultima assinatura) = 0 : {(acc.mrr==0).sum()}")
print(f"contas sem NENHUMA assinatura          : {(~acc.account_id.isin(subs.account_id)).sum()}")
print(f"assinaturas com mrr_amount == 0        : {(subs.mrr_amount==0).sum()} de {len(subs)}")
print(f"  ...destas, is_trial=True             : {subs.loc[subs.mrr_amount==0,'is_trial'].sum()}")
print(f"MRR total (soma da ultima assinatura)  : {acc.mrr.sum():,.0f}")
print(f"MRR se usasse a assinatura ATIVA (end_date nulo):")
ativa = subs[subs.end_date.isna()].sort_values("start_date").groupby("account_id")["mrr_amount"].last()
print(f"  contas com assinatura ativa          : {ativa.notna().sum()} | soma = {ativa.sum():,.0f}")
print(f"  top10% desse MRR = "
      f"{100*ativa.sort_values(ascending=False).head(50).sum()/ativa.sum():.1f}% (relatorio diz 45,5%)")
print("-> 'MRR total' e 'MRR em risco' dependem de qual assinatura das ~10 por conta e escolhida.")
print(f"   mediana de assinaturas por conta: {subs.groupby('account_id').size().median():.0f}; "
      f"{(subs.end_date.isna()).sum()} de {len(subs)} sem end_date.")
print(f"   contas com >1 assinatura SEM end_date (ambiguidade de 'atual'): "
      f"{(subs[subs.end_date.isna()].groupby('account_id').size()>1).sum()}")

H("12. SUPORTE — as diferencas da tabela tem teste? (o dashboard nao roda nenhum)")
t = tickets.copy(); t["churn"] = t["account_id"].map(acc.set_index("account_id")["churn_flag"])
for col, lab in [("satisfaction_score", "satisfacao"), ("resolution_time_hours", "resolucao (h)"),
                 ("first_response_time_minutes", "1a resposta (min)")]:
    a = t.loc[t.churn, col].dropna(); b = t.loc[~t.churn, col].dropna()
    tt, pp = sstats.ttest_ind(a, b, equal_var=False)
    print(f"{lab:20s} churn {a.mean():7.2f} (n={len(a):4d}) vs retido {b.mean():7.2f} (n={len(b):4d})  "
          f"Welch p={pp:.4f}  Mann-Whitney p={sstats.mannwhitneyu(a,b).pvalue:.4f}")
esc = t.groupby("account_id")["escalation_flag"].mean()
acc["pct_esc"] = acc["account_id"].map(esc)
a = acc.loc[acc.churn_flag, "pct_esc"].dropna(); b = acc.loc[~acc.churn_flag, "pct_esc"].dropna()
print(f"{'% escalado (conta)':20s} churn {100*a.mean():7.2f} (n={len(a):4d}) vs retido {100*b.mean():7.2f} (n={len(b):4d})  "
      f"Welch p={sstats.ttest_ind(a,b,equal_var=False).pvalue:.4f}")
print(f"\nNOTA: build_report_data.py faz acc['pct_escalated'].fillna(0) -> as "
      f"{acc.pct_esc.isna().sum()} contas SEM ticket entram como 0% escalado,")
print("      e depois entram na correlacao de Pearson. 'sem ticket' vira 'ticket nunca escalado'.")
print(f"      satisfaction_score ausente em {tickets.satisfaction_score.isna().sum()} de {len(tickets)} tickets "
      f"({100*tickets.satisfaction_score.isna().mean():.0f}%) — media calculada sobre quem respondeu (nao-resposta nao e aleatoria).")

H("13. CORRELACAO ECOLOGICA COM n=5 — qual e o poder real?")
for nome, r in [("industria", -0.533), ("referral", -0.344)]:
    n = 5
    z = np.arctanh(r); se = 1 / np.sqrt(n - 3)
    lo, hi = np.tanh(z - 1.96 * se), np.tanh(z + 1.96 * se)
    print(f"{nome:10s} r={r:+.3f}  IC95% = [{lo:+.3f}, {hi:+.3f}]  -> cobre de "
          f"{'forte negativa' if lo<-0.8 else 'negativa'} a {'forte positiva' if hi>0.8 else 'positiva'}")
print("\npoder: para detectar r=-0,53 a alpha=0,05 com n=5 grupos, o poder e ~13%.")
print("P(|r|>=0,53 por acaso com n=5) = "
      f"{2*sstats.beta.cdf((1-0.533)/2, 1.5, 1.5):.3f}  (~1 em 3)")
print("Alem disso: e correlacao ECOLOGICA (unidade = segmento, nao conta).")
print("No nivel da conta, uso total x churn: r = "
      f"{sstats.pointbiserialr(acc.churn_flag.astype(int), acc.usage).statistic:+.3f} "
      f"(p={sstats.pointbiserialr(acc.churn_flag.astype(int), acc.usage).pvalue:.3f}) — sinal OPOSTO ao ecologico.")

H("14. CORTES DE AMOSTRA PEQUENA EXIBIDOS NO DASHBOARD (min_n=5)")
for col in ["country", "industry", "referral_source"]:
    g = acc.groupby(col).agg(n=("account_id", "count"), k=("churn_flag", "sum"))
    g["rate"] = 100 * g.k / g.n
    g[["lo", "hi"]] = [list(100 * np.array(sstats.binomtest(int(k), int(n)).proportion_ci(0.95)))
                       for k, n in zip(g.k, g.n)]
    g = g.sort_values("rate", ascending=False)
    print(f"\n{col} (ordenado por taxa, como no dashboard):")
    for i, r in g.iterrows():
        marca = "  <-- topo da lista, IC cobre a base de 22,0%" if i == g.index[0] and r.lo < 22 < r.hi else ""
        print(f"  {str(i):14s} n={int(r.n):3d}  churn={r.rate:5.1f}%  IC95%=[{r.lo:5.1f}%, {r.hi:5.1f}%]{marca}")

H("15. feature_level — o padrao-ouro foi aplicado so na metade")
print("build_report_data.py corrige por Bonferroni os 40 t-tests de usage_count.")
print("Mas roda OUTROS 40 t-tests em error_rate e nao corrige, nao conta significativos,")
print("e publica p=0,0037 (feature_20) e p=0,0204 (feature_25) na mesma tabela, sem ressalva.")
u = usage.copy()
u["churn"] = u["account_id"].map(acc.set_index("account_id")["churn_flag"])
pf = u.groupby(["feature_name", "account_id"]).agg(uc=("usage_count", "sum"), ec=("error_count", "sum")).reset_index()
pf["churn"] = pf["account_id"].map(acc.set_index("account_id")["churn_flag"])
pf["er"] = pf.ec / pf.uc.replace(0, np.nan)
ps = []
for f, g in pf.groupby("feature_name"):
    a = g.loc[g.churn, "er"].dropna(); b = g.loc[~g.churn, "er"].dropna()
    if len(a) > 5 and len(b) > 5:
        ps.append(sstats.ttest_ind(a, b, equal_var=False).pvalue)
ps = np.array(ps)
print(f"\n  testes de error_rate rodados     : {len(ps)}")
print(f"  p<0,05 sem correcao              : {(ps<0.05).sum()}  (esperado por acaso: {0.05*len(ps):.1f})")
print(f"  p<Bonferroni (0,05/{len(ps)}={0.05/len(ps):.5f}) : {(ps<0.05/len(ps)).sum()}")
print(f"  menor p = {ps.min():.4f}; menor p esperado sob o nulo com {len(ps)} testes ~ {1/(len(ps)+1):.4f}")
print(f"  teste de uniformidade dos 40 p (KS contra U[0,1]): p={sstats.kstest(ps,'uniform').pvalue:.4f}")
ps_u = []
for f, g in pf.groupby("feature_name"):
    a = g.loc[g.churn, "uc"]; b = g.loc[~g.churn, "uc"]
    if len(a) >= 5 and len(b) >= 5:
        ps_u.append(sstats.ttest_ind(a, b, equal_var=False).pvalue)
print(f"  idem para os 40 p de usage_count: KS p={sstats.kstest(np.array(ps_u),'uniform').pvalue:.4f}")
print("  -> p uniformes = exatamente o que se espera se NAO ha efeito nenhum em lugar nenhum.")
