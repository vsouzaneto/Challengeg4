"""
Diagnóstico operacional — Dataset 1 (Customer Support Ticket Dataset).

Gera `../app/data/generated/diagnostico.json`, consumido pela página /diagnostico do app.

Princípio: antes de responder "onde perdemos tempo", auditar se os dados
conseguem responder isso. Toda conclusão vem acompanhada de teste estatístico.

Uso:
    python diagnostico.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.inspection import permutation_importance

ROOT = Path(__file__).parent
D1 = ROOT.parent / "app" / "data" / "raw" / "customer_support_tickets.csv"
OUT = ROOT.parent / "app" / "data" / "generated" / "diagnostico.json"
SEED = 42

df = pd.read_csv(D1)
df["frt"] = pd.to_datetime(df["First Response Time"])
df["ttr"] = pd.to_datetime(df["Time to Resolution"])
df["res_hours"] = (df["ttr"] - df["frt"]).dt.total_seconds() / 3600
closed = df[df["Ticket Status"] == "Closed"].copy()
valid = closed[closed["res_hours"] > 0].copy()

out: dict = {}


def r(x, n=2):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), n)


def cramers_v(a: pd.Series, b: pd.Series) -> tuple[float, float]:
    ct = pd.crosstab(a, b)
    chi2, p, _, _ = stats.chi2_contingency(ct)
    n = ct.values.sum()
    k = min(ct.shape) - 1
    return float(np.sqrt(chi2 / (n * k))), float(p)


# ---------------------------------------------------------------------------
# 1. Auditoria de qualidade dos dados
# ---------------------------------------------------------------------------
placeholders = df["Ticket Description"].str.findall(r"\{[a-z_]+\}").explode().value_counts()
type_subject_v, type_subject_p = cramers_v(df["Ticket Type"], df["Ticket Subject"])
csat_counts = closed["Customer Satisfaction Rating"].value_counts().sort_index()
csat_uniform_p = float(stats.chisquare(csat_counts.values).pvalue)

# O texto da descrição carrega sinal sobre o tipo do ticket? (se não, o "tipo" é ruído)
X_tr, X_te, y_tr, y_te = train_test_split(
    df["Ticket Description"], df["Ticket Type"], test_size=0.25, random_state=SEED, stratify=df["Ticket Type"]
)
vec = TfidfVectorizer(sublinear_tf=True, min_df=2)
clf = LogisticRegression(max_iter=2000)
clf.fit(vec.fit_transform(X_tr), y_tr)
text_to_type_acc = float((clf.predict(vec.transform(X_te)) == y_te).mean())

X_tr, X_te, y_tr, y_te = train_test_split(
    df["Ticket Description"], df["Ticket Subject"], test_size=0.25, random_state=SEED, stratify=df["Ticket Subject"]
)
clf.fit(vec.fit_transform(X_tr), y_tr)
text_to_subject_acc = float((clf.predict(vec.transform(X_te)) == y_te).mean())

resolution_examples = closed["Resolution"].dropna().sample(4, random_state=SEED).tolist()

out["data_quality"] = {
    "rows": int(len(df)),
    "rows_claimed_in_brief": 30000,
    "status_counts": df["Ticket Status"].value_counts().to_dict(),
    "missing_first_response": int(df["frt"].isna().sum()),
    "frt_window": [str(df["frt"].min()), str(df["frt"].max())],
    "frt_window_hours": r((df["frt"].max() - df["frt"].min()).total_seconds() / 3600, 1),
    "has_creation_timestamp": False,
    "closed": int(len(closed)),
    "closed_negative_resolution": int((closed["res_hours"] < 0).sum()),
    "closed_negative_resolution_pct": r((closed["res_hours"] < 0).mean() * 100, 1),
    "valid_resolution_rows": int(len(valid)),
    "placeholder_pct": r(df["Ticket Description"].str.contains(r"\{product_purchased\}").mean() * 100, 1),
    "placeholders": {k: int(v) for k, v in placeholders.head(6).items()},
    "type_subject_cramers_v": r(type_subject_v, 3),
    "type_subject_p": r(type_subject_p, 3),
    "csat_distribution": {str(int(k)): int(v) for k, v in csat_counts.items()},
    "csat_uniform_p": r(csat_uniform_p, 3),
    "text_to_type_accuracy": r(text_to_type_acc * 100, 1),
    "text_to_type_chance": r(100 / df["Ticket Type"].nunique(), 1),
    "text_to_subject_accuracy": r(text_to_subject_acc * 100, 1),
    "text_to_subject_chance": r(100 / df["Ticket Subject"].nunique(), 1),
    "resolution_examples": resolution_examples,
    "distributions": {
        c: df[c].value_counts(normalize=True).mul(100).round(1).to_dict()
        for c in ["Ticket Type", "Ticket Priority", "Ticket Channel"]
    },
}

# ---------------------------------------------------------------------------
# 2. Onde o fluxo trava? (somente durações válidas: TTR > FRT)
# ---------------------------------------------------------------------------


def describe(g: pd.Series) -> dict:
    return {
        "n": int(g.size),
        "mean": r(g.mean()),
        "median": r(g.median()),
        "p75": r(g.quantile(0.75)),
        "p90": r(g.quantile(0.90)),
        "p95": r(g.quantile(0.95)),
    }


bottlenecks = {}
for dim, col in [("channel", "Ticket Channel"), ("type", "Ticket Type"), ("priority", "Ticket Priority"), ("subject", "Ticket Subject")]:
    groups = [g["res_hours"].values for _, g in valid.groupby(col)]
    kw = stats.kruskal(*groups)
    bottlenecks[dim] = {
        "rows": {k: describe(g["res_hours"]) for k, g in valid.groupby(col)},
        "kruskal_p": r(kw.pvalue, 3),
    }

# Críticos são atendidos mais rápido?
crit = valid.loc[valid["Ticket Priority"] == "Critical", "res_hours"]
low = valid.loc[valid["Ticket Priority"] == "Low", "res_hours"]
mw = stats.mannwhitneyu(crit, low, alternative="less")
bottlenecks["critical_vs_low"] = {
    "critical_median": r(crit.median()),
    "low_median": r(low.median()),
    "mannwhitney_p_critical_faster": r(mw.pvalue, 3),
}

combo = (
    valid.groupby(["Ticket Channel", "Ticket Type", "Ticket Priority"])["res_hours"]
    .agg(n="size", median="median", p90=lambda s: s.quantile(0.9), total="sum")
    .reset_index()
)
combo = combo[combo["n"] >= 10]
overall_median = valid["res_hours"].median()
combo["excess_hours"] = (combo["median"] - overall_median) * combo["n"]
top = combo.sort_values("median", ascending=False).head(10)
bottom = combo.sort_values("median").head(5)
bottlenecks["combos_worst"] = [
    {"channel": a, "type": b, "priority": c, "n": int(n), "median": r(m), "p90": r(p9)}
    for a, b, c, n, m, p9 in top[["Ticket Channel", "Ticket Type", "Ticket Priority", "n", "median", "p90"]].values
]
bottlenecks["combos_best"] = [
    {"channel": a, "type": b, "priority": c, "n": int(n), "median": r(m), "p90": r(p9)}
    for a, b, c, n, m, p9 in bottom[["Ticket Channel", "Ticket Type", "Ticket Priority", "n", "median", "p90"]].values
]
bottlenecks["overall"] = describe(valid["res_hours"])

# Teste de "acaso": o pior combo é pior do que esperaríamos por sorte?
# Permutação: embaralhar a duração e medir a maior mediana entre combos com n>=10.
rng = np.random.default_rng(SEED)
keys = valid[["Ticket Channel", "Ticket Type", "Ticket Priority"]].astype(str).agg("|".join, axis=1).values
vals = valid["res_hours"].values
eligible = set(combo[["Ticket Channel", "Ticket Type", "Ticket Priority"]].astype(str).agg("|".join, axis=1))
mask = np.isin(keys, list(eligible))
k_e, v_e = keys[mask], vals[mask]
observed_max = float(top["median"].iloc[0])
null_max = []
for _ in range(300):
    perm = rng.permutation(v_e)
    s = pd.Series(perm).groupby(k_e).median()
    null_max.append(float(s.max()))
bottlenecks["worst_combo_permutation_p"] = r(float(np.mean(np.array(null_max) >= observed_max)), 3)
bottlenecks["null_max_median_p50"] = r(float(np.median(null_max)))
out["bottlenecks"] = bottlenecks

# Backlog — o gargalo que os dados mostram de forma inequívoca
out["backlog"] = {
    "open_without_first_response": int(((df["Ticket Status"] == "Open") & df["frt"].isna()).sum()),
    "pending_customer": int((df["Ticket Status"] == "Pending Customer Response").sum()),
    "closed": int(len(closed)),
    "open_pct": r((df["Ticket Status"] == "Open").mean() * 100, 1),
    "pending_pct": r((df["Ticket Status"] == "Pending Customer Response").mean() * 100, 1),
    "critical_pct": r((df["Ticket Priority"] == "Critical").mean() * 100, 1),
    "critical_or_high_pct": r(df["Ticket Priority"].isin(["Critical", "High"]).mean() * 100, 1),
    "open_critical": int(((df["Ticket Status"] == "Open") & (df["Ticket Priority"] == "Critical")).sum()),
}

# ---------------------------------------------------------------------------
# 3. O que impacta satisfação?
# ---------------------------------------------------------------------------
csat = {}
for dim, col in [("channel", "Ticket Channel"), ("type", "Ticket Type"), ("priority", "Ticket Priority"), ("product", "Product Purchased"), ("gender", "Customer Gender")]:
    groups = [g["Customer Satisfaction Rating"].values for _, g in closed.groupby(col)]
    kw = stats.kruskal(*groups)
    means = closed.groupby(col)["Customer Satisfaction Rating"].mean().sort_values()
    csat[dim] = {
        "kruskal_p": r(kw.pvalue, 3),
        "spread": r(means.max() - means.min()),
        "best": [means.index[-1], r(means.iloc[-1])],
        "worst": [means.index[0], r(means.iloc[0])],
        "means": {k: r(v) for k, v in means.items()} if dim != "product" else None,
    }

rho_res, p_res = stats.spearmanr(valid["res_hours"], valid["Customer Satisfaction Rating"])
rho_age, p_age = stats.spearmanr(closed["Customer Age"], closed["Customer Satisfaction Rating"])
csat["spearman_resolution_hours"] = {"rho": r(rho_res, 3), "p": r(p_res, 3), "n": int(len(valid))}
csat["spearman_age"] = {"rho": r(rho_age, 3), "p": r(p_age, 3)}

# Modelo explicativo: Random Forest com todas as variáveis estruturadas.
feat = pd.get_dummies(
    valid[["Ticket Channel", "Ticket Type", "Ticket Priority", "Product Purchased", "Customer Gender", "Ticket Subject"]]
).assign(age=valid["Customer Age"], res_hours=valid["res_hours"], frt_hour=valid["frt"].dt.hour)
y_cls = valid["Customer Satisfaction Rating"].astype(int)
rf = RandomForestClassifier(n_estimators=300, min_samples_leaf=5, random_state=SEED, n_jobs=-1)
acc_cv = cross_val_score(rf, feat, y_cls, cv=5, scoring="accuracy")
rfr = RandomForestRegressor(n_estimators=300, min_samples_leaf=5, random_state=SEED, n_jobs=-1)
r2_cv = cross_val_score(rfr, feat, y_cls, cv=5, scoring="r2")
majority = y_cls.value_counts(normalize=True).max()
rfr.fit(feat, y_cls)
pi = permutation_importance(rfr, feat, y_cls, n_repeats=5, random_state=SEED, n_jobs=-1)
imp = pd.Series(pi.importances_mean, index=feat.columns).sort_values(ascending=False).head(6)
csat["model"] = {
    "rf_accuracy_cv": r(acc_cv.mean() * 100, 1),
    "majority_baseline": r(majority * 100, 1),
    "rf_r2_cv": r(r2_cv.mean(), 3),
    "top_permutation_importance_in_sample": {k: r(v, 4) for k, v in imp.items()},
}
out["csat"] = csat

# ---------------------------------------------------------------------------
# 4. Oportunidade de automação por assunto (Opportunity Matrix)
# ---------------------------------------------------------------------------
# Julgamento humano (não derivado do dataset): risco e complexidade por assunto.
# Racional documentado em docs/automacao.md.
MATRIX = {
    "Account access": ("Baixa", "Médio", "Assistida", "Reset de senha é self-service; acesso bloqueado/suspeita de fraude vai p/ humano"),
    "Product setup": ("Baixa", "Baixo", "Automática", "Passo a passo documentável na KB"),
    "Installation support": ("Baixa", "Baixo", "Automática", "Guias de instalação versionados"),
    "Battery life": ("Baixa", "Baixo", "Automática", "Troubleshooting padronizado"),
    "Product recommendation": ("Baixa", "Baixo", "Automática", "Catálogo + regras; potencial upsell"),
    "Product compatibility": ("Baixa", "Baixo", "Automática", "Matriz de compatibilidade é dado estruturado"),
    "Peripheral compatibility": ("Baixa", "Baixo", "Automática", "Matriz de compatibilidade"),
    "Network problem": ("Média", "Baixo", "Assistida", "Diagnóstico guiado, escala se persistir"),
    "Display issue": ("Média", "Baixo", "Assistida", "Pode ser defeito de hardware (garantia)"),
    "Software bug": ("Média", "Médio", "Assistida", "IA coleta contexto e versão; humano confirma bug"),
    "Delivery problem": ("Média", "Médio", "Assistida", "Requer consulta a pedido (tool via MCP)"),
    "Hardware issue": ("Alta", "Médio", "Assistida", "Pode virar RMA/garantia"),
    "Data loss": ("Alta", "Alto", "Humano", "Impacto alto e irreversível; julgamento técnico"),
    "Payment issue": ("Média", "Alto", "Humano", "Decisão financeira"),
    "Refund request": ("Média", "Alto", "Humano", "Decisão financeira — IA só prepara o caso"),
    "Cancellation request": ("Média", "Alto", "Humano", "Churn: oportunidade de retenção exige humano"),
}
HIGH_RISK_TYPES = {"Refund request", "Cancellation request", "Billing inquiry"}
subject_counts = df["Ticket Subject"].value_counts()
opp = []
for subj, n in subject_counts.items():
    cx, risk, mode, why = MATRIX[subj]
    sub = df[df["Ticket Subject"] == subj]
    high_risk_type_pct = sub["Ticket Type"].isin(HIGH_RISK_TYPES).mean()
    opp.append({
        "subject": subj,
        "n": int(n),
        "share": r(n / len(df) * 100, 1),
        "complexity": cx,
        "risk": risk,
        "mode": mode,
        "why": why,
        "high_risk_type_pct": r(high_risk_type_pct * 100, 1),
    })
out["opportunity"] = opp

# Regra efetiva no produto: modo do assunto, mas se o TIPO for financeiro/churn => humano.
def effective_mode(row) -> str:
    if row["Ticket Type"] in {"Refund request", "Cancellation request"}:
        return "Humano"
    mode = MATRIX[row["Ticket Subject"]][2]
    if row["Ticket Type"] == "Billing inquiry" and mode == "Automática":
        return "Assistida"
    return mode


df["mode"] = df.apply(effective_mode, axis=1)
out["mode_share"] = df["mode"].value_counts(normalize=True).mul(100).round(1).to_dict()

# ---------------------------------------------------------------------------
# 5. Quanto estamos desperdiçando? (parâmetros editáveis no app)
# ---------------------------------------------------------------------------
out["waste_defaults"] = {
    "annual_tickets": 30000,
    "aht_minutes": {"Email": 14, "Chat": 10, "Phone": 9, "Social media": 12},
    "channel_share": {k: r(v / 100, 4) for k, v in out["data_quality"]["distributions"]["Ticket Channel"].items()},
    "triage_minutes": 2.5,
    "hour_cost_brl": 48.0,
    "auto_containment": 0.6,
    "assist_aht_reduction": 0.35,
    "human_prep_reduction": 0.15,
    "ai_cost_per_ticket_brl": 0.03,
    "platform_cost_month_brl": 1500,
    "human_review_minutes_auto": 0.5,
    "sources": {
        "aht": "Premissa: benchmarks de mercado de AHT por canal (ajustável). O dataset não tem tempo de manuseio.",
        "hour_cost": "Premissa: custo carregado de analista N1 no Brasil (~R$ 4.5k salário + encargos ≈ R$ 48/h).",
        "ai_cost": "Llama 3.1 8B (Groq) ~US$0,05/M tokens in, ~US$0,08/M out; ~3k tokens/ticket com cascata.",
    },
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str))
print(json.dumps({k: out[k] for k in ["data_quality", "backlog", "mode_share"]}, ensure_ascii=False, indent=1, default=str))
print("CSAT model", out["csat"]["model"])
print("crit vs low", bottlenecks["critical_vs_low"], "perm p", bottlenecks["worst_combo_permutation_p"])
print({d: bottlenecks[d]["kruskal_p"] for d in ["channel", "type", "priority", "subject"]})
print({d: csat[d]["kruskal_p"] for d in ["channel", "type", "priority", "product", "gender"]})
print("worst combos", bottlenecks["combos_worst"][:3])
