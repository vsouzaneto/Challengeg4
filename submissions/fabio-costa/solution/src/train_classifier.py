"""Reproducible supervised benchmark for Dataset 2; never modifies source CSV."""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/raw/all_tickets_processed_improved_v3.csv"
OUTPUT = ROOT / "artifacts/training"
EXPECTED_SHA = "044fdace33fa564e1e60453f2941dafc95539c99878b0d32746950394b9dd4d4"
SEED = 42


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare():
    if digest(SOURCE) != EXPECTED_SHA:
        raise RuntimeError("DATASET_SHA_MISMATCH")

    data = pd.read_csv(SOURCE)
    if list(data.columns) != ["Document", "Topic_group"]:
        raise RuntimeError("DATASET_SCHEMA_MISMATCH")
    if data.isna().any().any():
        raise RuntimeError("DATASET_MISSING_VALUES")

    texts = data["Document"].astype(str).to_numpy()
    labels = data["Topic_group"].astype(str).to_numpy()

    # Documents sharing an identical normalized six-token prefix
    # must not cross train / validation / test boundaries.
    groups = np.array([
        " ".join(text.lower().split()[:6]) for text in texts
    ])
    all_classes = set(labels)

    outer = GroupShuffleSplit(
        n_splits=1, test_size=0.15, random_state=SEED
    )
    rest, test = next(outer.split(texts, labels, groups))

    inner = GroupShuffleSplit(
        n_splits=1, test_size=0.1764705882, random_state=SEED + 1
    )
    train_local, val_local = next(
        inner.split(texts[rest], labels[rest], groups[rest])
    )
    train, val = rest[train_local], rest[val_local]

    for idx in (train, val, test):
        if set(labels[idx]) != all_classes:
            raise RuntimeError("SPLIT_CLASS_COVERAGE_FAIL")

    group_sets = [set(groups[idx]) for idx in (train, val, test)]
    if any(group_sets[a] & group_sets[b] for a, b in ((0, 1), (0, 2), (1, 2))):
        raise RuntimeError("GROUP_LEAKAGE")

    return texts, labels, (train, val, test), len(set(groups))


def model(kind):
    classifier = (
        LinearSVC(random_state=SEED)
        if kind == "LinearSVC"
        else LogisticRegression(max_iter=300, random_state=SEED)
    )
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            lowercase=True, ngram_range=(1, 2),
            min_df=2, max_features=50000, dtype=np.float32,
            sublinear_tf=True
        )),
        ("classifier", classifier),
    ])


def main():
    texts, labels, splits, group_count = prepare()
    train, val, test = splits
    models = {}
    results = {}

    for kind in ("LinearSVC", "LogisticRegression"):
        estimator = model(kind)
        start = time.perf_counter()
        estimator.fit(texts[train], labels[train])
        train_seconds = time.perf_counter() - start

        start = time.perf_counter()
        val_pred = estimator.predict(texts[val])
        val_seconds = time.perf_counter() - start
        val_f1 = float(f1_score(labels[val], val_pred, average="macro"))

        results[kind] = {
            "validation_macro_f1": val_f1,
            "training_seconds": round(train_seconds, 3),
            "validation_inference_seconds": round(val_seconds, 3),
        }
        models[kind] = estimator
        print(f"{kind}: validation_macro_f1={val_f1:.5f}", flush=True)

    winner = max(results, key=lambda k: results[k]["validation_macro_f1"])
    chosen = models[winner]
    start = time.perf_counter()
    predictions = chosen.predict(texts[test])
    test_seconds = time.perf_counter() - start
    classes = sorted(set(labels))

    report = {
        "status": "evaluated",
        "source_sha256": EXPECTED_SHA,
        "source_rows": len(texts),
        "classes": classes,
        "grouping": "normalized first six tokens",
        "unique_prefix_groups": group_count,
        "split": {
            "train": len(train), "validation": len(val), "test": len(test)
        },
        "random_seed": SEED,
        "selection_metric": "validation_macro_f1",
        "models": results,
        "selected_model": winner,
        "test_macro_f1": float(
            f1_score(labels[test], predictions, average="macro")
        ),
        "test_inference_seconds": round(test_seconds, 3),
        "test_classification_report": classification_report(
            labels[test], predictions, labels=classes,
            output_dict=True, zero_division=0
        ),
        "test_confusion_matrix": confusion_matrix(
            labels[test], predictions, labels=classes
        ).tolist(),
        "limitations": [
            "Dataset 2 is independent of Dataset 1.",
            "Prefix grouping reduces but does not eliminate semantic leakage.",
            "Performance on Dataset 1 has not been established.",
            "No cost savings or staffing reductions have been measured.",
            "Test metrics are not confidence calibration."
        ],
    }

    if digest(SOURCE) != EXPECTED_SHA:
        raise RuntimeError("SOURCE_MUTATION_DETECTED")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT / "benchmark.json"
    model_path = OUTPUT / "selected_model.joblib"
    joblib.dump(chosen, model_path)
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print("SELECTED_MODEL=" + winner)
    print("TEST_MACRO_F1=" + str(round(report["test_macro_f1"], 5)))
    print("REPORT=" + str(report_path))
    print("MODEL=" + str(model_path))
    print("SOURCE_MUTATION=NONE")
    print("STATUS=PASS")


if __name__ == "__main__":
    main()
