"""Auditoria do Dataset 1 (Customer Support Tickets).

Pergunta: os dados operacionais sustentam um diagnóstico de gargalos e de satisfação?
Cada verificação produz um número reproduzível. Saída: app/data/audit.json

Uso: python 01_auditoria_dataset1.py
"""
import re

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score

from common import SEED, TICKETS_CSV, save_json

N_PERMUTATIONS = 2000
SEGMENT = ["Ticket Channel", "Ticket Priority", "Ticket Type"]
# Ações técnicas que qualquer resolução real mencionaria. "order"/"account" ficam de fora de propósito:
# aparecem nas resoluções só como palavras soltas de dicionário ("Account eat tax accept.") e são reportadas à parte.
SUPPORT_ACTIONS = r"refund|reset|updat|replac|install|password|softwar|firmwar|restart|reboot|driver|cable|setting"
GENERIC_WORDS = r"\b(?:order|account|ticket)\b"

df = pd.read_csv(TICKETS_CSV)
first_response = pd.to_datetime(df["First Response Time"])
resolution = pd.to_datetime(df["Time to Resolution"])
purchase = pd.to_datetime(df["Date of Purchase"])
df["ttr_h"] = (resolution - first_response).dt.total_seconds() / 3600
closed = df[df["Ticket Status"] == "Closed"].copy()
rng = np.random.default_rng(SEED)
checks = []


def check(id_, titulo, valor, evidencia, peso="alto"):
    checks.append({"id": id_, "titulo": titulo, "valor": valor, "evidencia": evidencia, "peso": peso})
    print(f"[{id_}] {titulo}: {valor}")


# 1. Volume
check("volume", "Volume real", f"{len(df):,}".replace(",", "."),
      f"O brief fala em ~30.000 tickets; o arquivo tem {len(df):,} linhas.".replace(",", "."), "medio")

# 2. Placeholders de template não preenchidos
desc = df["Ticket Description"]
has_placeholder = desc.str.contains(r"\{[a-z_]+\}", regex=True)
placeholder_names = desc.str.findall(r"\{[a-z_]+\}").explode().dropna()
check("placeholders", "Descrições com variável de template não preenchida", f"{has_placeholder.mean():.0%}",
      f"Todas as descrições contêm marcadores como {{product_purchased}}; há {placeholder_names.nunique()} nomes de "
      f"variável distintos (ex.: {{product_paydirt}}, {{tiddlers_id}}) — texto gerado por modelo de linguagem a partir de template.")

# 3. Primeira frase x assunto
first_sentence = desc.str.split(r"(?<=[.?!])\s", n=1, regex=True).str[0]
top_first = first_sentence.value_counts()
top20 = first_sentence.where(first_sentence.isin(top_first.head(20).index))
p_first_subject = stats.chi2_contingency(pd.crosstab(top20, df["Ticket Subject"]))[1]
check("texto_assunto", "Texto do ticket não tem relação com o assunto", f"p = {p_first_subject:.2f}",
      f"Só existem {top_first.size} frases de abertura distintas ({top_first.iloc[0] / len(df):.0%} começam com "
      f"\"{top_first.index[0]}\"). A frase de abertura é independente do assunto (qui-quadrado p = {p_first_subject:.2f}): "
      f"'tela piscando' aparece em tickets de 'Payment issue' e 'Delivery problem'.")

# 4. Janela de tempo impossível
window_h = (max(first_response.max(), resolution.max()) - min(first_response.min(), resolution.min())).total_seconds() / 3600
check("janela", "Todas as respostas e resoluções cabem em", f"{window_h:.0f} horas",
      f"Primeira resposta e resolução de todos os tickets ficam entre {first_response.min():%d/%m/%Y %H:%M} e "
      f"{resolution.max():%d/%m/%Y %H:%M}, enquanto as compras vão de {purchase.min():%Y} a {purchase.max():%Y}.")

# 5. Resolução antes da primeira resposta
negative = (closed["ttr_h"] < 0).mean()
check("negativo", "Tickets fechados 'resolvidos antes da 1ª resposta'", f"{negative:.1%}",
      f"A diferença entre resolução e primeira resposta é simétrica em torno de zero "
      f"(mediana {closed['ttr_h'].median():+.1f} h, de {closed['ttr_h'].min():.0f} h a {closed['ttr_h'].max():+.0f} h): "
      f"é um sorteio uniforme de ±24 h, não um tempo de atendimento.")

# 6. Resoluções são frases aleatórias
res = closed["Resolution"]
support_actions = res.str.contains(SUPPORT_ACTIONS, case=False).sum()
generic_hits = res.str.contains(GENERIC_WORDS, case=False).sum()
check("resolucao", "Resoluções que descrevem alguma ação técnica", f"{support_actions} de {len(res):,}".replace(",", "."),
      f"As resoluções são frases aleatórias de 3 a 8 palavras, no padrão da biblioteca Faker: "
      + " / ".join(f"\"{s}\"" for s in res.sample(3, random_state=2))
      + f". Palavras como 'order' e 'account' aparecem em {generic_hits}, sempre soltas (\"Account eat tax accept.\").")

# 7. E-mails em domínios reservados
reserved = df["Customer Email"].str.endswith(("@example.com", "@example.org", "@example.net")).mean()
check("emails", "E-mails em domínios reservados para documentação", f"{reserved:.0%}",
      "Todos os clientes usam example.com/.org/.net, domínios reservados pela RFC 2606 — clientes fictícios.", "medio")

# 8. Distribuições perfeitamente uniformes
uniform = {}
for col in ["Ticket Channel", "Ticket Priority", "Ticket Type", "Ticket Status", "Customer Gender"]:
    counts = df[col].value_counts()
    uniform[col] = {"counts": counts.to_dict(), "p": stats.chisquare(counts).pvalue}
csat_counts = closed["Customer Satisfaction Rating"].value_counts().sort_index()
uniform["CSAT"] = {"counts": {str(int(k)): v for k, v in csat_counts.items()}, "p": stats.chisquare(csat_counts).pvalue}
# Gênero fica fora da afirmação: não é uniforme ('Other' tem ~2 p.p. a menos, p = 0,007) e nem é campo operacional.
min_p = min(u["p"] for k, u in uniform.items() if k != "Customer Gender")
check("uniforme", "Canal, prioridade, tipo, status e nota são uniformes", f"p ≥ {min_p:.2f}",
      "Telefone, chat, e-mail e redes sociais têm o mesmo volume; as notas 1 a 5 aparecem na mesma proporção "
      "(qui-quadrado de aderência à uniforme, nenhum campo rejeita). Nenhuma operação real é plana assim — é o padrão "
      "de sorteio independente por coluna.", "medio")

# 9. Tipo x assunto
p_type_subject = stats.chi2_contingency(pd.crosstab(df["Ticket Subject"], df["Ticket Type"]))[1]
refund = df[df["Ticket Subject"] == "Refund request"]["Ticket Type"].value_counts(normalize=True)
check("tipo_assunto", "Tipo do ticket é independente do assunto", f"p = {p_type_subject:.2f}",
      f"Tickets com assunto 'Refund request' estão classificados como 'Technical issue' em {refund['Technical issue']:.0%} "
      f"dos casos e como 'Refund request' em só {refund['Refund request']:.0%}.")

# 10. CSAT: nenhuma variável explica a nota
cat_cols = ["Ticket Channel", "Ticket Priority", "Ticket Type", "Ticket Subject", "Customer Gender", "Product Purchased"]
assoc = []
for col in cat_cols:
    ct = pd.crosstab(closed[col], closed["Customer Satisfaction Rating"])
    chi2, p, _, _ = stats.chi2_contingency(ct)
    assoc.append({"variavel": col, "p": p, "cramer_v": np.sqrt(chi2 / (ct.values.sum() * (min(ct.shape) - 1)))})
for col in ["Customer Age", "ttr_h"]:
    r, p = stats.spearmanr(closed[col], closed["Customer Satisfaction Rating"])
    assoc.append({"variavel": col, "p": p, "spearman_r": r})

X = closed[cat_cols].astype("category").apply(lambda s: s.cat.codes)
X["age"] = closed["Customer Age"]
X["ttr_h"] = closed["ttr_h"]
X["purchase_doy"] = pd.to_datetime(closed["Date of Purchase"]).dt.dayofyear
y = closed["Customer Satisfaction Rating"].astype(int)
cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
model_acc = cross_val_score(HistGradientBoostingClassifier(max_iter=200, categorical_features=list(range(len(cat_cols))),
                                                           random_state=SEED), X, y, cv=cv).mean()
dummy_acc = cross_val_score(DummyClassifier(strategy="most_frequent"), X, y, cv=cv).mean()
check("csat", "Modelo com TODAS as variáveis prevê a nota de satisfação com", f"{model_acc:.1%} de acerto",
      f"Chutar sempre a nota mais comum acerta {dummy_acc:.1%}; chutar ao acaso, 20%. Nenhuma variável tem associação "
      f"significativa com a nota (menor p = {min(a['p'] for a in assoc):.2f}).")

# Poder estatístico: menor diferença de CSAT entre dois canais que teríamos detectado
n_per_channel = closed["Ticket Channel"].value_counts().min()
mde = 2.8 * closed["Customer Satisfaction Rating"].std() * np.sqrt(2 / n_per_channel)


# 11. O que uma análise ingênua reportaria — e quantas vezes o mesmo "achado" aparece em dados embaralhados
def worst_segment(frame, value_col, by, agg="mean", pick="max"):
    s = frame.groupby(by)[value_col].agg(agg)
    return (s.idxmax(), s.max()) if pick == "max" else (s.idxmin(), s.min())


naive = []
combo, combo_val = worst_segment(closed, "ttr_h", SEGMENT)
null_combo = np.array([closed.assign(ttr_h=rng.permutation(closed["ttr_h"].values)).groupby(SEGMENT)["ttr_h"].mean().max()
                       for _ in range(N_PERMUTATIONS)])
naive.append({
    "afirmacao": f"O maior gargalo é {combo[0]} × prioridade {combo[1]} × {combo[2]}: {combo_val:.1f} h de resolução, "
                 f"contra {closed['ttr_h'].mean():.1f} h na média.",
    "teste": f"Com os tempos embaralhados ao acaso, a pior das {closed.groupby(SEGMENT).ngroups} combinações chega a esse "
             f"valor em {np.mean(null_combo >= combo_val):.0%} das {N_PERMUTATIONS} simulações.",
    "p": np.mean(null_combo >= combo_val),
    "null_hist": np.histogram(null_combo, bins=24)[0], "null_edges": np.histogram(null_combo, bins=24)[1], "observado": combo_val,
})
prod, prod_val = worst_segment(closed, "Customer Satisfaction Rating", "Product Purchased", pick="min")
null_prod = np.array([closed.assign(c=rng.permutation(closed["Customer Satisfaction Rating"].values))
                      .groupby("Product Purchased")["c"].mean().min() for _ in range(N_PERMUTATIONS)])
naive.append({
    "afirmacao": f"O produto com pior satisfação é {prod} (nota {prod_val:.2f}, contra "
                 f"{closed['Customer Satisfaction Rating'].mean():.2f} na média) — priorizar esse produto.",
    "teste": f"Com as notas embaralhadas, o pior de {closed['Product Purchased'].nunique()} produtos fica igual ou abaixo "
             f"disso em {np.mean(null_prod <= prod_val):.0%} das simulações.",
    "p": np.mean(null_prod <= prod_val),
})
channel_median = closed.groupby("Ticket Channel")["ttr_h"].median()
naive.append({
    "afirmacao": f"{channel_median.idxmin()} é o canal mais rápido (mediana de {channel_median.min():.1f} h) — "
                 f"migrar volume para ele.",
    "teste": f"A 'mediana' é negativa: o ticket seria resolvido antes de ser respondido. Diferença entre canais: "
             f"Kruskal-Wallis p = {stats.kruskal(*[g['ttr_h'] for _, g in closed.groupby('Ticket Channel')]).pvalue:.2f}.",
    "p": stats.kruskal(*[g["ttr_h"] for _, g in closed.groupby("Ticket Channel")]).pvalue,
})
for n in naive:
    print(" ingênuo:", n["afirmacao"], "|", n["teste"])

hist_counts, hist_edges = np.histogram(closed["ttr_h"], bins=np.arange(-24, 25, 2))
csat_by_channel = closed.groupby("Ticket Channel")["Customer Satisfaction Rating"].agg(["mean", "std", "count"])
csat_by_channel["ci95"] = 1.96 * csat_by_channel["std"] / np.sqrt(csat_by_channel["count"])

save_json("audit.json", {
    "linhas": len(df), "linhas_brief": 30000, "fechados": len(closed),
    "checks": checks,
    "ingenuo": naive,
    "csat": {"modelo": model_acc, "classe_mais_comum": dummy_acc, "acaso": 0.2, "associacoes": assoc,
             "mde_canal": mde, "por_canal": csat_by_channel[["mean", "ci95", "count"]].reset_index().to_dict("records")},
    "ttr_hist": {"counts": hist_counts, "edges": hist_edges},
    "uniformidade": uniform,
    "exemplos": {
        "descricao": desc.sample(2, random_state=7).tolist(),
        "resolucao": res.sample(5, random_state=3).tolist(),
    },
})
print(f"MDE de CSAT entre canais (80% de poder): {mde:.2f} ponto")
