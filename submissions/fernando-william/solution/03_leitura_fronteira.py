"""Leitura de tickets na fronteira entre classes. Só imprime; não comenta.

Parte 1: 30 tickets sorteados (semente 42) de HR Support, Administrative rights e Access.
Parte 2: mesmo split e mesmo baseline do script 01; 20 Administrative rights e 20 HR Support
previstos como Hardware no teste, com a probabilidade máxima prevista.
Saída em solution/03_leitura_fronteira.txt.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

SEED = 42
AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "data"
SAIDA = AQUI / "03_leitura_fronteira.txt"
N_AMOSTRA = 30
N_FRONTEIRA = 20
CLASSES_AMOSTRA = ["HR Support", "Administrative rights", "Access"]
CLASSE_PREVISTA = "Hardware"
CLASSES_REAIS = ["Administrative rights", "HR Support"]


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

tk = pd.read_csv(DADOS / "all_tickets_processed_improved_v3.csv")
doc = tk["Document"].fillna("")

print(f"=== PARTE 1: {N_AMOSTRA} tickets sorteados por classe (semente {SEED}) ===")
for classe in CLASSES_AMOSTRA:
    sub = tk[tk["Topic_group"] == classe].sample(N_AMOSTRA, random_state=SEED)
    print(f"\n--- {classe} ({len(sub)} de {(tk['Topic_group'] == classe).sum()}) ---")
    for idx, linha in sub.iterrows():
        print(f"\n[linha {idx}] rótulo: {linha['Topic_group']}")
        print(linha["Document"])

print(f"\n\n=== PARTE 2: previstos como {CLASSE_PREVISTA} no teste (split e baseline do script 01) ===")
X_tr, X_te, y_tr, y_te = train_test_split(
    doc, tk["Topic_group"], test_size=0.2, stratify=tk["Topic_group"], random_state=SEED)
vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2)
clf = LogisticRegression(max_iter=1000, random_state=SEED)
clf.fit(vec.fit_transform(X_tr), y_tr)
proba = clf.predict_proba(vec.transform(X_te))
pred = clf.classes_[proba.argmax(axis=1)]
teste = pd.DataFrame({
    "real": y_te.values,
    "previsto": pred,
    "prob_max": proba.max(axis=1),
    "texto": X_te.values,
}, index=X_te.index)

for real in CLASSES_REAIS:
    sel = teste[(teste["real"] == real) & (teste["previsto"] == CLASSE_PREVISTA)]
    mostrar = sel.sample(min(N_FRONTEIRA, len(sel)), random_state=SEED).sort_index()
    print(f"\n--- real {real}, previsto {CLASSE_PREVISTA}: {len(sel)} no teste, {len(mostrar)} listados ---")
    for idx, linha in mostrar.iterrows():
        print(f"\n[linha {idx}] real: {linha['real']}  previsto: {linha['previsto']}  "
              f"prob_max: {linha['prob_max']:.4f}")
        print(linha["texto"])

print(f"\nsaída gravada em {SAIDA.relative_to(AQUI.parent)}")
