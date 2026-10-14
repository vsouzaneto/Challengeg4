"""Bloco 2: numeros do diagnostico. Rodar da raiz da submissao:
.venv/bin/python -I solution/analise/02_diagnostico.py
"""
from pathlib import Path
import itertools
import pandas as pd
from scipy.stats import chi2_contingency, kruskal

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
pd.set_option("display.width", 200, "display.max_columns", 50)
def h(t): print(f"\n=== {t} ===")

d1 = pd.read_csv(RAW / "customer_support_tickets.csv")
N = len(d1)

# ---------- 1. Espera: estrutura do backlog ----------
h("Status")
st = d1["Ticket Status"].value_counts()
print(pd.DataFrame({"n": st, "%": (st / N * 100).round(1)}))
print(f"nao fechados: {(st['Open'] + st['Pending Customer Response'])} = {(st['Open'] + st['Pending Customer Response']) / N * 100:.1f}%")

for c in ["Ticket Priority", "Ticket Channel", "Ticket Type"]:
    ct = pd.crosstab(d1[c], d1["Ticket Status"])
    pct = (ct.div(ct.sum(axis=1), axis=0) * 100).round(1)
    h(f"Status por {c} (%), chi2 p={chi2_contingency(ct).pvalue:.3f}")
    print(pct)

h("Combinacoes canal x prioridade x tipo: % fechado")
g = d1.groupby(["Ticket Channel", "Ticket Priority", "Ticket Type"])["Ticket Status"]
comb = pd.DataFrame({"n": g.size(), "pct_fechado": (g.apply(lambda s: (s == "Closed").mean()) * 100).round(1)})
print("celulas:", len(comb), "| n min/max:", comb.n.min(), comb.n.max())
print("pct fechado min/max/mediana:", comb.pct_fechado.min(), comb.pct_fechado.max(), comb.pct_fechado.median())
ct3 = pd.crosstab([d1["Ticket Channel"], d1["Ticket Priority"], d1["Ticket Type"]], d1["Ticket Status"] == "Closed")
print("chi2 combinacao x fechado p=", round(chi2_contingency(ct3).pvalue, 3))
# o que o acaso sozinho produz: permutacao do status
import numpy as np
rng = np.random.default_rng(42)
spreads = []
for _ in range(500):
    perm = rng.permutation(d1["Ticket Status"].values == "Closed")
    s = pd.Series(perm).groupby([d1["Ticket Channel"], d1["Ticket Priority"], d1["Ticket Type"]]).mean() * 100
    spreads.append(s.max() - s.min())
print(f"amplitude observada {comb.pct_fechado.max() - comb.pct_fechado.min():.1f} pp | amplitude sob acaso (500 permutacoes) p5-p95: {np.percentile(spreads, 5):.1f} a {np.percentile(spreads, 95):.1f} pp")

h("Tipos ligados a dinheiro/saida de cliente")
fin = d1["Ticket Type"].isin(["Refund request", "Billing inquiry", "Cancellation request"])
print(f"Refund+Billing+Cancellation: {fin.sum()} = {fin.mean() * 100:.1f}%")
pay = d1["Ticket Subject"].isin(["Refund request", "Payment issue", "Cancellation request"])
print(f"Assunto Refund/Payment/Cancellation: {pay.sum()} = {pay.mean() * 100:.1f}%")
print(f"Tipo financeiro E assunto financeiro: {(fin & pay).sum()} = {(fin & pay).mean() * 100:.1f}%")

# ---------- 2. Satisfacao ----------
cl = d1[d1["Ticket Status"] == "Closed"].copy()
cl["delta_h"] = (pd.to_datetime(cl["Time to Resolution"]) - pd.to_datetime(cl["First Response Time"])).dt.total_seconds() / 3600
h(f"CSAT (n={len(cl)})")
print("media geral:", round(cl["Customer Satisfaction Rating"].mean(), 3))
rows = []
for c in ["Ticket Priority", "Ticket Channel", "Ticket Type", "Ticket Subject", "Product Purchased", "Customer Gender"]:
    grp = cl.groupby(c)["Customer Satisfaction Rating"].mean()
    rows.append((c, grp.idxmin(), round(grp.min(), 2), grp.idxmax(), round(grp.max(), 2),
                 round(chi2_contingency(pd.crosstab(cl[c], cl["Customer Satisfaction Rating"])).pvalue, 3),
                 round(kruskal(*[x["Customer Satisfaction Rating"] for _, x in cl.groupby(c)]).pvalue, 3)))
print(pd.DataFrame(rows, columns=["variavel", "pior", "media_pior", "melhor", "media_melhor", "chi2_p", "kruskal_p"]).to_string(index=False))
print("Spearman CSAT x idade:", round(cl[["Customer Satisfaction Rating", "Customer Age"]].corr("spearman").iloc[0, 1], 3))
print("Spearman CSAT x (TTR-FRT):", round(cl[["Customer Satisfaction Rating", "delta_h"]].corr("spearman").iloc[0, 1], 3))
# teste com todas as variaveis juntas: arvore/regressao preve melhor que a media?
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
X = pd.get_dummies(cl[["Ticket Priority", "Ticket Channel", "Ticket Type", "Ticket Subject", "Product Purchased", "Customer Gender"]]).assign(age=cl["Customer Age"], delta=cl["delta_h"])
y = cl["Customer Satisfaction Rating"].astype(int)
cv = StratifiedKFold(5, shuffle=True, random_state=42)
acc = cross_val_score(RandomForestClassifier(300, random_state=42, n_jobs=-1), X, y, cv=cv)
print(f"RandomForest com todas as variaveis, acuracia 5-fold: {acc.mean():.3f} (+-{acc.std():.3f}) | chute da classe mais comum: {y.value_counts(normalize=True).max():.3f}")

# ---------- 3. Desperdicio em faixa (premissas) ----------
TICKETS_ANO = 30_000  # brief
# cada premissa: (baixo, base, alto)
P = {
    # triagem MEDIDA: Jesse cronometrou 5 tickets aleatorios do D2 (seed 20261014): media 19,94 s = piso.
    # base 30 s = piso + ~10 s estimados por ele para ler texto original; teto 3 min = texto real com contexto.
    "triagem_min":          (20/60, 0.5, 3),   # min de humano lendo e classificando cada ticket
    "repasse_pct":          (0.10, 0.20, 0.30),# NAO MEDIDA: % de tickets roteados para fila errada
    "repasse_min":          (5, 10, 15),       # NAO MEDIDA: min perdidos por repasse (reler, reencaminhar, contexto)
    "pendente_pct":         (0.25, 0.34, 0.45),# % que passa por "esperando cliente" (base = foto do D1)
    "followups":            (1, 2, 3),         # NAO MEDIDA: cobrancas por ticket pendente
    "followup_min":         (3, 5, 8),         # NAO MEDIDA: min por cobranca
    "reabertura_pct":       (0.05, 0.10, 0.15),# % reaberto ou resposta que nao resolve
    "reabertura_min":       (10, 20, 30),      # min de retrabalho por reabertura
    # custo hora da operacao de atendimento do Jesse (venda, nao suporte): fixo+comissao R$ 29-37, so comissao R$ 56-74
    "custo_hora":           (30, 50, 70),      # R$ por hora de agente
}
def horas(p):
    return {
        "Superprocessamento (triagem manual)": TICKETS_ANO * p["triagem_min"] / 60,
        "Movimentacao (repasse entre filas)":  TICKETS_ANO * p["repasse_pct"] * p["repasse_min"] / 60,
        "Espera que vira trabalho (cobrar cliente)": TICKETS_ANO * p["pendente_pct"] * p["followups"] * p["followup_min"] / 60,
        "Retrabalho (reabertura)":             TICKETS_ANO * p["reabertura_pct"] * p["reabertura_min"] / 60,
    }
cen = {nome: {k: v[i] for k, v in P.items()} for i, nome in enumerate(["baixo", "base", "alto"])}
ETIQUETA = {
    "Superprocessamento (triagem manual)": "recuperavel por automacao",
    "Movimentacao (repasse entre filas)": "recuperavel por automacao",
    "Espera que vira trabalho (cobrar cliente)": "recuperavel por automacao",
    "Retrabalho (reabertura)": "nao recuperavel ate medir a causa",
}
h("Horas/ano por desperdicio e cenario")
tab = pd.DataFrame({c: horas(p) for c, p in cen.items()})
tab.loc["TOTAL"] = tab.sum()
print(tab.round(0).assign(etiqueta=pd.Series(ETIQUETA)))
print("maior item recuperavel no base:", tab['base'].drop('TOTAL')[[k for k,v in ETIQUETA.items() if v.startswith('recup')]].idxmax())
FTE_H = 1600  # horas produtivas por agente por ano (premissa)
for c, p in cen.items():
    t = tab.loc["TOTAL", c]
    print(f"{c}: {t:,.0f} h/ano = {t/12:,.0f} h/mes = {t/FTE_H:.1f} FTE | R$ {t*p['custo_hora']:,.0f}/ano (custo hora R$ {p['custo_hora']})")

h("Sensibilidade: cada premissa de baixo a alto, demais no base (total h/ano)")
base_total = sum(horas(cen["base"]).values())
sens = []
for k in P:
    if k == "custo_hora":
        continue
    lo = sum(horas({**cen["base"], k: P[k][0]}).values())
    hi = sum(horas({**cen["base"], k: P[k][2]}).values())
    sens.append((k, P[k][0], P[k][2], round(lo), round(hi), round(hi - lo)))
print(f"total base: {base_total:,.0f} h/ano")
print(pd.DataFrame(sens, columns=["premissa", "baixo", "alto", "total_se_baixo", "total_se_alto", "amplitude"]).sort_values("amplitude", ascending=False).to_string(index=False))
