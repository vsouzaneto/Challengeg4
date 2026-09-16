"""Auditoria dos dois datasets. Só imprime números com rótulo; não interpreta.

Saída em solution/01_auditoria_dados.txt. Semente 42 em tudo que sorteia.
"""

import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestNeighbors

SEED = 42
AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "data"
SAIDA = AQUI / "01_auditoria_dados.txt"
np.random.seed(SEED)

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 50)
pd.set_option("display.max_rows", 200)


class Tee:
    def __init__(self, caminho):
        self.arq = open(caminho, "w", encoding="utf-8")
        self.term = sys.stdout

    def write(self, s):
        self.arq.write(s)
        self.term.write(s)

    def flush(self):
        self.arq.flush()
        self.term.flush()


sys.stdout = Tee(SAIDA)


def secao(n, titulo):
    print(f"\n=== {n}. {titulo} ===")


def quantis(serie, qs=(0.05, 0.25, 0.5, 0.75, 0.95)):
    return {f"q{int(q*100)}": round(float(serie.quantile(q)), 2) for q in qs}


# ---------------------------------------------------------------- dataset 1
df = pd.read_csv(DADOS / "customer_support_tickets.csv")

secao(1, "customer_support_tickets.csv: dimensões e nulos")
print(f"linhas: {df.shape[0]}  colunas: {df.shape[1]}")
print("nulos por coluna:")
print(df.isna().sum().to_string())

secao(2, "nulos cruzados com Ticket Status")
for col in ["Customer Satisfaction Rating", "First Response Time", "Time to Resolution"]:
    print(f"\n{col} (True = nulo):")
    print(pd.crosstab(df["Ticket Status"], df[col].isna(), margins=True))

secao(3, "datas")
for col in ["Date of Purchase", "First Response Time", "Time to Resolution"]:
    conv = pd.to_datetime(df[col], errors="coerce")
    df[col + "_dt"] = conv
    nao_nulo = df[col].notna().sum()
    falhas = int(nao_nulo - conv.notna().sum())
    print(f"{col}: não nulos {nao_nulo}, falhas de parse {falhas}, "
          f"min {conv.min()}, max {conv.max()}, amplitude {conv.max() - conv.min()}")
fechados = df[df["Ticket Status"] == "Closed"]
ambos = fechados.dropna(subset=["First Response Time_dt", "Time to Resolution_dt"])
inv = (ambos["Time to Resolution_dt"] < ambos["First Response Time_dt"]).sum()
print(f"tickets Closed: {len(fechados)}; com as duas datas: {len(ambos)}; "
      f"Time to Resolution anterior a First Response Time: {inv} "
      f"(fração {inv/len(ambos):.4f})")
diff_h = (ambos["Time to Resolution_dt"] - ambos["First Response Time_dt"]).dt.total_seconds() / 3600
print(f"diferença (Time to Resolution - First Response Time) em horas, n={len(diff_h)}: {quantis(diff_h)}")

secao(4, "distribuições categóricas e qui-quadrado de uniformidade (Bonferroni)")
cats = ["Ticket Type", "Ticket Priority", "Ticket Channel", "Ticket Status",
        "Product Purchased", "Ticket Subject", "Customer Satisfaction Rating"]
n_testes = len(cats)
for col in cats:
    cont = df[col].value_counts(dropna=True)
    chi2, p = stats.chisquare(cont.values)
    print(f"\n{col}: {len(cont)} categorias, n={cont.sum()}, "
          f"chi2={chi2:.2f}, gl={len(cont)-1}, p={p:.4g}, p_bonferroni={min(1.0, p*n_testes):.4g}")
    print(cont.to_string())

secao(5, "tempos em horas por canal, prioridade e tipo (mediana e q90)")
print("definições: resolucao_h = Time to Resolution - First Response Time; "
      "primeira_resposta_h = First Response Time - Date of Purchase "
      "(não existe coluna de abertura do ticket)")
df["resolucao_h"] = (df["Time to Resolution_dt"] - df["First Response Time_dt"]).dt.total_seconds() / 3600
df["primeira_resposta_h"] = (df["First Response Time_dt"] - df["Date of Purchase_dt"]).dt.total_seconds() / 3600
for col in ["Ticket Channel", "Ticket Priority", "Ticket Type"]:
    g = df.groupby(col)[["primeira_resposta_h", "resolucao_h"]].agg(
        n_primeira=("primeira_resposta_h", "count"),
        primeira_mediana=("primeira_resposta_h", "median"),
        primeira_q90=("primeira_resposta_h", lambda s: s.quantile(0.9)),
        n_resolucao=("resolucao_h", "count"),
        resolucao_mediana=("resolucao_h", "median"),
        resolucao_q90=("resolucao_h", lambda s: s.quantile(0.9)),
    )
    print(f"\npor {col}:")
    print(g.round(2).to_string())

secao(6, "Customer Satisfaction Rating: ANOVA e correlações")
com_nota = df.dropna(subset=["Customer Satisfaction Rating"])
print(f"linhas com nota: {len(com_nota)}")
for col in ["Ticket Channel", "Ticket Priority", "Ticket Type", "Ticket Subject"]:
    grupos = [g["Customer Satisfaction Rating"].values for _, g in com_nota.groupby(col)]
    F, p = stats.f_oneway(*grupos)
    print(f"ANOVA nota ~ {col}: k={len(grupos)}, F={F:.4f}, p={p:.4g}")
sub = df[df["Ticket Status"] == "Closed"].dropna(subset=["Customer Satisfaction Rating", "resolucao_h"])
r_p, p_p = stats.pearsonr(sub["Customer Satisfaction Rating"], sub["resolucao_h"])
r_s, p_s = stats.spearmanr(sub["Customer Satisfaction Rating"], sub["resolucao_h"])
print(f"fechados com nota e resolucao_h: n={len(sub)}; "
      f"Pearson r={r_p:.4f} p={p_p:.4g}; Spearman rho={r_s:.4f} p={p_s:.4g}")

secao(7, "Ticket Description: placeholder e cardinalidade")
desc = df["Ticket Description"].fillna("")
tem_ph = desc.str.contains("{product_purchased}", regex=False)
print(f"linhas com '{{product_purchased}}' literal: {tem_ph.sum()} (fração {tem_ph.mean():.4f})")
desc_render = [d.replace("{product_purchased}", p) for d, p in zip(desc, df["Product Purchased"].fillna(""))]
df["desc_render"] = desc_render
print(f"textos distintos antes da substituição: {desc.nunique()}")
print(f"textos distintos depois da substituição: {pd.Series(desc_render).nunique()}")
primeira = desc.str.split(r"(?<=[.!?])\s", n=1, regex=True).str[0]
print(f"primeiras frases distintas (texto até o primeiro . ! ou ?): {primeira.nunique()}")
primeira_render = pd.Series(desc_render).str.split(r"(?<=[.!?])\s", n=1, regex=True).str[0]
print(f"primeiras frases distintas após substituição: {primeira_render.nunique()}")


def texto_prevê(textos, alvo, rotulo):
    X_tr, X_te, y_tr, y_te = train_test_split(
        textos, alvo, test_size=0.2, stratify=alvo, random_state=SEED)
    vec = TfidfVectorizer()
    clf = LogisticRegression(max_iter=1000, random_state=SEED)
    clf.fit(vec.fit_transform(X_tr), y_tr)
    acc = accuracy_score(y_te, clf.predict(vec.transform(X_te)))
    maj = y_tr.value_counts().idxmax()
    acc_maj = (y_te == maj).mean()
    print(f"{rotulo}: treino {len(X_tr)}, teste {len(X_te)}, classes {alvo.nunique()}, "
          f"acurácia teste {acc:.4f}, classe majoritária '{maj}' acurácia {acc_maj:.4f}")


secao(8, "texto prevê o rótulo? TF-IDF + regressão logística, split 80/20 estratificado")
texto_prevê(df["desc_render"], df["Ticket Type"], "alvo Ticket Type")
texto_prevê(df["desc_render"], df["Ticket Subject"], "alvo Ticket Subject")

secao(9, "Resolution")
res = df["Resolution"]
print(f"não nulos: {res.notna().sum()}, valores distintos: {res.nunique()}")
print("10 valores sorteados (semente 42):")
for v in res.dropna().sample(10, random_state=SEED):
    print(f"  - {v}")
print("nulos cruzados com Ticket Status (True = nulo):")
print(pd.crosstab(df["Ticket Status"], res.isna(), margins=True))

secao(10, "domínios de e-mail, top 10")
dom = df["Customer Email"].str.split("@").str[-1].str.lower()
print(f"domínios distintos: {dom.nunique()}")
print(dom.value_counts().head(10).to_string())

secao(11, "duplicatas")
print(f"linhas duplicadas exatas (todas as colunas): {df.duplicated().sum()}")
print(f"linhas duplicadas exatas ignorando Ticket ID: {df.drop(columns=['Ticket ID']).duplicated().sum()}")
dup_desc = desc.duplicated(keep=False)
print(f"linhas cuja Ticket Description se repete: {dup_desc.sum()}; "
      f"descrições repetidas distintas: {desc[dup_desc].nunique()}")
dup_render = pd.Series(desc_render).duplicated(keep=False)
print(f"idem após substituir placeholder: linhas {dup_render.sum()}, "
      f"distintas {pd.Series(desc_render)[dup_render].nunique()}")

secao(16, "placeholders entre chaves em Ticket Description")
padrao = re.compile(r"\{([^{}]+)\}")
cont_linhas = Counter()
for d in desc:
    for chave in set(padrao.findall(d)):
        cont_linhas[chave] += 1
colunas_norm = {re.sub(r"\s+", "_", c.strip().lower()): c for c in df.columns}
print(f"placeholders distintos: {len(cont_linhas)}")
for chave, n in cont_linhas.most_common():
    corresp = colunas_norm.get(chave.strip().lower())
    print(f"  {{{chave}}}: {n} linhas; coluna correspondente: {corresp if corresp else 'NENHUMA'}")

secao(17, "concentração das datas em 2023-06-01")
for col in ["First Response Time", "Time to Resolution"]:
    d = df[col + "_dt"].dropna()
    dias = d.dt.normalize()
    em_0601 = (dias == pd.Timestamp("2023-06-01")).sum()
    print(f"{col}: n={len(d)}, em 2023-06-01: {em_0601} (fração {em_0601/len(d):.4f}), "
          f"dias distintos: {dias.nunique()}")
    print("  contagem por dia:")
    print("  " + dias.value_counts().sort_index().to_string().replace("\n", "\n  "))

# ---------------------------------------------------------------- dataset 2
tk = pd.read_csv(DADOS / "all_tickets_processed_improved_v3.csv")

secao(12, "all_tickets_processed_improved_v3.csv: dimensões, nulos, classes")
print(f"linhas: {tk.shape[0]}  colunas: {tk.shape[1]}")
print("nulos por coluna:")
print(tk.isna().sum().to_string())
vc = tk["Topic_group"].value_counts()
print("Topic_group:")
print(pd.DataFrame({"n": vc, "pct": (100 * vc / len(tk)).round(2)}).to_string())
print(f"razão maior/menor classe: {vc.max()/vc.min():.2f}")

secao(13, "tamanho dos textos em palavras")
doc = tk["Document"].fillna("")
n_pal = doc.str.split().str.len()
print(f"n={len(n_pal)}, {quantis(n_pal)}, min {n_pal.min()}, max {n_pal.max()}")

secao(14, "duplicatas de Document")
dup_doc = doc.duplicated(keep=False)
print(f"linhas com Document repetido: {dup_doc.sum()}; documentos repetidos distintos: {doc[dup_doc].nunique()}; "
      f"linhas duplicadas exatas (Document + Topic_group): {tk.duplicated().sum()}")
amostra = doc.sample(5000, random_state=SEED)
vec_nn = TfidfVectorizer()
Xa = vec_nn.fit_transform(amostra)
nn = NearestNeighbors(n_neighbors=2, metric="cosine").fit(Xa)
dist, idx = nn.kneighbors(Xa)
sim = 1 - dist[:, 1]
acima = sim > 0.9
pares = {tuple(sorted((i, int(idx[i, 1])))) for i in np.where(acima)[0]}
exatos = sim > 0.9999
pares_exatos = {tuple(sorted((i, int(idx[i, 1])))) for i in np.where(exatos)[0]}
print(f"amostra de {Xa.shape[0]} documentos: com vizinho mais próximo de similaridade > 0,9: {acima.sum()} "
      f"(fração {acima.mean():.4f}); pares distintos: {len(pares)}; "
      f"desses, pares com similaridade > 0,9999: {len(pares_exatos)}")
print(f"similaridade com o vizinho mais próximo, quantis: {quantis(pd.Series(sim))}")

secao(15, "baseline TF-IDF (1-2gramas, min_df 2) + regressão logística prevendo Topic_group")
X_tr, X_te, y_tr, y_te = train_test_split(
    doc, tk["Topic_group"], test_size=0.2, stratify=tk["Topic_group"], random_state=SEED)
vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2)
Xtr = vec.fit_transform(X_tr)
Xte = vec.transform(X_te)
clf = LogisticRegression(max_iter=1000, random_state=SEED)
clf.fit(Xtr, y_tr)
pred = clf.predict(Xte)
maj = y_tr.value_counts().idxmax()
print(f"treino {len(X_tr)}, teste {len(X_te)}, vocabulário {len(vec.vocabulary_)}")
print(f"documentos do teste com Document idêntico presente no treino: {X_te.isin(set(X_tr)).sum()}")
print(f"acurácia global: {accuracy_score(y_te, pred):.4f}; "
      f"classe majoritária '{maj}': {(y_te == maj).mean():.4f}")
print(classification_report(y_te, pred, digits=4))
classes = list(clf.classes_)
cm = confusion_matrix(y_te, pred, labels=classes)
print("matriz de confusão (linhas = real, colunas = previsto):")
print(pd.DataFrame(cm, index=classes, columns=classes).to_string())

secao(18, "15 termos de maior coeficiente por classe (baseline do item 15)")
termos = np.array(vec.get_feature_names_out())
for i, c in enumerate(classes):
    top = np.argsort(clf.coef_[i])[::-1][:15]
    print(f"{c}: " + ", ".join(f"{termos[j]} ({clf.coef_[i][j]:.2f})" for j in top))

print(f"\nsaída gravada em {SAIDA.relative_to(AQUI.parent)}")
