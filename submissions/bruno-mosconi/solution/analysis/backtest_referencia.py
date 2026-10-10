# Backtest determinístico (desempate por ID; aleatório = esperança exata), referência para o painel.
import pandas as pd, numpy as np
import os, pathlib
D = os.environ.get("CRM_DATA_DIR", str(pathlib.Path(__file__).resolve().parent.parent / "data"))
P=pd.read_csv(f"{D}/sales_pipeline.csv"); Pr=pd.read_csv(f"{D}/products.csv")
P["product"]=P["product"].replace({"GTXPro":"GTX Pro"}); P=P.merge(Pr,on="product")
P["eng"]=pd.to_datetime(P.engage_date); P["cl"]=pd.to_datetime(P.close_date)
P=P[P.deal_stage!="Prospecting"].copy()
H,K,MAXC=90,10,138; BANDS=[0,30,60,90,104,120]
def snap(T):
    s=P[(P.eng<=T)&((P.cl.isna())|(P.cl>T))].copy(); s["age"]=(T-s.eng).dt.days
    s["rev"]=np.where((s.deal_stage=="Won")&(s.cl<=T+pd.Timedelta(days=H)),s.close_value,0.0); return s
def bands(T):
    c=P[P.eng<=T-pd.Timedelta(days=MAXC)].copy()
    c["t"]=np.where(c.cl.notna()&(c.cl<=T),(c.cl-c.eng).dt.days,(T-c.eng).dt.days); c["w"]=(c.deal_stage=="Won")&(c.cl<=T)
    tab={b:c[c.t>b].w.mean() for b in BANDS}
    return lambda a: 0.0 if a>MAXC else tab[max(b for b in BANDS if b<=a)]
def closed_only(T):
    c=P[P.cl<=T].copy(); c["cyc"]=(c.cl-c.eng).dt.days; w=(c.deal_stage=="Won").values; cyc=c.cyc.values
    xs=[x for x in range(0,int(cyc.max())+1) if (cyc>x).sum()>=30]; xmax=max(xs)
    return lambda a: w[cyc>min(max(a,0),xmax)].mean()
def scores(s,T,m):
    p=s.sales_price.values; a=s.age.values
    if m=="price": return p
    if m=="nostale": return np.where(a>MAXC,-1e9,0)+p
    if m=="bands": return np.select([a<=90,a<=MAXC],[2,1],0)*1e6+p
    if m=="ev": f=bands(T); return np.array([f(x) for x in a])*p
    if m=="closed": f=closed_only(T); return np.array([f(x) for x in a])*p
out={}
for T in pd.to_datetime(["2017-06-30","2017-07-31","2017-08-31","2017-09-30"]):
    s=snap(T); tot=s.rev.sum()
    g=s.groupby("sales_agent"); rnd=sum(min(K,len(x))/len(x)*x.rev.sum() for _,x in g)
    out.setdefault("random",[]).append((rnd,tot))
    for m in ["price","nostale","bands","ev","closed"]:
        s["sc"]=scores(s,T,m); top=s.sort_values(["sc","opportunity_id"],ascending=[False,True]).groupby("sales_agent").head(K)
        out.setdefault(m,[]).append((top.rev.sum(),tot))
for m,v in out.items(): print(m, round(100*sum(a for a,_ in v)/sum(b for _,b in v),2), [float(round(100*a/b,2)) for a,b in v])
