from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


# -----------------------------------------------------------------------------
# DATASET 2 DIAGNOSTICS
# -----------------------------------------------------------------------------
class Dataset2Diagnostics:
    """Diagnostics for the provided IT classification corpus.

    The source file is kept read-only. This module only derives descriptive
    metrics about Topic_group and the text shape of Document. It intentionally
    does not infer ticket status because Dataset 2 has no status field.
    """

    REQUIRED_COLUMNS = {"Document", "Topic_group"}

    def __init__(self, raw_dir: Path):
        self.raw_dir = Path(raw_dir)

    def run(self) -> dict[str, Any]:
        source = self._find_source()
        if source is None:
            return {
                "status": "awaiting_data",
                "message": "Dataset 2 not found in data/raw/.",
            }

        df = pd.read_csv(source)
        documents = df["Document"].fillna("").astype(str)
        groups = self._topic_groups(df)
        quality = self._document_quality(documents)

        return {
            "status": "ready",
            "source": source.name,
            "rows": int(len(df)),
            "topic_groups": groups,
            "document_quality": quality,
            "status_availability": {
                "available": False,
                "reason": (
                    "Dataset 2 contains only Document and Topic_group; it has no Ticket Status field or shared customer/ticket key with Dataset 1. "
                    "Therefore, Open/Pending/Closed by Topic_group does not exist as observed data. A classifier may generate predicted categories for Dataset 1, "
                    "but those categories remain MODEL-DERIVED rather than ground truth."
                ),
            },
        }

    # -------------------------------------------------------------------------
    # SOURCE DISCOVERY
    # -------------------------------------------------------------------------
    def _find_source(self) -> Path | None:
        if not self.raw_dir.exists():
            return None
        for path in sorted(self.raw_dir.glob("*.csv")):
            try:
                columns = set(pd.read_csv(path, nrows=0).columns)
            except Exception:
                continue
            if self.REQUIRED_COLUMNS.issubset(columns):
                return path
        return None

    # -------------------------------------------------------------------------
    # TOPIC DISTRIBUTION
    # -------------------------------------------------------------------------
    @staticmethod
    def _topic_groups(df: pd.DataFrame) -> dict[str, Any]:
        counts = df["Topic_group"].fillna("(missing)").value_counts(dropna=False)
        total = int(len(df))
        rows = [
            {
                "label": str(label),
                "count": int(count),
                "pct": round((int(count) / total * 100) if total else 0.0, 2),
            }
            for label, count in counts.items()
        ]
        return {
            "count": int(len(rows)),
            "rows": rows,
            "largest": rows[0] if rows else None,
            "interpretation": (
                "This distribution describes only the labeled Dataset 2 corpus. It does not establish "
                "the operational distribution of the 8,469 Dataset 1 tickets until semantic validation is completed."
            ),
        }

    # -------------------------------------------------------------------------
    # DOCUMENT QUALITY
    # -------------------------------------------------------------------------
    @staticmethod
    def _document_quality(documents: pd.Series) -> dict[str, Any]:
        token_counts: list[int] = []
        unique_ratios: list[float] = []
        repeated_bigram_flags: list[bool] = []
        repeated_bigram_ratios: list[float] = []
        punctuation_flags: list[bool] = []
        lowercase_flags: list[bool] = []

        for text in documents:
            tokens = re.findall(r"\b\w+\b", text.lower())
            token_count = len(tokens)
            token_counts.append(token_count)
            unique_ratios.append((len(set(tokens)) / token_count) if token_count else 0.0)

            if token_count >= 2:
                bigrams = list(zip(tokens, tokens[1:]))
                unique_bigrams = len(set(bigrams))
                repetition = 1.0 - (unique_bigrams / len(bigrams))
                repeated_bigram_flags.append(unique_bigrams < len(bigrams))
                repeated_bigram_ratios.append(max(0.0, repetition))
            else:
                repeated_bigram_flags.append(False)
                repeated_bigram_ratios.append(0.0)

            punctuation_flags.append(bool(re.search(r"[^\w\s]", text)))
            letters = [ch for ch in text if ch.isalpha()]
            lowercase_flags.append(bool(letters) and all(not ch.isupper() for ch in letters))

        tc = np.asarray(token_counts, dtype=float)
        ur = np.asarray(unique_ratios, dtype=float)
        br = np.asarray(repeated_bigram_ratios, dtype=float)
        n = len(documents)

        return {
            "documents": int(n),
            "unique_documents": int(documents.nunique(dropna=False)),
            "exact_duplicate_documents": int(documents.duplicated().sum()),
            "token_count_mean": round(float(tc.mean()), 2) if n else 0.0,
            "token_count_median": round(float(np.median(tc)), 2) if n else 0.0,
            "token_count_p95": round(float(np.percentile(tc, 95)), 2) if n else 0.0,
            "mean_unique_token_ratio_pct": round(float(ur.mean() * 100), 2) if n else 0.0,
            "documents_with_repeated_bigrams": int(sum(repeated_bigram_flags)),
            "documents_with_repeated_bigrams_pct": round(sum(repeated_bigram_flags) / n * 100, 2) if n else 0.0,
            "mean_repeated_bigram_ratio_pct": round(float(br.mean() * 100), 2) if n else 0.0,
            "documents_with_punctuation_pct": round(sum(punctuation_flags) / n * 100, 2) if n else 0.0,
            "lowercase_only_pct": round(sum(lowercase_flags) / n * 100, 2) if n else 0.0,
            "interpretation": (
                "Document appears to be text already processed for NLP rather than a clean transcript of the original ticket. "
                "Internal term and n-gram repetition is measured as a corpus characteristic; the original source remains unchanged in the Explorer."
            ),
            "source_mutation_allowed": False,
        }
