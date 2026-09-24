"""Population Stability Index (PSI) per feature: training frame vs scored batch.

Small arrays (thousands of rows), computed in pandas on the driver. The training distribution
is stored in ``training_manifest.json`` (``feature_distributions``) so ``score`` can compare
any later batch without re-reading the training data.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from lead_scorer.ml.features import CATEGORICAL_FEATURES, NUMERIC_FEATURES

PSI_ALERT = 0.2
_EPS = 1e-4
_N_BINS = 10


def feature_distribution(df: pd.DataFrame) -> dict[str, dict[str, Any]]:
    """Reference distribution: decile edges + proportions (numeric), category shares (categorical).

    Nulls are counted as their own bin (``null_share``) so a change in missingness is drift too.
    """
    out: dict[str, dict[str, Any]] = {}
    for col in NUMERIC_FEATURES:
        values = pd.to_numeric(df[col], errors="coerce")
        non_null = values.dropna().to_numpy(dtype=float)
        edges = (
            np.unique(np.quantile(non_null, np.linspace(0, 1, _N_BINS + 1)))
            if len(non_null)
            else np.array([0.0, 1.0])
        )
        if len(edges) < 2:
            edges = np.array([edges[0] - 0.5, edges[0] + 0.5])
        counts, _ = np.histogram(non_null, bins=edges)
        total = max(len(values), 1)
        out[col] = {
            "type": "numeric",
            "edges": [float(e) for e in edges],
            "shares": [float(c) / total for c in counts],
            "null_share": float(values.isna().sum()) / total,
            "mean": float(non_null.mean()) if len(non_null) else None,
        }
    for col in CATEGORICAL_FEATURES:
        shares = df[col].fillna("__null__").astype(str).value_counts(normalize=True)
        out[col] = {"type": "categorical", "shares": {str(k): float(v) for k, v in shares.items()}}
    return out


def _psi(expected: np.ndarray, actual: np.ndarray) -> float:
    e = np.clip(expected, _EPS, None)
    a = np.clip(actual, _EPS, None)
    return float(np.sum((a - e) * np.log(a / e)))


def psi_report(reference: dict[str, dict[str, Any]], batch: pd.DataFrame) -> dict[str, float]:
    """PSI of every feature in ``reference`` against ``batch`` (same binning as the reference)."""
    out: dict[str, float] = {}
    for col, ref in reference.items():
        if col not in batch.columns:
            continue
        if ref["type"] == "numeric":
            values = pd.to_numeric(batch[col], errors="coerce")
            non_null = values.dropna().to_numpy(dtype=float)
            edges = np.array(ref["edges"], dtype=float)
            edges[0], edges[-1] = -np.inf, np.inf  # tails: everything outside falls in the end bins
            counts, _ = np.histogram(non_null, bins=edges)
            total = max(len(values), 1)
            actual = np.append(counts / total, values.isna().sum() / total)
            expected = np.append(np.array(ref["shares"], dtype=float), ref["null_share"])
        else:
            shares = batch[col].fillna("__null__").astype(str).value_counts(normalize=True)
            keys = sorted(set(ref["shares"]) | set(shares.index))
            expected = np.array([ref["shares"].get(k, 0.0) for k in keys])
            actual = np.array([float(shares.get(k, 0.0)) for k in keys])
        out[col] = round(_psi(expected, actual), 6)
    return out


def psi_alerts(report: dict[str, float], threshold: float = PSI_ALERT) -> list[str]:
    return sorted(k for k, v in report.items() if v > threshold)


__all__ = ["PSI_ALERT", "feature_distribution", "psi_alerts", "psi_report"]
