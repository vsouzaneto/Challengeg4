"""Auditoria parte 4 — poder/MDE e pseudo-replicacao da serie mensal."""
import warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats as sstats
warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]; DATA = ROOT / "data"
acc = pd.read_csv(DATA/"ravenstack_accounts.csv", parse_dates=["signup_date"])
subs = pd.read_csv(DATA/"ravenstack_subscriptions.csv")
usage = pd.read_csv(DATA/"ravenstack_feature_usage.csv", parse_dates=["usage_date"])
H = lambda t: print("\n"+"="*78+"\n"+t+"\n"+"="*78)
rng = np.random.default_rng(11)

H("16. PODER — o que este estudo CONSEGUIRIA ter detectado?")
def power_2prop(p1, p2, n1, n2, alpha=0.05):
    p = (p1*n1+p2*n2)/(n1+n2)
    se0 = np.sqrt(p*(1-p)*(1/n1+1/n2)); se1 = np.sqrt(p1*(1-p1)/n1+p2*(1-p2)/n2)
    z = sstats.norm.ppf(1-alpha/2)
    return sstats.norm.sf((z*se0-abs(p1-p2))/se1)
print("segmento de ~100 contas vs ~400 (o formato de todo corte categorico do relatorio):")
for d in [5,8,10,12,15,20]:
    print(f"  diferenca de {d:2d} p.p. (22,0% vs {22+d:4.1f}%): poder = {power_2prop(0.22,0.22+d/100,100,400):.2f}")
lo,hi=0,50
for _ in range(60):
    mid=(lo+hi)/2
    if power_2prop(0.22,0.22+mid/100,100,400)<0.80: lo=mid
    else: hi=mid
print(f"  -> MDE a 80% de poder: {hi:.1f} p.p.  (so diferencas MAIORES que isso eram achavel)")
print(f"  DevTools observou {31.0-19.4:.1f} p.p. — logo acima do MDE: por construcao, so um efeito")
print("     grande passaria, e um efeito grande e o que o acaso produz com mais facilidade num extremo.")
print("\ncorrelacao com n=500:")
for r in [0.05,0.09,0.12,0.15]:
    t=r*np.sqrt(498/(1-r**2)); print(f"  r={r:.2f}: p bilateral = {2*sstats.t.sf(abs(t),498):.4f}")
print("  -> MDE de r a 80% poder, n=500: r ~ 0.125. Os |r|<0,09 observados NAO descartam")
print("     efeitos reais de |r| ate ~0,12. 'ruido' e leitura correta; 'nao existe causa' nao seria.")

H("17. GLOBAL NULL sobre as 10 correlacoes de correlation_with_churn")
rs = np.array([-0.087,0.064,0.064,0.063,0.036,-0.034,-0.033,-0.02,-0.02,-0.017])
ps = np.array([2*sstats.t.sf(abs(r*np.sqrt(498/(1-r**2))),498) for r in rs])
print("  p correspondentes:", np.round(ps,3))
print(f"  menor p = {ps.min():.3f} | Bonferroni(10) = {min(1,ps.min()*10):.3f}")
print(f"  Fisher combinado: chi2={-2*np.log(ps).sum():.2f}, p={sstats.chi2.sf(-2*np.log(ps).sum(),20):.4f}")
print("  -> nem individualmente nem em conjunto ha sinal. Conclusao do relatorio: correta.")

H("18. PSEUDO-REPLICACAO — o '+0,87 evento/mes' entre churnadas e retidas")
sub2acc = subs.set_index("subscription_id")["account_id"]
u = usage.copy(); u["account_id"]=u["subscription_id"].map(sub2acc)
u["churned"]=u["account_id"].map(acc.set_index("account_id")["churn_flag"])
u["month"]=u["usage_date"].dt.to_period("M")
mon=u.groupby(["month","churned"]).agg(tot=("usage_count","sum"),n=("account_id","nunique")).reset_index()
mon["upa"]=mon.tot/mon.n
sc=mon[mon.churned].sort_values("month").upa.values; sr=mon[~mon.churned].sort_values("month").upa.values
d=sc-sr
print(f"teste do relatorio implicito (24 meses como 24 observacoes): media={d.mean():+.3f} p={sstats.ttest_1samp(d,0).pvalue:.4f}")
print("  -> mas os 24 meses nao sao 24 amostras independentes: sao as MESMAS 500 contas remedidas.")
tot=u.groupby("account_id")["usage_count"].sum(); acc["usage"]=acc.account_id.map(tot).fillna(0)
mean_m=u.groupby(["account_id","month"])["usage_count"].sum().groupby("account_id").mean()
acc["upa_conta"]=acc.account_id.map(mean_m)
a=acc.loc[acc.churn_flag,"upa_conta"].dropna(); b=acc.loc[~acc.churn_flag,"upa_conta"].dropna()
print(f"mesma pergunta no nivel da CONTA (uso medio/mes por conta):")
print(f"  churnadas n={len(a)} media={a.mean():.2f} | retidas n={len(b)} media={b.mean():.2f}")
print(f"  Welch p={sstats.ttest_ind(a,b,equal_var=False).pvalue:.4f} | Mann-Whitney p={sstats.mannwhitneyu(a,b).pvalue:.4f}")
print(f"  Cohen d = {(a.mean()-b.mean())/np.sqrt((a.var()+b.var())/2):+.3f}")
# permutacao no nivel da conta, replicando a estatistica agregada do relatorio
y=acc.set_index("account_id")["churn_flag"]
per=u.groupby(["account_id","month"])["usage_count"].sum().reset_index()
piv=per.pivot(index="account_id",columns="month",values="usage_count")
piv=piv.reindex(acc.account_id)
obs=d.mean()
N=5000; null=np.empty(N); yv=y.values
for k in range(N):
    yp=rng.permutation(yv)
    A=piv[yp]; B=piv[~yp]
    dd=(A.sum(axis=0)/A.notna().sum(axis=0)) - (B.sum(axis=0)/B.notna().sum(axis=0))
    null[k]=dd.mean()
print(f"\npermutacao do rotulo de churn NO NIVEL DA CONTA (a unidade certa), {N} reps:")
print(f"  estatistica observada (+{obs:.3f}) | p = {(np.sum(np.abs(null)>=abs(obs))+1)/(N+1):.4f}")
print("  -> o p=0,003 do teste mensal cai para ~0,15 quando a unidade de aleatorizacao e a conta.")
print("     Era pseudo-replicacao: 24 meses tratados como 24 graus de liberdade.")
