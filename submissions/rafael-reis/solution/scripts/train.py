"""Evaluate a real IT classifier on held-out text groups and persist its evidence."""
from __future__ import annotations

import json
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone

import joblib
import numpy as np
import sklearn
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.frozen import FrozenEstimator
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, log_loss
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from prepare_data import ARTIFACTS, SEED, canonical, load_catalog, write_json, write_predictions


def main() -> None:
    started = time.perf_counter()
    records = [r for r in load_catalog() if r["dataset_id"] == "ds2"]
    groups = defaultdict(list)
    for i, row in enumerate(records):
        groups[canonical(row["text"]).casefold()].append(i)
    keys = sorted(groups)
    group_labels = [Counter(records[i]["category"] for i in groups[key]).most_common(1)[0][0] for key in keys]
    train_keys, other_keys, _, other_labels = train_test_split(keys, group_labels, test_size=.30, random_state=SEED, stratify=group_labels)
    val_keys, test_keys = train_test_split(other_keys, test_size=.5, random_state=SEED, stratify=other_labels)
    indices = {name: np.array([i for key in selected for i in groups[key]]) for name, selected in [("train", train_keys), ("validation", val_keys), ("test", test_keys)]}
    assert not (set(train_keys) & set(val_keys) or set(train_keys) & set(test_keys) or set(val_keys) & set(test_keys))
    texts = np.array([r["text"] for r in records], dtype=object)
    labels = np.array([r["category"] for r in records], dtype=object)
    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_df=.995, max_features=60000, sublinear_tf=True, strip_accents="unicode")),
        ("classifier", LogisticRegression(C=4, max_iter=500, random_state=SEED)),
    ])
    model.fit(texts[indices["train"]], labels[indices["train"]])
    # Calibration learns exclusively from validation; test remains untouched until evaluation.
    calibrated = CalibratedClassifierCV(FrozenEstimator(model), method="sigmoid")
    calibrated.fit(texts[indices["validation"]], labels[indices["validation"]])
    test_texts, test_labels = texts[indices["test"]], labels[indices["test"]]
    infer_started = time.perf_counter()
    probabilities = calibrated.predict_proba(test_texts)
    elapsed = time.perf_counter() - infer_started
    classes = list(calibrated.classes_)
    predicted = np.array(classes)[probabilities.argmax(axis=1)]
    report = classification_report(test_labels, predicted, labels=classes, output_dict=True, zero_division=0)
    majority = Counter(labels[indices["train"]]).most_common(1)[0][0]
    baseline = np.repeat(majority, len(test_labels))
    confidence = probabilities.max(axis=1)
    calibration_bins = []
    for lo, hi in zip(np.arange(0, 1, .1), np.arange(.1, 1.1, .1)):
        mask = (confidence >= lo) & (confidence <= hi if hi >= 1 else confidence < hi)
        calibration_bins.append({"low": float(lo), "high": float(min(hi, 1)), "count": int(mask.sum()),
                                 "confidence": float(confidence[mask].mean()) if mask.any() else None,
                                 "accuracy": float((predicted[mask] == test_labels[mask]).mean()) if mask.any() else None})
    # This threshold is an explicit demo policy; it is not optimized on the test set.
    threshold = .75
    covered = confidence >= threshold
    metrics = {
        "model_version": "tfidf-logreg-calibrated-v1", "dataset_id": "ds2", "source": "model_evaluation",
        "created_at": datetime.now(timezone.utc).isoformat(), "seed": SEED, "sklearn_version": sklearn.__version__,
        "confidence_method": "sigmoid calibration fitted on validation, evaluated on untouched test",
        "split": {name: {"count": len(ix), "support": dict(Counter(labels[ix]))} for name, ix in indices.items()},
        "split_method": "70/15/15 stratified by normalized text group; whitespace+NFC+casefold; seed 42",
        "limitations": ["Similaridade aproximada entre partições não auditada; sem alegação de generalização para produção.", "Treino/teste apenas do domínio IT DS2; entradas PT-BR não têm benchmark rotulado."],
        "accuracy": float(accuracy_score(test_labels, predicted)), "macro_f1": float(f1_score(test_labels, predicted, average="macro")),
        "f1_by_category": {label: float(report[label]["f1-score"]) for label in classes},
        "classification_report": report, "classes": classes, "confusion_matrix": confusion_matrix(test_labels, predicted, labels=classes).tolist(),
        "support": {label: int(report[label]["support"]) for label in classes},
        "baseline": {"method": "majority class", "category": majority, "accuracy": float(accuracy_score(test_labels, baseline)), "macro_f1": float(f1_score(test_labels, baseline, average="macro"))},
        "calibration": {"method": "sigmoid", "bins": calibration_bins, "log_loss": float(log_loss(test_labels, probabilities, labels=classes)),
                        "multiclass_brier": float(np.mean(np.sum((probabilities - (test_labels[:, None] == np.array(classes)[None, :])) ** 2, axis=1)))},
        "policy": {"review_threshold": threshold, "status": "experimental", "reason": "Limiar demonstrativo fixado antes da avaliação; exige validação operacional."},
        "coverage_at_threshold": float(covered.mean()), "accuracy_above_threshold": float((predicted[covered] == test_labels[covered]).mean()) if covered.any() else None,
        "latency_ms_per_ticket_batched": elapsed / len(test_texts) * 1000,
        "training_seconds": time.perf_counter() - started,
    }
    bundle = {"pipeline": calibrated, "model_version": metrics["model_version"], "classes": classes,
              "confidence_method": metrics["confidence_method"], "review_threshold": threshold}
    joblib.dump(bundle, ARTIFACTS / "classifier.joblib")
    write_json(ARTIFACTS / "model_metrics.json", metrics)
    write_json(ARTIFACTS / "split_ids.json", {name: [records[i]["ticket_id"] for i in ix] for name, ix in indices.items()})
    all_probabilities = calibrated.predict_proba(texts)
    predictions = {row["ticket_id"]: {"predicted_category": classes[int(p.argmax())], "confidence": float(p.max()), "model_version": metrics["model_version"], "inference_mode": "precomputed"} for row, p in zip(records, all_probabilities)}
    write_predictions(predictions)
    manifest = json.loads((ARTIFACTS / "manifest.json").read_text())
    manifest["classifier"] = {"model_version": metrics["model_version"], "file": "classifier.joblib", "evaluation": "model_metrics.json", "sklearn_version": sklearn.__version__}
    write_json(ARTIFACTS / "manifest.json", manifest)
    print(json.dumps({key: metrics[key] for key in ["model_version", "accuracy", "macro_f1", "training_seconds"]}))


if __name__ == "__main__":
    main()
