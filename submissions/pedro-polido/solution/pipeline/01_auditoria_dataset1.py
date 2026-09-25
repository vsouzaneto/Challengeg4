"""Auditoria do Dataset 1 (Customer Support Tickets).

Pergunta: os dados operacionais sustentam um diagnóstico de gargalos e de satisfação?
Cada verificação produz um número reproduzível. Saída: app/data/audit.json

Uso: python 01_auditoria_dataset1.py
"""
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score

from common import SEED, TICKETS_CSV, br, save_json

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


def pct(x, d=0):
    return br(100 * x, d, "%")


def check(id_, titulo, valor, evidencia, peso="alto"):
    checks.append({"id": id_, "titulo": titulo, "valor": valor, "evidencia": evidencia, "peso": peso})
    print(f"[{id_}] {titulo}: {valor}")


# 1. Volume: o "~30.000" do brief bate com as linhas físicas; as quebras de linha estão dentro das descrições
raw_text = open(TICKETS_CSV, encoding="utf-8").read()
physical_lines = raw_text.count("\n")
embedded = int(df["Ticket Description"].str.count("\n").sum())
contiguous = sorted(df["Ticket ID"]) == list(range(1, len(df) + 1))
check("volume", "Registros no arquivo", br(len(df), 0),
      f"O brief fala em ~30.000 tickets. O arquivo tem {br(physical_lines, 0)} linhas físicas, mas {br(len(df), 0)} "
      f"registros: {br(embedded, 0)} quebras de linha estão dentro das descrições (1 cabeçalho + {br(len(df), 0)} + "
      f"{br(embedded, 0)} = {br(1 + len(df) + embedded, 0)}). IDs de 1 a {br(len(df), 0)}"
      f"{', sem buracos' if contiguous else ', com buracos'}.", "medio")

# 2. Placeholders de template não preenchidos
desc = df["Ticket Description"]
has_placeholder = desc.str.contains(r"\{[a-z_]+\}", regex=True)
placeholder_names = desc.str.findall(r"\{[a-z_]+\}").explode().dropna()
check("placeholders", "Descrições com variável de template não preenchida", pct(has_placeholder.mean()),
      f"Todas trazem marcadores como {{product_purchased}}. Há {placeholder_names.nunique()} nomes de variável "
      f"diferentes (ex.: {{product_paydirt}}, {{tiddlers_id}}): padrão de texto montado a partir de template sem substituir as variáveis.")

# 3. Texto x assunto
first_sentence = desc.str.split(r"(?<=[.?!])\s", n=1, regex=True).str[0]
top_first = first_sentence.value_counts()
top20 = first_sentence.where(first_sentence.isin(top_first.head(20).index))
p_first_subject = stats.chi2_contingency(pd.crosstab(top20, df["Ticket Subject"]))[1]
flicker = df.loc[desc.str.contains("screen is flickering", regex=False), "Ticket Subject"].value_counts()
flicker_other = [s for s in flicker.index if s not in ("Display issue", "Hardware issue")][:2]
check("texto_assunto", "Texto do ticket × assunto do ticket", f"p = {br(p_first_subject, 2)}",
      f"Só existem {top_first.size} frases de abertura ({pct(top_first.iloc[0] / len(df))} começam com "
      f"\"{top_first.index[0]}\") e não têm associação detectável com o assunto. \"The screen is flickering\" aparece em "
      f"tickets de '{flicker_other[0]}' e '{flicker_other[1]}'.")

# 4. Janela de tempo impossível
window_h = (max(first_response.max(), resolution.max()) - min(first_response.min(), resolution.min())).total_seconds() / 3600
check("janela", "Todas as respostas e resoluções cabem em", f"{window_h:.0f} horas",
      f"A primeira resposta e a resolução de todos os tickets ficam entre "
      f"{min(first_response.min(), resolution.min()):%d/%m/%Y %H:%M} e "
      f"{resolution.max():%d/%m/%Y %H:%M}, enquanto as compras vão de {purchase.min():%Y} a {purchase.max():%Y}.")

# 5. Resolução antes da primeira resposta
# Cada horário é um instante-base + sorteio uniforme de ±12 h. A diferença de dois sorteios independentes assim tem
# forma de triângulo: desvio-padrão sqrt(2 * 24² / 12) = 9,8 h e curtose -0,6. (A 1ª hipótese, "uniforme na janela
# inteira de 27 h", foi rejeitada pelo teste KS: p < 0,001.)
negative = (closed["ttr_h"] < 0).mean()
ttr_sd, ttr_kurt = closed["ttr_h"].std(), stats.kurtosis(closed["ttr_h"])
check("negativo", "Tickets fechados \"resolvidos antes da 1ª resposta\"", pct(negative, 1),
      f"A diferença entre resolução e 1ª resposta é simétrica em torno de zero (média de {br(closed['ttr_h'].mean(), 2)} h) "
      f"e tem forma de triângulo: desvio-padrão de {br(ttr_sd, 1)} h e curtose de {br(ttr_kurt, 1)}, contra 9,8 h e -0,6 "
      f"na diferença entre dois horários sorteados de forma independente em ±12 h. Não é tempo de atendimento.")

# 6. Resoluções são frases aleatórias
res = closed["Resolution"]
support_actions = res.str.contains(SUPPORT_ACTIONS, case=False).sum()
generic_hits = res.str.contains(GENERIC_WORDS, case=False).sum()
check("resolucao", "Resoluções que descrevem alguma ação técnica", f"{support_actions} de {br(len(res), 0)}",
      "São frases aleatórias de 3 a 8 palavras, no padrão da biblioteca Faker: "
      + " / ".join(f"\"{s}\"" for s in res.sample(3, random_state=2))
      + f". Palavras como 'order' e 'account' aparecem em {generic_hits}, sempre soltas (\"Account eat tax accept.\").")

# 7. E-mails em example.com/.org/.net: NÃO entra como evidência. Anonimizar e-mail assim é prática legítima ao publicar
# um dataset real, então sozinho não prova nada. Fica registrado só no JSON.
reserved = df["Customer Email"].str.endswith(("@example.com", "@example.org", "@example.net")).mean()

# 8. Distribuições perfeitamente uniformes
uniform = {}
for col in ["Ticket Channel", "Ticket Priority", "Ticket Type", "Ticket Status", "Customer Gender"]:
    counts = df[col].value_counts()
    uniform[col] = {"counts": counts.to_dict(), "p": stats.chisquare(counts).pvalue}
csat_counts = closed["Customer Satisfaction Rating"].value_counts().sort_index()
uniform["CSAT"] = {"counts": {str(int(k)): v for k, v in csat_counts.items()}, "p": stats.chisquare(csat_counts).pvalue}
# Gênero fica fora da afirmação: não é uniforme ('Other' tem ~2 p.p. a menos, p = 0,007) e nem é campo operacional.
min_p = min(u["p"] for k, u in uniform.items() if k != "Customer Gender")
check("uniforme", "Canal, prioridade, tipo, status e nota compatíveis com distribuição uniforme", f"p ≥ {br(min_p, 2)}",
      "Telefone, chat, e-mail e redes sociais têm o mesmo volume, e as notas de 1 a 5 aparecem na mesma proporção "
      "(qui-quadrado de aderência à uniforme: nenhum campo rejeita). Operações reais raramente são planas assim; o "
      "padrão é compatível com sorteio independente por coluna.", "medio")

# 9. Tipo x assunto
ct_ts = pd.crosstab(df["Ticket Subject"], df["Ticket Type"])
chi2_ts, p_type_subject, _, _ = stats.chi2_contingency(ct_ts)
v_ts = np.sqrt(chi2_ts / (ct_ts.values.sum() * (min(ct_ts.shape) - 1)))
refund = df[df["Ticket Subject"] == "Refund request"]["Ticket Type"].value_counts(normalize=True)
check("tipo_assunto", "Tipo do ticket × assunto do ticket", f"p = {br(p_type_subject, 2)}",
      f"Sem associação detectável (V de Cramér {br(v_ts, 3)}). Tickets com assunto 'Refund request' estão classificados como 'Technical issue' em "
      f"{pct(refund['Technical issue'])} dos casos e como 'Refund request' em só {pct(refund['Refund request'])}.")

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
check("csat", "Modelo com TODAS as variáveis prevê a nota de satisfação com", f"{pct(model_acc, 1)} de acerto",
      f"Chutar sempre a nota mais comum acerta {pct(dummy_acc, 1)}; chutar ao acaso, 20%. Nenhuma variável tem "
      f"associação significativa com a nota (menor p = {br(min(a['p'] for a in assoc), 2)}).")

# Poder estatístico: menor diferença de CSAT entre dois canais que teríamos detectado
n_per_channel = closed["Ticket Channel"].value_counts().min()
mde = 2.8 * closed["Customer Satisfaction Rating"].std() * np.sqrt(2 / n_per_channel)


# 11. O que uma análise ingênua reportaria — e quantas vezes o mesmo "achado" aparece em dados embaralhados
def worst_segment(frame, value_col, by, pick="max"):
    s = frame.groupby(by)[value_col].mean()
    return (s.idxmax(), s.max()) if pick == "max" else (s.idxmin(), s.min())


naive = []
combo, combo_val = worst_segment(closed, "ttr_h", SEGMENT)
null_combo = np.array([closed.assign(ttr_h=rng.permutation(closed["ttr_h"].values)).groupby(SEGMENT)["ttr_h"].mean().max()
                       for _ in range(N_PERMUTATIONS)])
naive.append({
    "afirmacao": f"O maior gargalo é {combo[0]} × prioridade {combo[1]} × {combo[2]}: {br(combo_val, 1)} h de resolução, "
                 f"contra {br(closed['ttr_h'].mean(), 1)} h na média.",
    "teste": f"Com os tempos embaralhados ao acaso, a pior das {closed.groupby(SEGMENT).ngroups} combinações chega a esse "
             f"valor em {pct(np.mean(null_combo >= combo_val))} das {br(N_PERMUTATIONS, 0)} simulações.",
    "p": np.mean(null_combo >= combo_val),
})
prod, prod_val = worst_segment(closed, "Customer Satisfaction Rating", "Product Purchased", pick="min")
null_prod = np.array([closed.assign(c=rng.permutation(closed["Customer Satisfaction Rating"].values))
                      .groupby("Product Purchased")["c"].mean().min() for _ in range(N_PERMUTATIONS)])
naive.append({
    "afirmacao": f"O produto com pior satisfação é {prod} (nota {br(prod_val, 2)}, contra "
                 f"{br(closed['Customer Satisfaction Rating'].mean(), 2)} na média). Priorizar esse produto.",
    "teste": f"Com as notas embaralhadas, o pior de {closed['Product Purchased'].nunique()} produtos fica igual ou abaixo "
             f"disso em {pct(np.mean(null_prod <= prod_val))} das simulações.",
    "p": np.mean(null_prod <= prod_val),
})
channel_median = closed.groupby("Ticket Channel")["ttr_h"].median()
p_channel = stats.kruskal(*[g["ttr_h"] for _, g in closed.groupby("Ticket Channel")]).pvalue
naive.append({
    "afirmacao": f"{channel_median.idxmin()} é o canal mais rápido (mediana de {br(channel_median.min(), 1)} h). "
                 f"Migrar volume para ele.",
    "teste": f"A mediana é negativa: o ticket seria resolvido antes de ser respondido. E a diferença entre canais não é "
             f"significativa (Kruskal-Wallis p = {br(p_channel, 2)}).",
    "p": p_channel,
})
for n in naive:
    print(" ingênuo:", n["afirmacao"], "|", n["teste"])

hist_counts, hist_edges = np.histogram(closed["ttr_h"], bins=np.arange(-24, 25, 2))
csat_by_channel = closed.groupby("Ticket Channel")["Customer Satisfaction Rating"].agg(["mean", "std", "count"])
csat_by_channel["ci95"] = 1.96 * csat_by_channel["std"] / np.sqrt(csat_by_channel["count"])

save_json("audit.json", {
    "linhas": len(df), "linhas_brief": 30000, "fechados": len(closed), "negativos": negative,
    "ttr_desvio_h": ttr_sd, "ttr_curtose": ttr_kurt, "emails_reservados": reserved,
    "checks": checks,
    "ingenuo": naive,
    "csat": {"modelo": model_acc, "classe_mais_comum": dummy_acc, "acaso": 0.2, "associacoes": assoc,
             "mde_canal": mde, "por_canal": csat_by_channel[["mean", "ci95", "count"]].reset_index().to_dict("records")},
    "ttr_hist": {"counts": hist_counts, "edges": hist_edges},
    "uniformidade": uniform,
})
print(f"MDE de CSAT entre canais (80% de poder): {br(mde, 2)} ponto")
