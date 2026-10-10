import pandas as pd, numpy as np
from scipy.stats import chi2_contingency
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
import os, pathlib
D = os.environ.get("CRM_DATA_DIR", str(pathlib.Path(__file__).resolve().parent.parent / "data"))
P=pd.read_csv(f"{D}/sales_pipeline.csv").merge(pd.read_csv(f"{D}/sales_teams.csv"),on="sales_agent")
P["eng"]=pd.to_datetime(P.engage_date); P["cl"]=pd.to_datetime(P.close_date)
cl=P[P.deal_stage.isin(["Won","Lost"])].copy(); cl["won"]=cl.deal_stage=="Won"
cl["cmq"]=(cl.cl.dt.month-1)%3+1   # mês dentro do trimestre (1,2,3)
cl["cyc"]=(cl.cl-cl.eng).dt.days
print("1) Taxa de vitória por mês do trimestre do FECHAMENTO:"); print(cl.groupby("cmq").won.agg(["size","mean"]).round(3).to_string())
print("\n2) Dia do mês do fechamento — ganhos em meses de fim de trimestre (quartis):", cl[(cl.cmq==3)&cl.won].cl.dt.day.quantile([.1,.25,.5,.75,.9]).tolist())
print("   perdidos em meses de fim de trimestre:", cl[(cl.cmq==3)&~cl.won].cl.dt.day.quantile([.1,.25,.5,.75,.9]).tolist())
print("   ganhos em meses 1-2:", cl[(cl.cmq<3)&cl.won].cl.dt.day.quantile([.1,.25,.5,.75,.9]).tolist())
print("\n3) Distribuição de ciclo: ganhos x perdidos por fechamento em fim de trimestre")
print(cl.groupby(["cmq","won"]).cyc.describe()[["count","25%","50%","75%"]].round(0).to_string())
# 4) atributos conhecidos no início (coorte com janela completa)
d=P[(P.deal_stage!="Prospecting")&(P.eng<=pd.Timestamp("2017-08-15"))].copy()
d["y"]=d.deal_stage=="Won"; d["emq"]=(d.eng.dt.month-1)%3+1; d["emonth"]=d.eng.dt.strftime("%Y-%m"); d["dow"]=d.eng.dt.dayofweek
d["days_to_qend"]=(d.eng.dt.to_period("Q").dt.end_time.dt.normalize()-d.eng).dt.days
for col in ["emq","emonth","dow"]:
    ct=pd.crosstab(d[col],d.y); p=chi2_contingency(ct)[1]; print(f"\n4) Ganhou (vs perdeu/nunca fechou) por {col}: p={p:.2e}"); print((ct[True]/ct.sum(axis=1)).round(3).to_dict())
d["bucket_qend"]=pd.cut(d.days_to_qend,[-1,15,30,45,60,75,92]); print("\n   por dias até o fim do trimestre no início do deal:"); print(d.groupby("bucket_qend",observed=True).y.agg(["size","mean"]).round(3).to_string())
# 5) Modelos com o que se sabe no início
X=pd.DataFrame({"emq":d.emq,"dqe":d.days_to_qend,"dow":d.dow,"m":d.eng.dt.month,"prod":d["product"].astype("category"),"agent":d.sales_agent.astype("category")})
cv=StratifiedKFold(5,shuffle=True,random_state=0)
gb=HistGradientBoostingClassifier(categorical_features="from_dtype",random_state=0)
print("\n5) AUC (ganhou eventualmente) com atributos do início — tempo + produto + vendedor:", cross_val_score(gb,X,d.y,cv=cv,scoring="roc_auc").mean().round(3))
print("   só produto+vendedor:", cross_val_score(gb,X[["prod","agent"]],d.y,cv=cv,scoring="roc_auc").mean().round(3))
print("   só dias até fim do trimestre:", cross_val_score(gb,X[["dqe"]],d.y,cv=cv,scoring="roc_auc").mean().round(3))
