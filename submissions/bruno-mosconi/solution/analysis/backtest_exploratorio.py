import pandas as pd, numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
import os, pathlib
D = os.environ.get("CRM_DATA_DIR", str(pathlib.Path(__file__).resolve().parent.parent / "data"))
P=pd.read_csv(f"{D}/sales_pipeline.csv"); Pr=pd.read_csv(f"{D}/products.csv")
P["product"]=P["product"].replace({"GTXPro":"GTX Pro"}); P=P.merge(Pr,on="product")
P["eng"]=pd.to_datetime(P.engage_date); P["cl"]=pd.to_datetime(P.close_date)
P=P[P.deal_stage!="Prospecting"].copy()
H=90; K=10; MAXC=138
def snapshot(T):
    s=P[(P.eng<=T)&((P.cl.isna())|(P.cl>T))].copy()
    s["age"]=(T-s.eng).dt.days
    s["win_h"]=(s.deal_stage=="Won")&(s.cl<=T+pd.Timedelta(days=H))
    s["rev_h"]=np.where(s.win_h,s.close_value,0.0)
    s["dqe"]=(s.eng.dt.to_period("Q").dt.end_time.dt.normalize()-s.eng).dt.days
    return s
def curve_closed_only(T):  # o método original (enviesado)
    c=P[(P.cl<=T)].copy(); c["cyc"]=(c.cl-c.eng).dt.days; c["w"]=c.deal_stage=="Won"
    base=c.w.mean()
    def f(a):
        r=c[c.cyc>a]; return r.w.mean() if len(r)>=30 else c[c.cyc>c.cyc.quantile(.97)].w.mean()
    return f
def curve_cohort(T):       # corrigido: coorte com 138 dias observados até T; desfecho medido em T
    c=P[P.eng<=T-pd.Timedelta(days=MAXC)].copy()
    c["t"]=np.where(c.cl.notna()&(c.cl<=T),(c.cl-c.eng).dt.days,(T-c.eng).dt.days)
    c["w"]=(c.deal_stage=="Won")&(c.cl<=T)
    def f(a):
        r=c[c.t>a]; return r.w.mean() if len(r)>=30 else 0.0
    return f
def ml_model(T):
    T0=T-pd.Timedelta(days=H); s=snapshot(T0)
    s["y"]=(s.deal_stage=="Won")&(s.cl<=T)   # observável em T
    X=pd.DataFrame({"age":s.age,"price":s.sales_price,"dqe":s.dqe,"prod":s["product"].astype("category"),"agent":s.sales_agent.astype("category")})
    m=HistGradientBoostingClassifier(categorical_features="from_dtype",random_state=0).fit(X,s.y)
    return m, X.dtypes
def score(s,T,method,rng):
    if method=="Aleatório": return rng.random(len(s))
    if method=="Só valor": return s.sales_price.values
    if method=="Valor esperado (idade, só fechados) — ORIGINAL":
        f=curve_closed_only(T); return np.array([f(a) for a in s.age])*s.sales_price.values
    if method=="Valor esperado (idade corrigida)":
        f=curve_cohort(T); return np.array([f(a) for a in s.age])*s.sales_price.values
    if method=="Regra: tira parados (>138d) e ordena por valor":
        return np.where(s.age>MAXC,-1e9,0)+s.sales_price.values
    if method=="Regra: faixas de idade (≤90, 91–138, >138) e valor":
        band=np.select([s.age<=90,s.age<=MAXC],[2,1],0); return band*1e6+s.sales_price.values
    if method=="Pontos (valor + idade)":
        pv=np.select([s.sales_price>=5000,s.sales_price>=1000],[50,30],10)
        pa=np.select([s.age<=60,s.age<=104,s.age<=MAXC],[40,25,10],0); return pv+pa+s.sales_price.values/1e6
    if method=="Modelo ML (gradient boosting)":
        m,dt=ml_model(T)
        X=pd.DataFrame({"age":s.age,"price":s.sales_price,"dqe":s.dqe,"prod":pd.Categorical(s["product"],categories=dt["prod"].categories),"agent":pd.Categorical(s.sales_agent,categories=dt["agent"].categories)})
        return m.predict_proba(X)[:,1]*s.sales_price.values
methods=["Aleatório","Só valor","Valor esperado (idade, só fechados) — ORIGINAL","Valor esperado (idade corrigida)","Regra: tira parados (>138d) e ordena por valor","Regra: faixas de idade (≤90, 91–138, >138) e valor","Pontos (valor + idade)","Modelo ML (gradient boosting)"]
snaps=pd.to_datetime(["2017-06-30","2017-07-31","2017-08-31","2017-09-30"])
rows=[]
for T in snaps:
    s=snapshot(T); total=s.rev_h.sum()
    for mth in methods:
        reps=20 if mth=="Aleatório" else 1
        for r in range(reps):
            rng=np.random.default_rng(r); s["sc"]=score(s,T,mth,rng)
            top=s.sort_values("sc",ascending=False).groupby("sales_agent").head(K)
            rows.append(dict(T=T.date(),metodo=mth,rep=r,deals_top=len(top),ganhos_top=int(top.win_h.sum()),receita_top=top.rev_h.sum(),receita_total=total,abertos=len(s),parados_no_top=int((top.age>MAXC).sum())))
R=pd.DataFrame(rows).groupby(["metodo","T"]).mean(numeric_only=True).reset_index()
agg=R.groupby("metodo").agg(receita_top=("receita_top","sum"),receita_total=("receita_total","sum"),ganhos_top=("ganhos_top","sum"),deals_top=("deals_top","sum"),parados_no_top=("parados_no_top","sum")).reset_index()
agg["% da receita capturada pelo top 10"]=(100*agg.receita_top/agg.receita_total).round(1)
agg["% do top 10 ganho em 90d"]=(100*agg.ganhos_top/agg.deals_top).round(1)
agg["% do top 10 parado (>138d)"]=(100*agg.parados_no_top/agg.deals_top).round(1)
agg["receita_top (US$ mil)"]=(agg.receita_top/1000).round(0)
print("Snapshots:",[str(t.date()) for t in snaps],"| horizonte",H,"dias | top",K,"por vendedor | Prospecting fora (sem datas)")
for T in snaps:
    s=snapshot(T); print(f"  {T.date()}: {len(s)} abertos (Engaging), {int((s.age>MAXC).sum())} com >138d, receita ganha nos 90d seguintes US$ {s.rev_h.sum()/1e3:.0f} mil")
print(agg.sort_values("% da receita capturada pelo top 10",ascending=False)[["metodo","% da receita capturada pelo top 10","receita_top (US$ mil)","% do top 10 ganho em 90d","% do top 10 parado (>138d)"]].to_markdown(index=False))
print("\nPor snapshot (% receita capturada):")
R["pct"]=(100*R.receita_top/R.receita_total).round(1); print(R.pivot(index="metodo",columns="T",values="pct").to_markdown())
