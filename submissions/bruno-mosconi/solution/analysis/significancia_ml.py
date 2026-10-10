"""O ganho do ML sobre o valor ponderado é significativo? (N18, revisão inicial)

Repete o modelo de backtest_exploratorio.py (gradient boosting treinado na foto T-90 com o
desfecho observável em T; atributos: idade, preço, dias até o fim do trimestre, produto,
vendedor), agora com desempate pelo ID e 5 sementes. Grava a receita capturada pelos 10
primeiros de cada vendedor em cada foto, para o teste pareado em TypeScript
(scripts/auditoria.ts, função pairedTest).

Saída: saidas/ml-por-vendedor.csv
Rodar: .venv/bin/python -I significancia_ml.py
"""

import os
import pathlib

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

AQUI = pathlib.Path(__file__).resolve().parent
D = os.environ.get("CRM_DATA_DIR", str(AQUI.parent / "data"))
H, K, MAXC = 90, 10, 138
SEMENTES = [0, 1, 2, 3, 4]
FOTOS = pd.to_datetime(["2017-06-30", "2017-07-31", "2017-08-31", "2017-09-30"])

P = pd.read_csv(f"{D}/sales_pipeline.csv")
P["product"] = P["product"].replace({"GTXPro": "GTX Pro"})
P = P.merge(pd.read_csv(f"{D}/products.csv"), on="product")
P["eng"] = pd.to_datetime(P.engage_date)
P["cl"] = pd.to_datetime(P.close_date)
P = P[P.deal_stage != "Prospecting"].copy()


def foto(T):
    s = P[(P.eng <= T) & (P.cl.isna() | (P.cl > T))].copy()
    s["age"] = (T - s.eng).dt.days
    s["rev"] = np.where((s.deal_stage == "Won") & (s.cl <= T + pd.Timedelta(days=H)), s.close_value, 0.0)
    s["dqe"] = (s.eng.dt.to_period("Q").dt.end_time.dt.normalize() - s.eng).dt.days
    return s


def atributos(s, categorias=None):
    X = pd.DataFrame({
        "age": s.age, "price": s.sales_price, "dqe": s.dqe,
        "prod": pd.Categorical(s["product"], categories=None if categorias is None else categorias["prod"]),
        "agent": pd.Categorical(s.sales_agent, categories=None if categorias is None else categorias["agent"]),
    })
    return X


def ml_scores(s, T, semente):
    T0 = T - pd.Timedelta(days=H)
    treino = foto(T0)
    y = (treino.deal_stage == "Won") & (treino.cl <= T)  # desfecho já observável em T
    Xt = atributos(treino)
    m = HistGradientBoostingClassifier(categorical_features="from_dtype", random_state=semente).fit(Xt, y)
    cats = {"prod": Xt["prod"].cat.categories, "agent": Xt["agent"].cat.categories}
    return m.predict_proba(atributos(s, cats))[:, 1] * s.sales_price.values


def curva_por_dia(T):
    """Valor ponderado do exploratório: chance por dia exato (em risco: duração > a, mínimo 30)."""
    c = P[P.eng <= T - pd.Timedelta(days=MAXC)].copy()
    c["t"] = np.where(c.cl.notna() & (c.cl <= T), (c.cl - c.eng).dt.days, (T - c.eng).dt.days)
    c["w"] = (c.deal_stage == "Won") & (c.cl <= T)
    t, w = c.t.values, c.w.values

    def f(a):
        r = t > a
        return w[r].mean() if r.sum() >= 30 else 0.0
    return f


def top_receita(s, score):
    s = s.assign(sc=score).sort_values(["sc", "opportunity_id"], ascending=[False, True])
    return s.groupby("sales_agent").head(K).groupby("sales_agent").rev.sum()


linhas = []
for T in FOTOS:
    s = foto(T)
    den = s.groupby("sales_agent").rev.sum()
    f = curva_por_dia(T)
    ev_dia = top_receita(s, np.array([f(a) for a in s.age]) * s.sales_price.values)
    ml = {k: top_receita(s, ml_scores(s, T, k)) for k in SEMENTES}
    for agente in sorted(den.index):
        linha = {"agent": agente, "t": T.date().isoformat(), "den": den[agente], "ev_dia": ev_dia.get(agente, 0.0)}
        linha.update({f"ml_{k}": ml[k].get(agente, 0.0) for k in SEMENTES})
        linhas.append(linha)

R = pd.DataFrame(linhas)
R.to_csv(AQUI / "saidas" / "ml-por-vendedor.csv", index=False)
tot = R.den.sum()
print("valor ponderado por dia (exploratório):", round(100 * R.ev_dia.sum() / tot, 2))
for k in SEMENTES:
    print(f"ML semente {k}:", round(100 * R[f'ml_{k}'].sum() / tot, 2))
