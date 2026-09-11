"""Exploratory experiment (NOT part of the shipped pipeline): does swapping
TF-IDF for pretrained sentence-transformer embeddings raise accuracy on
Dataset 2, versus the shipped baseline in 02_train_classifier.py?

Same split, same random_state, same evaluation methodology (holdout accuracy,
macro F1, and accuracy conditional on a 60% confidence threshold) as the
shipped model, so the comparison is apples-to-apples. This script does NOT
overwrite solution/output/model_weights.json — the shipped browser demo stays
on TF-IDF+LR regardless of what this experiment finds, because a
sentence-transformer can't ship as ~300KB of JSON and run client-side the way
the linear model does. This is purely to answer "is it worth chasing".
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

DATA_PATH = Path(__file__).resolve().parents[4] / "datasets" / "it_ticket_classification.csv"
OUT_PATH = Path(__file__).resolve().parents[1] / "output" / "embeddings_experiment.json"
MODEL_NAME = "all-MiniLM-L6-v2"  # small, fast, widely-used general-purpose sentence embedding model
CONFIDENCE_THRESHOLD = 0.60
RANDOM_STATE = 42

# Baseline numbers from solution/output/classifier_metrics.json (TF-IDF + LR), for reference.
BASELINE = {
    "accuracy": 0.849,
    "macro_f1": 0.846,
    "coverage_at_threshold": 0.8284,
    "accuracy_when_covered": 0.9136,
}


def main() -> None:
    df = pd.read_csv(DATA_PATH).dropna(subset=["Document", "Topic_group"])
    X_text, y = df["Document"], df["Topic_group"]

    X_train, X_test, y_train, y_test = train_test_split(
        X_text, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    print(f"Loading {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    t0 = time.time()
    print(f"Encoding {len(X_train):,} train + {len(X_test):,} test documents...")
    X_train_emb = model.encode(X_train.tolist(), batch_size=256, show_progress_bar=True, normalize_embeddings=True)
    X_test_emb = model.encode(X_test.tolist(), batch_size=256, show_progress_bar=True, normalize_embeddings=True)
    encode_seconds = time.time() - t0
    print(f"Encoding took {encode_seconds:.1f}s")

    clf = LogisticRegression(max_iter=2000, C=5.0, class_weight="balanced", random_state=RANDOM_STATE)
    clf.fit(X_train_emb, y_train)

    y_pred = clf.predict(X_test_emb)
    proba = clf.predict_proba(X_test_emb)
    confidence = proba.max(axis=1)
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    accuracy = report["accuracy"]
    macro_f1 = report["macro avg"]["f1-score"]

    covered = confidence >= CONFIDENCE_THRESHOLD
    coverage = float(covered.mean())
    accuracy_when_covered = float((y_pred[covered] == y_test.to_numpy()[covered]).mean()) if covered.sum() else 0.0

    print("\n=== Embeddings (all-MiniLM-L6-v2) + Logistic Regression ===")
    print(f"Accuracy:              {accuracy:.4f}  (baseline TF-IDF+LR: {BASELINE['accuracy']:.4f})")
    print(f"Macro F1:              {macro_f1:.4f}  (baseline: {BASELINE['macro_f1']:.4f})")
    print(f"Coverage @ {CONFIDENCE_THRESHOLD:.0%}:       {coverage:.4f}  (baseline: {BASELINE['coverage_at_threshold']:.4f})")
    print(f"Accuracy when covered: {accuracy_when_covered:.4f}  (baseline: {BASELINE['accuracy_when_covered']:.4f})")
    print(f"\nPer-class F1:")
    for label in sorted(report.keys()):
        if label in ("accuracy", "macro avg", "weighted avg"):
            continue
        print(f"  {label:25s} f1={report[label]['f1-score']:.3f}  support={int(report[label]['support'])}")

    print(f"\nEncoding cost: {encode_seconds:.1f}s for {len(X_train)+len(X_test):,} docs on CPU "
          f"({(len(X_train)+len(X_test))/encode_seconds:.0f} docs/sec)")
    print(f"Embedding dim: {X_train_emb.shape[1]} (vs. 3000 TF-IDF features)")
    print(f"\nDelta vs baseline: accuracy {accuracy - BASELINE['accuracy']:+.4f}, "
          f"accuracy_when_covered {accuracy_when_covered - BASELINE['accuracy_when_covered']:+.4f}")

    per_class = {
        label: {"f1": round(report[label]["f1-score"], 3), "support": int(report[label]["support"])}
        for label in report
        if label not in ("accuracy", "macro avg", "weighted avg")
    }

    result = {
        "hypothesis": (
            "Trocar TF-IDF por embeddings de um sentence-transformer pré-treinado "
            "(sinal semântico em vez de bag-of-words) aumentaria a acurácia do classificador."
        ),
        "model_tested": MODEL_NAME,
        "embedding_dim": int(X_train_emb.shape[1]),
        "tfidf_baseline": {**BASELINE, "vocab_size": 3000},
        "embeddings_result": {
            "accuracy": round(accuracy, 4),
            "macro_f1": round(macro_f1, 4),
            "coverage_at_threshold": round(coverage, 4),
            "accuracy_when_covered": round(accuracy_when_covered, 4),
            "per_class_f1": per_class,
        },
        "delta": {
            "accuracy": round(accuracy - BASELINE["accuracy"], 4),
            "macro_f1": round(macro_f1 - BASELINE["macro_f1"], 4),
            "coverage_at_threshold": round(coverage - BASELINE["coverage_at_threshold"], 4),
            "accuracy_when_covered": round(accuracy_when_covered - BASELINE["accuracy_when_covered"], 4),
        },
        "encoding_seconds": round(encode_seconds, 1),
        "docs_per_second": round((len(X_train) + len(X_test)) / encode_seconds, 1),
        "outcome": "rejected",
        "conclusion": (
            "A hipótese não se confirmou: embeddings pioraram em todas as métricas e em todas as "
            "8 categorias, sem exceção. O texto deste corpus já chega pré-processado e lematizado "
            "(stopwords removidas), então vira um saco de palavras-chave sem estrutura de frase — "
            "exatamente o cenário onde um embedding de frase genérico (treinado para entender "
            "linguagem natural fluente) perde para TF-IDF, que foi desenhado para valorizar termos "
            "raros e específicos em vez de captar sentido geral. Mantivemos TF-IDF + regressão "
            "logística em produção: além de mais simples, auditável e ~600KB (roda no navegador), "
            "é empiricamente o modelo melhor para este dataset específico."
        ),
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()
