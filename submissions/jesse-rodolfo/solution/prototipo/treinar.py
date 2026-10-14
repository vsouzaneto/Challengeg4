"""Treina o classificador de tickets no dataset 2 e mede no held-out.
Rodar da raiz da submissao: .venv/bin/python -I solution/prototipo/treinar.py
"""
import re
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline

RAIZ = Path(__file__).resolve().parents[1]
CSV = RAIZ / "data" / "raw" / "all_tickets_processed_improved_v3.csv"
MODELO = Path(__file__).resolve().parent / "modelo.joblib"
SEED = 42
LIMIARES = [0.5, 0.6, 0.7, 0.8, 0.9]
RESIDUO = re.compile(r"\b(?:thanks?|regards|best|annual leave)\b")


def limpar(texto: str) -> str:
    """Remove resíduo de assinatura e normaliza espaços."""
    return re.sub(r"\s+", " ", RESIDUO.sub(" ", str(texto).lower())).strip()


def novo_pipeline():
    return make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), min_df=3),
        LogisticRegression(max_iter=1000, random_state=SEED),
    )


def treinar_e_salvar(verbose=True):
    df = pd.read_csv(CSV)
    X = df["Document"].map(limpar)
    y = df["Topic_group"]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEED)
    modelo = novo_pipeline().fit(X_tr, y_tr)
    joblib.dump(modelo, MODELO)

    if verbose:
        proba = modelo.predict_proba(X_te)
        pred = modelo.classes_[proba.argmax(axis=1)]
        conf = proba.max(axis=1)
        acc = (pred == y_te.values).mean()
        maj = y_te.value_counts(normalize=True)
        print(f"treino={len(X_tr)} held-out={len(X_te)} | seed={SEED}")
        print(f"acurácia held-out: {acc:.4f}")
        print(f"classe majoritária ({maj.index[0]}): {maj.iloc[0]:.4f}")
        print("\nmatriz de confusão (linhas=real, colunas=previsto):")
        print(pd.DataFrame(confusion_matrix(y_te, pred, labels=modelo.classes_),
                           index=modelo.classes_, columns=modelo.classes_).to_string())
        print("\nlimiar | cobertura (% aceitos) | acurácia só nos aceitos | aceitos")
        for t in LIMIARES:
            m = conf >= t
            a = (pred[m] == y_te.values[m]).mean() if m.any() else float("nan")
            print(f"{t:.1f}    | {m.mean()*100:6.1f}%               | {a*100:6.1f}%                  | {m.sum()}")
    return modelo


if __name__ == "__main__":
    treinar_e_salvar()
