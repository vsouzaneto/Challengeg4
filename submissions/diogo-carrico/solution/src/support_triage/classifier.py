"""Ticket classifier for Dataset 2: leakage-safe split, model choice, calibration and routing thresholds."""

from __future__ import annotations

import re
from itertools import pairwise

import numpy as np
import pandas as pd
from scipy import sparse
from scipy.sparse.csgraph import connected_components
from scipy.stats import norm
from sklearn.calibration import CalibratedClassifierCV
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.frozen import FrozenEstimator
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import normalize
from sklearn.svm import LinearSVC

SEED = 42
_NON_LETTERS = re.compile(r"[^a-z\s]+")
_SPACES = re.compile(r"\s+")


# ---------------------------------------------------------------- text


def normalize_text(text: str) -> str:
    """Bring raw ticket text to Dataset 2's form: lowercase, no digits or punctuation, single spaces."""
    text = _NON_LETTERS.sub(" ", str(text).lower())
    return _SPACES.sub(" ", text).strip()


def vocabulary_coverage(text: str, vocab: set[str]) -> float:
    """Share of the ticket's content words that the model saw in training.

    English stopwords are ignored: Dataset 2's preprocessing removed some of them ("my") and kept
    others ("for"), so they say nothing about whether a ticket belongs to the domain.
    A ticket with no content words gets 0 and goes to a person.
    """
    words = [w for w in normalize_text(text).split() if w not in ENGLISH_STOP_WORDS]
    return sum(w in vocab for w in words) / len(words) if words else 0.0


# ---------------------------------------------------------------- near duplicates and split


def near_duplicate_groups(
    texts: pd.Series, threshold: float = 0.9, chunk: int = 500
) -> np.ndarray:
    """Group documents whose TF-IDF cosine similarity is at least `threshold`.

    Candidates come from a 128-dimension SVD projection (cheap dense dot products); each
    candidate pair is then confirmed on the exact TF-IDF vectors.
    """
    tfidf = TfidfVectorizer(min_df=2, sublinear_tf=True).fit_transform(texts)
    dense = normalize(
        TruncatedSVD(n_components=128, random_state=SEED).fit_transform(tfidf)
    ).astype(np.float32)
    rows, cols = [], []
    for start in range(0, dense.shape[0], chunk):
        sims = dense[start : start + chunk] @ dense.T
        r, c = np.nonzero(sims >= threshold - 0.05)
        r = r + start
        keep = r < c
        rows.append(r[keep])
        cols.append(c[keep])
    r, c = np.concatenate(rows), np.concatenate(cols)
    exact = np.asarray(tfidf[r].multiply(tfidf[c]).sum(axis=1)).ravel()
    keep = exact >= threshold
    n = tfidf.shape[0]
    graph = sparse.coo_matrix((np.ones(keep.sum()), (r[keep], c[keep])), shape=(n, n))
    _, labels = connected_components(graph, directed=False)
    return labels


def split_indices(labels: pd.Series, groups: np.ndarray) -> dict[str, np.ndarray]:
    """70% train, 10% calibration, 10% threshold selection, 10% test; stratified, groups kept together."""
    folds = list(
        StratifiedGroupKFold(n_splits=10, shuffle=True, random_state=SEED).split(
            np.zeros(len(labels)), labels, groups
        )
    )
    test, val, cal = folds[0][1], folds[1][1], folds[2][1]
    used = np.concatenate([test, val, cal])
    train = np.setdiff1d(np.arange(len(labels)), used)
    return {"train": train, "calibration": cal, "validation": val, "test": test}


# ---------------------------------------------------------------- models


def candidate_models() -> dict[str, Pipeline]:
    def tfidf() -> TfidfVectorizer:
        return TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)

    models: dict[str, Pipeline] = {}
    for c in (1, 4, 16):
        models[f"tfidf_logreg_C{c}"] = Pipeline(
            [("tfidf", tfidf()), ("clf", LogisticRegression(C=c, max_iter=3000))]
        )
    for c in (0.25, 1.0):
        models[f"tfidf_linearsvc_C{c}"] = Pipeline(
            [("tfidf", tfidf()), ("clf", LinearSVC(C=c))]
        )
    for a in (0.1, 0.5):
        models[f"tfidf_complementnb_a{a}"] = Pipeline(
            [("tfidf", tfidf()), ("clf", ComplementNB(alpha=a))]
        )
    return models


def calibrate(
    model: Pipeline, x_cal: pd.Series, y_cal: pd.Series
) -> CalibratedClassifierCV:
    """Sigmoid calibration fitted on a split the model never trained on."""
    return CalibratedClassifierCV(FrozenEstimator(model), method="sigmoid").fit(
        x_cal, y_cal
    )


# ---------------------------------------------------------------- metrics


def wilson_interval(
    successes: int, total: int, confidence: float = 0.95
) -> tuple[float, float]:
    if total == 0:
        return (float("nan"), float("nan"))
    z = norm.ppf(1 - (1 - confidence) / 2)
    p = successes / total
    centre = (p + z**2 / (2 * total)) / (1 + z**2 / total)
    half = z * np.sqrt(p * (1 - p) / total + z**2 / (4 * total**2)) / (1 + z**2 / total)
    return (float(centre - half), float(centre + half))


def bootstrap_ci(
    y_true: np.ndarray, y_pred: np.ndarray, metric, n_boot: int = 1000
) -> tuple[float, float]:
    rng = np.random.default_rng(SEED)
    n = len(y_true)
    stats = [
        metric(y_true[idx], y_pred[idx])
        for idx in (rng.integers(0, n, n) for _ in range(n_boot))
    ]
    return (float(np.quantile(stats, 0.025)), float(np.quantile(stats, 0.975)))


def expected_calibration_error(
    confidence: np.ndarray, correct: np.ndarray, bins: int = 15
) -> float:
    edges = np.linspace(0, 1, bins + 1)
    ece = 0.0
    for lo, hi in pairwise(edges):
        mask = (confidence > lo) & (confidence <= hi)
        if mask.any():
            ece += mask.mean() * abs(correct[mask].mean() - confidence[mask].mean())
    return float(ece)


def classification_report(
    y_true: np.ndarray, y_pred: np.ndarray, classes: list[str]
) -> dict:
    p, r, f, s = precision_recall_fscore_support(
        y_true, y_pred, labels=classes, zero_division=0
    )
    macro = lambda a, b: f1_score(a, b, average="macro")
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "accuracy_ci95": bootstrap_ci(y_true, y_pred, accuracy_score),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro")),
        "macro_f1_ci95": bootstrap_ci(y_true, y_pred, macro),
        "per_class": {
            c: {
                "precision": float(p[i]),
                "recall": float(r[i]),
                "f1": float(f[i]),
                "support": int(s[i]),
            }
            for i, c in enumerate(classes)
        },
    }


# ---------------------------------------------------------------- thresholds


def coverage_at_threshold(
    confidence: np.ndarray, correct: np.ndarray, threshold: float
) -> dict:
    routed = confidence >= threshold
    k, n = int(correct[routed].sum()), int(routed.sum())
    return {
        "threshold": float(threshold),
        "coverage": float(routed.mean()),
        "routed": n,
        "precision": float(k / n) if n else float("nan"),
        "precision_ci95": wilson_interval(k, n),
    }


def threshold_for_precision(
    confidence: np.ndarray, correct: np.ndarray, target: float
) -> float:
    """Lowest threshold whose routed tickets reach the target precision, using the Wilson lower bound
    so the target holds with 95% confidence rather than only on average."""
    for t in np.round(np.arange(0.30, 1.0, 0.005), 3):
        routed = confidence >= t
        if (
            routed.sum() >= 30
            and wilson_interval(int(correct[routed].sum()), int(routed.sum()))[0]
            >= target
        ):
            return float(t)
    return 1.0


def per_class_thresholds(
    confidence: np.ndarray,
    predicted: np.ndarray,
    correct: np.ndarray,
    classes: list[str],
    target: float,
) -> dict[str, float]:
    """One threshold per predicted class, each meeting the target precision on its own Wilson lower bound.
    A class that cannot reach the target gets 1.0 (never auto-routed)."""
    return {
        c: threshold_for_precision(
            confidence[predicted == c], correct[predicted == c], target
        )
        for c in classes
    }


def route(
    confidence: np.ndarray, predicted: np.ndarray, thresholds: dict[str, float]
) -> np.ndarray:
    """True where the ticket is auto-routed: its confidence clears the threshold of its predicted class."""
    return confidence >= np.array([thresholds[p] for p in predicted])


def routed_quality(routed: np.ndarray, correct: np.ndarray) -> dict:
    k, n = int(correct[routed].sum()), int(routed.sum())
    return {
        "coverage": float(routed.mean()),
        "routed": n,
        "precision": float(k / n) if n else float("nan"),
        "precision_ci95": wilson_interval(k, n),
    }


def cost_threshold(triage_minutes: float, misroute_minutes: float) -> float:
    """Auto-route when the expected misroute cost is below the manual triage cost:
    (1 - p) * misroute_minutes < triage_minutes  =>  p > 1 - triage / misroute."""
    return float(max(0.0, 1 - triage_minutes / misroute_minutes))
