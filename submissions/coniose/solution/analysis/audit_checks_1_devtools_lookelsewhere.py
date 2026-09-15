"""
Auditoria adversarial do report_data.json — testes de robustez.
Roda com: python analysis/audit_checks.py
Não escreve nada; só imprime.
"""
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sstats

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
rng = np.random.default_rng(20260914)

acc = pd.read_csv(DATA / "ravenstack_accounts.csv", parse_dates=["signup_date"])
subs = pd.read_csv(DATA / "ravenstack_subscriptions.csv", parse_dates=["start_date", "end_date"])
usage = pd.read_csv(DATA / "ravenstack_feature_usage.csv", parse_dates=["usage_date"])
tickets = pd.read_csv(DATA / "ravenstack_support_tickets.csv", parse_dates=["submitted_at"])
churn = pd.read_csv(DATA / "ravenstack_churn_events.csv", parse_dates=["churn_date"])

H = lambda t: print("\n" + "=" * 78 + "\n" + t + "\n" + "=" * 78)

# ---------------------------------------------------------------- 1. qualidade
H("1. CONTAMINACAO DE churn_events vs churn_flag")
flag = acc.set_index("account_id")["churn_flag"]
ev_acc = churn["account_id"].nunique()
churn["flag"] = churn["account_id"].map(flag)
print(f"contas totais                              : {len(acc)}")
print(f"churn_flag = True                          : {int(flag.sum())}")
print(f"contas com >=1 evento em churn_events      : {ev_acc}")
print(f"  ...destas, churn_flag=True               : {int(churn.groupby('account_id')['flag'].first().sum())}")
print(f"  ...destas, churn_flag=False (CONTAMINACAO): {int((~churn.groupby('account_id')['flag'].first()).sum())}")
print(f"eventos totais                             : {len(churn)}")
print(f"  eventos de contas churn_flag=True        : {int(churn['flag'].sum())} ({100*churn['flag'].mean():.1f}%)")
print(f"  eventos de contas churn_flag=False       : {int((~churn['flag']).sum())} ({100*(~churn['flag']).mean():.1f}%)")
print("\n-> reason_codes / reason_by_plan / reason_code_devtools_vs_rest usam TODOS os 600 eventos.")
print("   Distribuicao de reason_code, eventos de churnados vs nao-churnados:")
ct = pd.crosstab(churn["reason_code"].fillna("unknown"), churn["flag"], normalize="columns") * 100
chi2, p, dof, _ = sstats.chi2_contingency(pd.crosstab(churn["reason_code"].fillna("unknown"), churn["flag"]))
print(ct.round(1).to_string())
print(f"   chi2 reason_code x (conta realmente churnada): chi2={chi2:.2f} p={p:.4f} dof={dof}")

# reason_by_plan sem contaminacao
H("1b. reason_by_plan — tem estrutura?")
m = churn.merge(acc[["account_id", "plan_tier"]], on="account_id", how="left")
ct2 = pd.crosstab(m["plan_tier"], m["reason_code"].fillna("unknown"))
chi2, p, dof, _ = sstats.chi2_contingency(ct2)
print(f"todos 600 eventos : chi2={chi2:.2f} p={p:.4f} dof={dof}")
mc = m[m["account_id"].map(flag)]
ct3 = pd.crosstab(mc["plan_tier"], mc["reason_code"].fillna("unknown"))
chi2, p, dof, _ = sstats.chi2_contingency(ct3)
print(f"so contas churnadas (n={len(mc)}): chi2={chi2:.2f} p={p:.4f} dof={dof}")

# ------------------------------------------------- 2. look-elsewhere DevTools
H("2. DEVTOOLS — look-elsewhere / selecao pos-hoc")


def chi2_bin(mask, y):
    ct = pd.crosstab(mask, y)
    if ct.shape != (2, 2):
        return 0.0, 1.0
    c, p, _, _ = sstats.chi2_contingency(ct, correction=True)
    return c, p


y = acc["churn_flag"].values
inds = sorted(acc["industry"].unique())
print("todas as 5 comparacoes um-contra-o-resto que PODERIAM ter sido escolhidas:")
obs = []
for i in inds:
    c, p = chi2_bin(acc["industry"].eq(i), acc["churn_flag"])
    r_in = acc.loc[acc.industry == i, "churn_flag"].mean() * 100
    r_out = acc.loc[acc.industry != i, "churn_flag"].mean() * 100
    obs.append(c)
    print(f"  {i:14s} churn {r_in:5.1f}% vs {r_out:5.1f}%   chi2={c:5.2f}  p_bruto={p:.4f}"
          f"  p_Bonferroni(5)={min(1, p*5):.4f}")
chi2_max = max(obs)

# permutacao: distribuicao nula de max(chi2) sobre as 5 comparacoes
n_perm = 20000
null_max = np.empty(n_perm)
ind_codes = pd.Categorical(acc["industry"]).codes
for k in range(n_perm):
    yp = rng.permutation(y)
    best = 0.0
    for ci in range(5):
        mask = ind_codes == ci
        a = np.sum(mask & yp); b = np.sum(mask & ~yp)
        c_ = np.sum(~mask & yp); d = np.sum(~mask & ~yp)
        n = a + b + c_ + d
        num = n * (abs(a * d - b * c_) - n / 2) ** 2
        den = (a + b) * (c_ + d) * (a + c_) * (b + d)
        st = num / den if den else 0.0
        best = max(best, st)
    null_max[k] = best
p_look = (np.sum(null_max >= chi2_max) + 1) / (n_perm + 1)
print(f"\nchi2 observado do MAIOR corte (DevTools)         : {chi2_max:.2f}")
print(f"p 'ingenuo' (como se o corte fosse pre-registrado): 0.0128")
print(f"p corrigido por look-elsewhere (permutacao, {n_perm}): {p_look:.4f}")
print(f"p Bonferroni sobre as 5 escolhas possiveis       : {min(1, 0.0128*5):.4f}")
print(f"qui-quadrado omnibus de 5 categorias (o teste correto): p=0.0657")

# ------------------------------------- 3. DevTools e confundimento com canal
H("3. DEVTOOLS — confundido com canal de aquisicao / plano / pais / trial?")
for col in ["referral_source", "plan_tier", "country", "is_trial"]:
    ct = pd.crosstab(acc["industry"].eq("DevTools"), acc[col], normalize="index") * 100
    c, p, _, _ = sstats.chi2_contingency(pd.crosstab(acc["industry"].eq("DevTools"), acc[col]))
    print(f"\nDevTools x {col}: chi2={c:.2f} p={p:.4f}")
    print(ct.round(1).to_string())

print("\n-- DevTools vs resto ESTRATIFICADO por canal (Mantel-Haenszel) --")


def mantel_haenszel(df, exposure, outcome, strata):
    num = den = 0.0
    rows = []
    for s, g in df.groupby(strata):
        a = int(((g[exposure]) & (g[outcome])).sum())
        b = int(((g[exposure]) & (~g[outcome])).sum())
        c = int(((~g[exposure]) & (g[outcome])).sum())
        d = int(((~g[exposure]) & (~g[outcome])).sum())
        n = a + b + c + d
        if n == 0 or (a + b) == 0 or (c + d) == 0:
            continue
        num += a * d / n
        den += b * c / n
        orat = (a * d) / (b * c) if b * c else np.nan
        rows.append((s, a + b, c + d, 100 * a / (a + b), 100 * c / (c + d), orat))
    return num / den if den else np.nan, rows


acc["is_dev"] = acc["industry"].eq("DevTools")
for strata in ["referral_source", "plan_tier", "country"]:
    mh, rows = mantel_haenszel(acc, "is_dev", "churn_flag", strata)
    print(f"\n  estrato = {strata}: OR de Mantel-Haenszel = {mh:.2f}")
    for s, n1, n0, r1, r0, orat in rows:
        print(f"    {str(s):14s} DevTools n={n1:3d} churn {r1:5.1f}% | resto n={n0:3d} churn {r0:5.1f}%  OR={orat:.2f}")
crude_or = (acc.loc[acc.is_dev, "churn_flag"].mean() / (1 - acc.loc[acc.is_dev, "churn_flag"].mean())) / (
    acc.loc[~acc.is_dev, "churn_flag"].mean() / (1 - acc.loc[~acc.is_dev, "churn_flag"].mean()))
print(f"\n  OR bruto (sem estratificar) = {crude_or:.2f}")

# ------------------------------------------------------------ 4. tenure
H("4. TENURE (signup_date) — a variavel que NUNCA foi usada")
asof = max(usage["usage_date"].max(), pd.Timestamp("2024-12-31"))
last_churn = churn.sort_values("churn_date").groupby("account_id")["churn_date"].last()
acc["churn_date"] = acc["account_id"].map(last_churn)
acc["tenure_days"] = (acc["churn_date"].fillna(asof) - acc["signup_date"]).dt.days
acc["tenure_obs_days"] = (asof - acc["signup_date"]).dt.days
print(f"signup_date vai de {acc.signup_date.min().date()} a {acc.signup_date.max().date()}")
print(f"tenure observavel (asof {asof.date()} - signup), dias: "
      f"mediana={acc.tenure_obs_days.median():.0f} min={acc.tenure_obs_days.min()} max={acc.tenure_obs_days.max()}")
print("\nchurn por quartil de tenure observavel:")
acc["ten_q"] = pd.qcut(acc["tenure_obs_days"], 4, labels=["Q1 mais nova", "Q2", "Q3", "Q4 mais velha"])
g = acc.groupby("ten_q").agg(n=("account_id", "count"), churn=("churn_flag", "mean"),
                             mrr_med=("seats", "median"))
g["churn"] = (g["churn"] * 100).round(1)
print(g.to_string())
c, p, dof, _ = sstats.chi2_contingency(pd.crosstab(acc["ten_q"], acc["churn_flag"]))
print(f"chi2 tenure_quartil x churn: chi2={c:.2f} p={p:.4f} dof={dof}")
r, pr = sstats.pointbiserialr(acc["churn_flag"].astype(int), acc["tenure_obs_days"])
print(f"corr(tenure_obs, churn) r={r:.3f} p={pr:.4f}")
print("\nRISCO DE EXPOSICAO: taxa de churn por dia de exposicao")
print(f"  churn por 100 contas-ano = {100*acc.churn_flag.sum()/ (acc.tenure_obs_days.sum()/365):.2f}")

# --------------------------------------------- 5. MRR concentracao / tamanho
H("5. CONCENTRACAO DE MRR — 'as contas grandes sao mais fieis'")
subs_sorted = subs.sort_values("start_date")
mrr = subs_sorted.groupby("account_id")["mrr_amount"].last()
acc["mrr"] = acc["account_id"].map(mrr).fillna(0)
acc = acc.sort_values("mrr", ascending=False).reset_index(drop=True)
acc["top10"] = acc.index < 50
t10 = acc.loc[acc.top10, "churn_flag"]
rest = acc.loc[~acc.top10, "churn_flag"]
ct = pd.crosstab(acc["top10"], acc["churn_flag"])
c, p, _, _ = sstats.chi2_contingency(ct, correction=True)
odds, pf = sstats.fisher_exact(ct.values)
lo, hi = sstats.binomtest(int(t10.sum()), len(t10)).proportion_ci(0.95)
print(f"top 10% (n=50): churn {100*t10.mean():.1f}%  IC95% [{100*lo:.1f}%, {100*hi:.1f}%]")
print(f"resto  (n=450): churn {100*rest.mean():.1f}%")
print(f"chi2={c:.2f} p={p:.4f} | Fisher p={pf:.4f} | OR={odds:.2f}")
print(f"diferenca observada: {100*(rest.mean()-t10.mean()):.1f} p.p. — dentro do IC do acaso? {lo < rest.mean() < hi}")
print("\nmonotonicidade por decil de MRR (se fosse efeito de tamanho, deveria ser monotono):")
acc["mrr_dec"] = pd.qcut(acc["mrr"].rank(method="first"), 10, labels=False) + 1
gd = acc.groupby("mrr_dec").agg(n=("account_id", "count"), churn=("churn_flag", "mean"),
                                mrr_med=("mrr", "median"))
gd["churn"] = (gd["churn"] * 100).round(1)
print(gd.to_string())
r, pr = sstats.pointbiserialr(acc["churn_flag"].astype(int), acc["mrr"])
print(f"corr(mrr, churn) r={r:.4f} p={pr:.4f}  (Spearman: "
      f"{sstats.spearmanr(acc['churn_flag'].astype(int), acc['mrr']).statistic:.4f})")
print("\ncomposicao de industria do top 10% (candidato a confundidor):")
print((acc.loc[acc.top10, "industry"].value_counts(normalize=True) * 100).round(1).to_string())
print((acc.loc[~acc.top10, "industry"].value_counts(normalize=True) * 100).round(1).to_string())
mh, rows = mantel_haenszel(acc, "top10", "churn_flag", "industry")
print(f"\nOR top10 vs resto, ajustado por industria (MH) = {mh:.2f}")
for s, n1, n0, r1, r0, orat in rows:
    print(f"  {s:14s} top10 n={n1:2d} churn {r1:5.1f}% | resto n={n0:3d} churn {r0:5.1f}%")
print("\nCAUSALIDADE REVERSA: mrr usado e o da ULTIMA assinatura.")
print("  Para conta churnada, a 'ultima' e a que terminou no churn. Comparacao de niveis medida em tempos diferentes.")
print(f"  n de assinaturas por conta: mediana={subs.groupby('account_id').size().median():.0f}")
print(f"  corr(tenure_obs, mrr) r={sstats.pearsonr(acc.tenure_obs_days, acc.mrr).statistic:.3f}")
