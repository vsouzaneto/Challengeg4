"""Auditoria adversarial parte 2 — tendencia de uso, tickets, multiplicidade, modelo conjunto."""
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sstats

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
rng = np.random.default_rng(7)

acc = pd.read_csv(DATA / "ravenstack_accounts.csv", parse_dates=["signup_date"])
subs = pd.read_csv(DATA / "ravenstack_subscriptions.csv", parse_dates=["start_date", "end_date"])
usage = pd.read_csv(DATA / "ravenstack_feature_usage.csv", parse_dates=["usage_date"])
tickets = pd.read_csv(DATA / "ravenstack_support_tickets.csv", parse_dates=["submitted_at"])
churn = pd.read_csv(DATA / "ravenstack_churn_events.csv", parse_dates=["churn_date"])
H = lambda t: print("\n" + "=" * 78 + "\n" + t + "\n" + "=" * 78)

flag = acc.set_index("account_id")["churn_flag"]
sub2acc = subs.set_index("subscription_id")["account_id"]
u = usage.copy()
u["account_id"] = u["subscription_id"].map(sub2acc)
u["churned"] = u["account_id"].map(flag)
u = u.merge(acc[["account_id", "signup_date"]], on="account_id", how="left")
last_churn = churn.sort_values("churn_date").groupby("account_id")["churn_date"].last()
u["churn_date"] = u["account_id"].map(last_churn)

# --------------------------------------------------- 6. integridade temporal
H("6. INTEGRIDADE TEMPORAL DA TABELA DE USO (base da 'trajetoria')")
print(f"usage_date  : {u.usage_date.min().date()} .. {u.usage_date.max().date()}")
print(f"signup_date : {acc.signup_date.min().date()} .. {acc.signup_date.max().date()} (mediana {acc.signup_date.median().date()})")
pre = (u["usage_date"] < u["signup_date"]).mean() * 100
print(f"\n>>> linhas de uso ANTERIORES ao signup_date da propria conta: {pre:.1f}% ({int((u.usage_date<u.signup_date).sum())} de {len(u)})")
sd = subs.set_index("subscription_id")
u["sub_start"] = u["subscription_id"].map(sd["start_date"])
u["sub_end"] = u["subscription_id"].map(sd["end_date"])
print(f">>> linhas de uso fora da janela da propria assinatura (antes do start): "
      f"{(u.usage_date < u.sub_start).mean()*100:.1f}%")
print(f">>> linhas de uso depois do end_date da assinatura: "
      f"{(u.usage_date > u.sub_end).mean()*100:.1f}% (das que tem end_date)")
cu = u[u["churned"] & u["churn_date"].notna()]
print(f"\n>>> linhas de uso de contas churnadas POSTERIORES ao churn_date: "
      f"{(cu.usage_date > cu.churn_date).mean()*100:.1f}% ({int((cu.usage_date>cu.churn_date).sum())} linhas)")
print("    (o dashboard afirma: 'medido enquanto ainda estavam ativas')")
mact = u[u.churned].groupby(u.usage_date.dt.to_period("M"))["account_id"].nunique()
print(f"\ncontas churnadas 'ativas' por mes: min={mact.min()} max={mact.max()} (de 110 churnadas)")
print("    -> sem truncamento em churn_date: a serie vermelha nao para no cancelamento.")

# ------------------------------------- 7. tendencia de uso: teste de verdade
H("7. 'QUEM CANCELA USA MAIS' — o achado tem teste?")
u["month"] = u["usage_date"].dt.to_period("M")
per = u.groupby(["account_id", "month"])["usage_count"].sum().reset_index()
per["mi"] = per["month"].astype("period[M]").astype(int)


def slope(g):
    if len(g) < 6:
        return np.nan
    return sstats.linregress(g["mi"], g["usage_count"]).slope


sl = per.groupby("account_id").apply(slope).dropna()
sl_df = pd.DataFrame({"slope": sl})
sl_df["churned"] = sl_df.index.map(flag)
a = sl_df.loc[sl_df.churned, "slope"]
b = sl_df.loc[~sl_df.churned, "slope"]
t, p = sstats.ttest_ind(a, b, equal_var=False)
mw = sstats.mannwhitneyu(a, b)
print("slope de uso mensal POR CONTA (a mesma pergunta, no nivel certo):")
print(f"  churnadas n={len(a):3d} slope medio={a.mean():+.4f} (dp {a.std():.3f})")
print(f"  retidas   n={len(b):3d} slope medio={b.mean():+.4f} (dp {b.std():.3f})")
print(f"  Welch t={t:.3f} p={p:.4f} | Mann-Whitney p={mw.pvalue:.4f}")
print(f"  Cohen d = {(a.mean()-b.mean())/np.sqrt((a.var()+b.var())/2):.3f}")

print("\nagora o numero DO RELATORIO (+10,0% vs +1,7%) com incerteza:")
mon = u.groupby(["month", "churned"]).agg(tot=("usage_count", "sum"),
                                          n=("account_id", "nunique")).reset_index()
mon["upa"] = mon["tot"] / mon["n"]
for ch in [True, False]:
    s = mon[mon.churned == ch].sort_values("month")["upa"].values
    fq, lq = s[:3].mean(), s[-3:].mean()
    pooled = np.sqrt(s[:3].var(ddof=1) / 3 + s[-3:].var(ddof=1) / 3)
    tt, pp = sstats.ttest_ind(s[-3:], s[:3], equal_var=False)
    lab = "churnadas" if ch else "retidas  "
    print(f"  {lab}: {fq:.2f} -> {lq:.2f} ({100*(lq-fq)/fq:+.1f}%)  EP da diferenca={pooled:.2f}  "
          f"t={tt:.2f} p={pp:.3f}  (n=3 vs 3 MESES, nao contas)")
sc = mon[mon.churned].sort_values("month")["upa"].values
sr = mon[~mon.churned].sort_values("month")["upa"].values
print(f"  dp mes-a-mes da serie churnada: {sc.std(ddof=1):.2f} — a 'divergencia' de "
      f"{sc[-3:].mean()-sc[:3].mean():.2f} eventos/conta e {(sc[-3:].mean()-sc[:3].mean())/sc.std(ddof=1):.1f} dp.")
d = sc - sr
print(f"  diferenca churnada-retida por mes: media={d.mean():+.2f} dp={d.std(ddof=1):.2f} "
      f"t 1-amostra p={sstats.ttest_1samp(d,0).pvalue:.4f}")
print(f"  tendencia da DIFERENCA ao longo dos 24 meses: slope={sstats.linregress(np.arange(24),d).slope:+.4f} "
      f"p={sstats.linregress(np.arange(24),d).pvalue:.4f}")

print("\nsera artefato de composicao (coorte de signup)? uso medio por conta x quartil de signup:")
acc["ten"] = (pd.Timestamp("2024-12-31") - acc["signup_date"]).dt.days
acc["ten_q"] = pd.qcut(acc["ten"], 4, labels=["Q1 nova", "Q2", "Q3", "Q4 velha"])
tot = u.groupby("account_id")["usage_count"].sum()
acc["tot_usage"] = acc["account_id"].map(tot)
print(acc.groupby("ten_q").agg(n=("account_id", "count"), uso_total=("tot_usage", "mean"),
                               churn=("churn_flag", "mean")).round(2).to_string())
print("-> se uso total nao cresce com tenure, a tabela de uso nao respeita o ciclo de vida da conta.")

# ------------------------------------------- 8. tickets: proxy de VOLUME
H("8. TICKET PRIORITY — 'ter ticket high = menos churn' e efeito de prioridade ou de VOLUME?")
nt = tickets.groupby("account_id").size()
acc["n_tickets"] = acc["account_id"].map(nt).fillna(0)
print("churn por faixa de nº de tickets (o confundidor obvio):")
acc["nt_b"] = pd.cut(acc["n_tickets"], [-1, 2, 3, 4, 5, 99],
                     labels=["0-2", "3", "4", "5", "6+"])
print(acc.groupby("nt_b").agg(n=("account_id", "count"), churn=("churn_flag", "mean")).round(3).to_string())
for pr in ["high", "low", "medium", "urgent"]:
    s = set(tickets.loc[tickets.priority == pr, "account_id"])
    acc[f"has_{pr}"] = acc["account_id"].isin(s)
    print(f"\n{pr}: media de tickets de quem TEM = {acc.loc[acc[f'has_{pr}'],'n_tickets'].mean():.2f} | "
          f"de quem NAO tem = {acc.loc[~acc[f'has_{pr}'],'n_tickets'].mean():.2f}")
    # Mantel-Haenszel estratificado por volume de tickets
    num = den = 0.0
    for s_, g in acc.groupby("nt_b"):
        a_ = ((g[f"has_{pr}"]) & (g.churn_flag)).sum(); b_ = ((g[f"has_{pr}"]) & (~g.churn_flag)).sum()
        c_ = ((~g[f"has_{pr}"]) & (g.churn_flag)).sum(); d_ = ((~g[f"has_{pr}"]) & (~g.churn_flag)).sum()
        n_ = a_ + b_ + c_ + d_
        if n_ and (a_ + b_) and (c_ + d_):
            num += a_ * d_ / n_; den += b_ * c_ / n_
    crude = ((acc.loc[acc[f"has_{pr}"], "churn_flag"].mean() / (1 - acc.loc[acc[f"has_{pr}"], "churn_flag"].mean()))
             / (acc.loc[~acc[f"has_{pr}"], "churn_flag"].mean() / (1 - acc.loc[~acc[f"has_{pr}"], "churn_flag"].mean())))
    print(f"   OR bruto = {crude:.2f} | OR ajustado por volume de tickets (MH) = {num/den if den else float('nan'):.2f}")

# ------------------------------- 9. multiplicidade total do relatorio
H("9. MULTIPLICIDADE — quantos testes o relatorio realmente rodou?")
fam = {"correlacoes de Pearson (correlation_with_churn)": 10,
       "qui-quadrado omnibus de segmento": 5,
       "t-tests por feature (uso)": 40,
       "t-tests por feature (error_rate)": 40,
       "qui-quadrado por prioridade de ticket": 4,
       "qui-quadrado de escalacao": 1,
       "DevTools vs resto (pos-hoc)": 1,
       "Pearson crescimento x churn entre segmentos": 2,
       "comparacoes de concentracao de MRR": 3}
tot = sum(fam.values())
for k, v in fam.items():
    print(f"  {v:3d}  {k}")
print(f"  {tot:3d}  TOTAL de testes formais no build_report_data.py")
print(f"\nesperado de falsos positivos a p<0,05 sob a hipotese nula: {tot*0.05:.1f}")
print(f"P(pelo menos 1 falso positivo) = {1-0.95**tot:.3f}")
print("achados 'significativos' de fato encontrados: 3 features (uso) + 2 features (error_rate) + 1 DevTools = 6")
print("-> 6 observados vs 5,3 esperados por acaso puro. Indistinguivel de ruido.")
print("\nfamilia honesta do 'maior corte um-contra-o-resto' (nao so industria):")
y = acc["churn_flag"].values
cuts = []
for col in ["industry", "country", "referral_source", "plan_tier"]:
    for v in acc[col].dropna().unique():
        cuts.append(acc[col].eq(v).values)
cuts.append(acc["is_trial"].values.astype(bool))
print(f"  nº de cortes binarios um-contra-o-resto disponiveis: {len(cuts)}")


def chi2c(mask, yy):
    a = np.sum(mask & yy); b = np.sum(mask & ~yy); c = np.sum(~mask & yy); d = np.sum(~mask & ~yy)
    n = a + b + c + d
    den = (a + b) * (c + d) * (a + c) * (b + d)
    return (n * (abs(a * d - b * c) - n / 2) ** 2 / den) if den else 0.0


obs_max = max(chi2c(m, y) for m in cuts)
N = 20000
nm = np.empty(N)
for k in range(N):
    yp = rng.permutation(y)
    nm[k] = max(chi2c(m, yp) for m in cuts)
print(f"  chi2 do maior corte observado = {obs_max:.2f} (DevTools)")
print(f"  p corrigido por look-elsewhere sobre TODOS os {len(cuts)} cortes: "
      f"{(np.sum(nm>=obs_max)+1)/(N+1):.4f}")

# ------------------------------------------- 10. modelo conjunto
H("10. EXISTE QUALQUER SINAL? regressao logistica completa + teste de razao de verossimilhanca")
import statsmodels.api as sm

sub2 = subs.sort_values("start_date")
acc["mrr"] = acc["account_id"].map(sub2.groupby("account_id")["mrr_amount"].last()).fillna(0)
acc["usage"] = acc["account_id"].map(tot).fillna(0)
X = pd.get_dummies(acc[["industry", "country", "referral_source", "plan_tier"]], drop_first=True).astype(float)
X["seats"] = acc["seats"]; X["is_trial"] = acc["is_trial"].astype(float)
X["mrr"] = acc["mrr"] / 1000; X["usage"] = acc["usage"] / 100
X["tenure"] = acc["ten"] / 365; X["n_tickets"] = acc["n_tickets"]
X = sm.add_constant(X)
m1 = sm.Logit(acc["churn_flag"].astype(int), X).fit(disp=0)
m0 = sm.Logit(acc["churn_flag"].astype(int), np.ones((len(acc), 1))).fit(disp=0)
lr = 2 * (m1.llf - m0.llf)
dfree = X.shape[1] - 1
print(f"LR chi2 = {lr:.2f} com {dfree} gl -> p = {sstats.chi2.sf(lr, dfree):.4f}")
print(f"pseudo R2 (McFadden) = {1 - m1.llf/m0.llf:.4f}")
print("\ncoeficientes com |z|>1,5:")
for n_, c_, se_, z_, p_ in zip(X.columns, m1.params, m1.bse, m1.tvalues, m1.pvalues):
    if abs(z_) > 1.5:
        print(f"  {n_:28s} OR={np.exp(c_):5.2f}  z={z_:+.2f}  p={p_:.4f}")
print("\n-> Um modelo com TODAS as covariaveis do dataset nao rejeita o modelo nulo.")
print("   Traducao: churn_flag e, dentro do poder desta amostra, independente de tudo que foi medido.")
