"""Bloco 1: auditoria dos dois datasets. Rodar da raiz da submissao:
.venv/bin/python -I solution/analise/01_auditoria.py
"""
import sys
from pathlib import Path
import pandas as pd

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
pd.set_option("display.width", 200, "display.max_columns", 50, "display.max_colwidth", 120)

def h(t): print(f"\n=== {t} ===")

# ---------------- Dataset 1 ----------------
d1 = pd.read_csv(RAW / "customer_support_tickets.csv")
h("D1 shape / dtypes"); print(d1.shape); print(d1.dtypes)
h("D1 nulos"); print(d1.isna().sum())
h("D1 head"); print(d1.head(3).T)
h("D1 duplicados"); print("linhas:", d1.duplicated().sum(), "| Ticket ID:", d1["Ticket ID"].duplicated().sum(),
      "| email:", d1["Customer Email"].duplicated().sum())
for c in ["Ticket Type","Ticket Subject","Ticket Status","Ticket Priority","Ticket Channel","Product Purchased","Customer Gender"]:
    h(f"D1 {c}"); print(d1[c].value_counts(dropna=False))
h("D1 Customer Age"); print(d1["Customer Age"].describe())

# Tempos: o que sao?
for c in ["Date of Purchase","First Response Time","Time to Resolution"]:
    h(f"D1 {c} amostra"); print(d1[c].dropna().head(5).tolist())
d1["purchase"] = pd.to_datetime(d1["Date of Purchase"], errors="coerce")
d1["frt"] = pd.to_datetime(d1["First Response Time"], errors="coerce")
d1["ttr"] = pd.to_datetime(d1["Time to Resolution"], errors="coerce")
h("D1 faixas de data"); print(d1[["purchase","frt","ttr"]].agg(["min","max"]))
h("D1 preenchimento de tempos x status")
print(d1.groupby("Ticket Status")[["frt","ttr","Customer Satisfaction Rating","Resolution"]].apply(lambda g: g.notna().mean().round(3)))
d1["delta_h"] = (d1["ttr"] - d1["frt"]).dt.total_seconds() / 3600
h("D1 TTR - FRT em horas (so Closed)"); print(d1["delta_h"].describe())
print("negativos:", (d1["delta_h"] < 0).sum(), "de", d1["delta_h"].notna().sum())
h("D1 FRT antes da compra?"); print((d1["frt"] < d1["purchase"]).sum())

# Satisfacao
h("D1 CSAT distribuicao"); print(d1["Customer Satisfaction Rating"].value_counts(dropna=False).sort_index())
cl = d1[d1["Customer Satisfaction Rating"].notna()]
for c in ["Ticket Priority","Ticket Channel","Ticket Type","Product Purchased"]:
    h(f"D1 CSAT medio por {c}"); print(cl.groupby(c)["Customer Satisfaction Rating"].agg(["mean","count"]).round(3).sort_values("mean"))
h("D1 CSAT x delta_h (corr Spearman)"); print(cl[["Customer Satisfaction Rating","delta_h","Customer Age"]].corr(method="spearman").round(3))
h("D1 Prioridade x Tipo (crosstab %)"); print(pd.crosstab(d1["Ticket Type"], d1["Ticket Priority"], normalize="index").round(3))

# Texto
desc = d1["Ticket Description"].astype(str)
h("D1 descricoes exemplo"); [print("-", t[:300]) for t in desc.sample(6, random_state=42)]
h("D1 placeholders"); print("contem '{product_purchased}':", desc.str.contains(r"\{product_purchased\}").sum(),
      "| contem '{':", desc.str.contains(r"\{").sum())
first = desc.str.split(".").str[0]
h("D1 primeiras frases mais repetidas"); print(first.value_counts().head(10))
print("primeiras frases distintas:", first.nunique(), "de", len(first))
h("D1 Subject bate com a descricao? (palavra-chave do assunto aparece no texto)")
kw = d1["Ticket Subject"].str.lower().str.split().str[0]
print(pd.Series([k in t.lower() for k, t in zip(kw, desc)]).mean().round(3))
h("D1 Resolution exemplo"); print(d1["Resolution"].dropna().sample(5, random_state=1).tolist())

# ---------------- Dataset 2 ----------------
d2 = pd.read_csv(RAW / "all_tickets_processed_improved_v3.csv")
h("D2 shape / dtypes"); print(d2.shape); print(d2.dtypes)
h("D2 nulos"); print(d2.isna().sum())
txt_col = d2.columns[0]; lab_col = d2.columns[-1]
h("D2 categorias"); print(d2[lab_col].value_counts(dropna=False)); print((d2[lab_col].value_counts(normalize=True)*100).round(1))
h("D2 tamanho texto (palavras)"); print(d2[txt_col].astype(str).str.split().str.len().describe())
h("D2 exemplos"); [print(f"[{r[lab_col]}]", str(r[txt_col])[:250]) for _, r in d2.sample(8, random_state=7).iterrows()]
h("D2 duplicados"); print("texto dup:", d2[txt_col].duplicated().sum(), "| texto dup com rotulo diferente:",
      d2.groupby(txt_col)[lab_col].nunique().gt(1).sum())

# ---------------- Testes de uniformidade e correspondencia ----------------
from scipy.stats import chi2_contingency, kruskal
h("Testes: CSAT depende de alguma coisa? (chi2 / Kruskal, so Closed)")
for c in ["Ticket Priority","Ticket Channel","Ticket Type","Ticket Subject","Product Purchased","Customer Gender"]:
    chi = chi2_contingency(pd.crosstab(cl[c], cl["Customer Satisfaction Rating"]))
    kw_p = kruskal(*[g["Customer Satisfaction Rating"].values for _, g in cl.groupby(c)]).pvalue
    print(f"{c:20s} chi2 p={chi.pvalue:.3f} | kruskal p={kw_p:.3f}")
h("Testes: Ticket Type x Ticket Subject independentes?")
ct = pd.crosstab(d1["Ticket Type"], d1["Ticket Subject"])
print("chi2 p=", round(chi2_contingency(ct).pvalue, 3)); print(ct)
h("Testes: Type x Priority / Channel x Priority")
print("type x prio p=", round(chi2_contingency(pd.crosstab(d1["Ticket Type"], d1["Ticket Priority"])).pvalue, 3))
print("canal x prio p=", round(chi2_contingency(pd.crosstab(d1["Ticket Channel"], d1["Ticket Priority"])).pvalue, 3))
h("Carimbo de hora x Ticket ID (gerado em sequencia?)")
s = d1.dropna(subset=["frt"]).copy()
s["seg_do_dia"] = s["frt"].dt.second
print("Spearman Ticket ID x segundos do FRT:", round(s[["Ticket ID","seg_do_dia"]].corr(method="spearman").iloc[0,1], 3))
print(s[["Ticket ID","First Response Time"]].head(8).to_string(index=False))
h("Emails repetidos: mesmo nome?")
dup = d1[d1["Customer Email"].duplicated(keep=False)].sort_values("Customer Email")
print("emails repetidos com nomes diferentes:", dup.groupby("Customer Email")["Customer Name"].nunique().gt(1).sum(), "de", dup["Customer Email"].nunique())
h("Texto da descricao x Ticket Subject: frase-modelo vs assunto")
d1["frase"] = desc.str.extract(r"(?:Please assist\.\s*.*?)?((?:I'm|I've|My|The)[^.]*\{product_purchased\}[^.]*)", expand=False)
tmpl = d1[~first.str.startswith("I'm having an issue with the")]
print("tickets cuja 1a frase e especifica:", len(tmpl))
print(pd.crosstab(tmpl["Ticket Description"].str.split(".").str[0], tmpl["Ticket Subject"]).iloc[:, :6].head(6))
