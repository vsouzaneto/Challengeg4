"""
Classificador de tópicos — Dataset 2 (IT Service Ticket Classification, ~48k textos, 8 classes).

1. Split estratificado train / validation / test (70 / 15 / 15).
2. Compara approaches: TF-IDF + {Logistic Regression, Complement NB, Linear SVM}.
3. Calibra os thresholds do Confidence Gate no conjunto de validação
   (acurácia vs. cobertura) e reporta no teste.
4. Exporta o modelo vencedor para JSON (vocabulário, idf, coeficientes), que é
   executado em TypeScript dentro do app — sem Python em produção.
5. Exporta uma amostra do teste como golden set para o eval de paridade no app.

Uso:
    python train_classifier.py
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import ComplementNB
from sklearn.svm import LinearSVC

ROOT = Path(__file__).parent
D2 = ROOT / "data" / "all_tickets_processed_improved_v3.csv"
GEN = ROOT.parent / "app" / "data" / "generated"
SEED = 42

df = pd.read_csv(D2).dropna()
labels = sorted(df["Topic_group"].unique())

X_tmp, X_test, y_tmp, y_test = train_test_split(df["Document"], df["Topic_group"], test_size=0.15, random_state=SEED, stratify=df["Topic_group"])
X_train, X_val, y_train, y_val = train_test_split(X_tmp, y_tmp, test_size=0.15 / 0.85, random_state=SEED, stratify=y_tmp)
print("split", len(X_train), len(X_val), len(X_test))

# Tokenização padrão do sklearn (r"(?u)\b\w\w+\b", lowercase) — replicada em TS.
VEC_KW = dict(sublinear_tf=True, min_df=3, max_df=0.5, ngram_range=(1, 2), max_features=40000)

results = []
models = {}
for name, est in [
    ("TF-IDF + Logistic Regression", LogisticRegression(max_iter=3000, C=4.0)),
    ("TF-IDF + Complement Naive Bayes", ComplementNB(alpha=0.3)),
    ("TF-IDF + Linear SVM (calibrado)", CalibratedClassifierCV(LinearSVC(C=0.5), cv=3)),
]:
    vec = TfidfVectorizer(**VEC_KW)
    t0 = time.time()
    Xtr = vec.fit_transform(X_train)
    est.fit(Xtr, y_train)
    train_s = time.time() - t0
    pv = est.predict(vec.transform(X_val))
    results.append({
        "model": name,
        "val_accuracy": round(accuracy_score(y_val, pv) * 100, 2),
        "val_macro_f1": round(f1_score(y_val, pv, average="macro") * 100, 2),
        "train_seconds": round(train_s, 1),
    })
    models[name] = (vec, est)
    print(results[-1])

# Unigramas apenas (mais simples de portar) — vale a pena o bigrama?
vec_uni = TfidfVectorizer(**{**VEC_KW, "ngram_range": (1, 1)})
lr_uni = LogisticRegression(max_iter=3000, C=4.0).fit(vec_uni.fit_transform(X_train), y_train)
pv = lr_uni.predict(vec_uni.transform(X_val))
results.append({
    "model": "TF-IDF (só unigramas) + Logistic Regression",
    "val_accuracy": round(accuracy_score(y_val, pv) * 100, 2),
    "val_macro_f1": round(f1_score(y_val, pv, average="macro") * 100, 2),
    "train_seconds": None,
})
print(results[-1])

# Vencedor: LR (melhor trade-off entre qualidade, probabilidades calibradas e portabilidade).
WIN = "TF-IDF + Logistic Regression"
vec, lr = models[WIN]

# ---- Calibração do Confidence Gate no conjunto de VALIDAÇÃO ----
proba_val = lr.predict_proba(vec.transform(X_val))
conf_val = proba_val.max(1)
pred_val = lr.classes_[proba_val.argmax(1)]
calib = []
for t in np.arange(0.30, 0.96, 0.05):
    m = conf_val >= t
    calib.append({
        "threshold": round(float(t), 2),
        "coverage": round(float(m.mean()) * 100, 1),
        "accuracy": round(float((pred_val[m] == np.array(y_val)[m]).mean()) * 100, 1) if m.any() else None,
    })

# ---- Teste final ----
Xte = vec.transform(X_test)
proba = lr.predict_proba(Xte)
pred = lr.classes_[proba.argmax(1)]
conf = proba.max(1)
yt = np.array(y_test)
p, rcl, f1, sup = precision_recall_fscore_support(yt, pred, labels=labels)
cm = confusion_matrix(yt, pred, labels=labels)


def band(lo, hi):
    m = (conf >= lo) & (conf < hi)
    return {
        "coverage": round(float(m.mean()) * 100, 1),
        "accuracy": round(float((pred[m] == yt[m]).mean()) * 100, 1) if m.any() else None,
    }


metrics = {
    "dataset": {"rows": int(len(df)), "train": int(len(X_train)), "val": int(len(X_val)), "test": int(len(X_test)), "labels": labels,
                 "label_counts": df["Topic_group"].value_counts().to_dict()},
    "comparison": results,
    "winner": WIN,
    "test": {
        "accuracy": round(accuracy_score(yt, pred) * 100, 2),
        "macro_f1": round(f1_score(yt, pred, average="macro") * 100, 2),
        "weighted_f1": round(f1_score(yt, pred, average="weighted") * 100, 2),
        "per_class": [
            {"label": l, "precision": round(float(a) * 100, 1), "recall": round(float(b) * 100, 1), "f1": round(float(c) * 100, 1), "support": int(s)}
            for l, a, b, c, s in zip(labels, p, rcl, f1, sup)
        ],
        "confusion_matrix": cm.tolist(),
        "bands": {
            "auto (>=0.85)": band(0.85, 1.01),
            "assist (0.60-0.85)": band(0.60, 0.85),
            "human (<0.60)": band(0.0, 0.60),
        },
    },
    "calibration_val": calib,
    "vectorizer": {k: (list(v) if isinstance(v, tuple) else v) for k, v in VEC_KW.items()},
}

# ---- Exporta modelo para TS ----
vocab = vec.vocabulary_
terms = [None] * len(vocab)
for t, i in vocab.items():
    terms[i] = t
model_json = {
    "version": "tfidf-lr-v1",
    "classes": lr.classes_.tolist(),
    "terms": terms,
    "idf": [round(float(x), 4) for x in vec.idf_],
    "coef": [[round(float(x), 4) for x in row] for row in lr.coef_],
    "intercept": [round(float(x), 4) for x in lr.intercept_],
    "ngram_range": [1, 2],
    "sublinear_tf": True,
}

# Golden set de classificação: amostra estratificada do TESTE (nunca vista no treino).
gold = (
    pd.DataFrame({"text": X_test, "label": y_test})
    .groupby("label")
    .sample(n=60, random_state=SEED)
)
gold_idx = gold.index
gold_py = lr.classes_[lr.predict_proba(vec.transform(gold["text"])).argmax(1)]
golden = [{"text": t, "expected": l, "python_pred": pp} for t, l, pp in zip(gold["text"], gold["label"], gold_py)]

GEN.mkdir(parents=True, exist_ok=True)
(GEN / "classifier.json").write_text(json.dumps(model_json, separators=(",", ":")))
(GEN / "classifier_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2))
(GEN / "golden_classification.json").write_text(json.dumps(golden, ensure_ascii=False))
print(json.dumps(metrics["test"]["bands"], indent=1))
print("test acc", metrics["test"]["accuracy"], "macro f1", metrics["test"]["macro_f1"])
for row in metrics["test"]["per_class"]:
    print(row)
for c in calib:
    print(c)
print("model size MB", round((GEN / "classifier.json").stat().st_size / 1e6, 2))
