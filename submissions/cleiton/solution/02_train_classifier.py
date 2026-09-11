"""Trains a ticket classifier on Dataset 2 (IT Service Ticket Classification,
~47.8k labelled tickets, 8 categories) and exports the fitted TF-IDF vocabulary
+ Logistic Regression weights as JSON so the dashboard artifact can run
inference **entirely client-side in the browser** — no backend needed for the
live demo, and no risk of the "3 cherry-picked examples" trap: anyone can
paste arbitrary text and get a real prediction from the real model.

Model choice: TF-IDF (unigrams+bigrams, capped vocabulary) + multinomial
Logistic Regression. Not the most exotic option available (transformer
embeddings would likely add a few points of accuracy) but it is the right
choice for this prototype: fully auditable coefficients, sub-millisecond
inference, ~600KB exported weights, zero inference cost, and it re-implements
exactly in ~40 lines of vanilla JS with no numerical surprises. A director
who asks "why did it say Hardware?" can be shown the exact word weights.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

DATA_PATH = Path(__file__).resolve().parents[3] / "datasets" / "it_ticket_classification.csv"
OUT_DIR = Path(__file__).resolve().parent / "output"
WEIGHTS_PATH = OUT_DIR / "model_weights.json"
METRICS_PATH = OUT_DIR / "classifier_metrics.json"

MAX_FEATURES = 3000
CONFIDENCE_THRESHOLD = 0.60  # below this, the prototype recommends human triage
RANDOM_STATE = 42


def main() -> None:
    df = pd.read_csv(DATA_PATH).dropna(subset=["Document", "Topic_group"])
    X_text, y = df["Document"], df["Topic_group"]

    X_train, X_test, y_train, y_test = train_test_split(
        X_text, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    vectorizer = TfidfVectorizer(
        max_features=MAX_FEATURES,
        ngram_range=(1, 2),
        min_df=3,
        sublinear_tf=True,
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    clf = LogisticRegression(
        max_iter=2000,
        C=5.0,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )
    clf.fit(X_train_vec, y_train)

    y_pred = clf.predict(X_test_vec)
    proba = clf.predict_proba(X_test_vec)
    confidence = proba.max(axis=1)
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    accuracy = report["accuracy"]
    macro_f1 = report["macro avg"]["f1-score"]

    covered = confidence >= CONFIDENCE_THRESHOLD
    coverage = float(covered.mean())
    accuracy_when_covered = float((y_pred[covered] == y_test.to_numpy()[covered]).mean()) if covered.sum() else 0.0
    accuracy_when_not_covered = float((y_pred[~covered] == y_test.to_numpy()[~covered]).mean()) if (~covered).sum() else 0.0

    labels = list(clf.classes_)
    cm = confusion_matrix(y_test, y_pred, labels=labels).tolist()

    metrics = {
        "model": "TF-IDF (unigrams+bigrams, max 3000 features) + multinomial Logistic Regression",
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "accuracy": round(accuracy, 4),
        "macro_f1": round(macro_f1, 4),
        "per_class": {
            label: {
                "precision": round(report[label]["precision"], 3),
                "recall": round(report[label]["recall"], 3),
                "f1": round(report[label]["f1-score"], 3),
                "support": int(report[label]["support"]),
            }
            for label in labels
        },
        "confusion_matrix": {"labels": labels, "matrix": cm},
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "coverage_at_threshold": round(coverage, 4),
        "accuracy_when_confidence_above_threshold": round(accuracy_when_covered, 4),
        "accuracy_when_confidence_below_threshold": round(accuracy_when_not_covered, 4),
        "class_distribution_train": y_train.value_counts().to_dict(),
        "interpretation": (
            f"Acurácia geral de {accuracy:.1%} num holdout estratificado de "
            f"{len(X_test):,} tickets nunca vistos no treino. Mais importante para "
            f"produção: ao só auto-rotear quando a confiança do modelo é >= "
            f"{CONFIDENCE_THRESHOLD:.0%}, isso cobre {coverage:.1%} dos tickets e "
            f"acerta {accuracy_when_covered:.1%} deles — a fatia coberta é "
            f"significativamente mais confiável que a média geral. É esse número "
            f"(coverage x accuracy_when_covered), não a acurácia bruta, que deveria "
            f"virar a política de auto-roteamento e a base do cálculo de ROI."
        ),
    }

    # --- Export weights for client-side (browser JS) inference ---------------
    vocab = vectorizer.vocabulary_  # term -> index
    idf = vectorizer.idf_
    terms_sorted = sorted(vocab.items(), key=lambda kv: kv[1])
    terms = [t for t, _ in terms_sorted]
    idf_sorted = [round(float(idf[i]), 6) for _, i in terms_sorted]

    coef = clf.coef_  # (n_classes, n_features)
    intercept = clf.intercept_

    weights_payload = {
        "vocab_terms": terms,
        "idf": idf_sorted,
        "ngram_range": [1, 2],
        "classes": labels,
        "coef": [[round(float(x), 6) for x in row] for row in coef],
        "intercept": [round(float(x), 6) for x in intercept],
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "notes": (
            "Reimplemente o pipeline sklearn TfidfVectorizer(sublinear_tf=True, "
            "norm='l2') + LogisticRegression.decision_function + softmax. "
            "Tokenização: minúsculas, regex \\b\\w\\w+\\b, unigramas e bigramas "
            "adjacentes, restrito a vocab_terms."
        ),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    WEIGHTS_PATH.write_text(json.dumps(weights_payload, ensure_ascii=False), encoding="utf-8")
    METRICS_PATH.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {WEIGHTS_PATH} ({WEIGHTS_PATH.stat().st_size / 1024:.1f} KB)")
    print(f"Wrote {METRICS_PATH}")
    print(f"Accuracy: {accuracy:.1%} | Macro F1: {macro_f1:.3f}")
    print(f"Coverage @ {CONFIDENCE_THRESHOLD:.0%} confidence: {coverage:.1%}, accuracy when covered: {accuracy_when_covered:.1%}")


if __name__ == "__main__":
    main()
