"""Data audit for both Challenge 002 datasets.

Every function returns plain dicts of numbers so the results can be written to JSON
and every figure in the README can be traced back to this module.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import make_pipeline

SEED = 42
PLACEHOLDER = "{product_purchased}"
RESERVED_EMAIL_DOMAINS = {"example.com", "example.net", "example.org"}  # RFC 2606

D1_CATEGORICALS = [
    "Ticket Type",
    "Ticket Priority",
    "Ticket Channel",
    "Ticket Status",
    "Customer Gender",
    "Product Purchased",
    "Ticket Subject",
]


# ---------------------------------------------------------------- helpers


def cramers_v(a: pd.Series, b: pd.Series) -> dict:
    """Association between two categorical variables, with the chi-square test behind it."""
    table = pd.crosstab(a, b)
    chi2, p, dof, _ = stats.chi2_contingency(table)
    n = table.to_numpy().sum()
    k = min(table.shape) - 1
    return {
        "cramers_v": float(np.sqrt(chi2 / (n * k))),
        "chi2": float(chi2),
        "dof": int(dof),
        "p_value": float(p),
        "n": int(n),
    }


def uniformity(counts: pd.Series) -> dict:
    """Chi-square goodness of fit against equal shares, plus the max/min share ratio."""
    chi2, p = stats.chisquare(counts.to_numpy())
    shares = counts / counts.sum()
    return {
        "n_categories": len(counts),
        "chi2_vs_uniform": float(chi2),
        "p_value_vs_uniform": float(p),
        "max_min_share_ratio": float(shares.max() / shares.min()),
        "shares": {
            str(k): round(float(v), 4)
            for k, v in shares.sort_values(ascending=False).items()
        },
    }


def spearman_with_permutation(
    x: np.ndarray, y: np.ndarray, n_perm: int = 10_000
) -> dict:
    """Spearman correlation with a two-sided permutation p-value (no distributional assumption)."""
    rho = stats.spearmanr(x, y).statistic
    rng = np.random.default_rng(SEED)
    rx = stats.rankdata(x)
    ry = stats.rankdata(y)
    rx = (rx - rx.mean()) / rx.std()
    null = np.empty(n_perm)
    for i in range(n_perm):
        yp = rng.permutation(ry)
        null[i] = np.mean(rx * (yp - yp.mean()) / yp.std())
    p = (np.sum(np.abs(null) >= abs(rho)) + 1) / (n_perm + 1)
    return {
        "rho": float(rho),
        "permutation_p_value": float(p),
        "null_95pct_band": [
            float(np.quantile(null, 0.025)),
            float(np.quantile(null, 0.975)),
        ],
        "n": len(x),
    }


def text_predicts_label(texts: pd.Series, labels: pd.Series) -> dict:
    """5-fold cross-validated TF-IDF + logistic regression: does the text carry signal about the label?"""
    model = make_pipeline(
        TfidfVectorizer(min_df=2, ngram_range=(1, 2), sublinear_tf=True),
        LogisticRegression(max_iter=2000),
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    scores = cross_validate(
        model, texts, labels, cv=cv, scoring=["accuracy", "f1_macro"]
    )
    majority = labels.value_counts(normalize=True).iloc[0]
    return {
        "accuracy_mean": float(scores["test_accuracy"].mean()),
        "accuracy_std": float(scores["test_accuracy"].std()),
        "macro_f1_mean": float(scores["test_f1_macro"].mean()),
        "majority_class_share": float(majority),
        "chance_uniform": float(1 / labels.nunique()),
        "n_classes": int(labels.nunique()),
    }


# ---------------------------------------------------------------- Dataset 1


def load_d1(path) -> pd.DataFrame:
    return pd.read_csv(path)


def audit_d1(path) -> dict:
    raw = Path(path).read_bytes()
    df = load_d1(path)
    out: dict = {}

    out["counts"] = {
        "bytes": len(raw),
        "physical_lines": raw.count(b"\n"),
        "blank_physical_lines": sum(1 for line in raw.split(b"\n") if not line.strip()),
        "parsed_records": len(df),
        "unique_ticket_ids": int(df["Ticket ID"].nunique()),
        "exact_duplicate_rows": int(df.duplicated().sum()),
        "duplicate_rows_ignoring_id": int(
            df.drop(columns="Ticket ID").duplicated().sum()
        ),
        "records_with_line_breaks_in_description": int(
            df["Ticket Description"].str.contains("\n", regex=False).sum()
        ),
    }

    out["missing_by_column"] = {c: int(v) for c, v in df.isna().sum().items() if v}
    out["missing_by_status"] = {
        status: {c: int(v) for c, v in g.isna().sum().items() if v}
        for status, g in df.groupby("Ticket Status")
    }

    out["categoricals"] = {c: uniformity(df[c].value_counts()) for c in D1_CATEGORICALS}

    # Ages are whole numbers, so test them as categories (a KS test is invalid with this many ties).
    ages = df["Customer Age"]
    age_counts = ages.value_counts().reindex(
        range(ages.min(), ages.max() + 1), fill_value=0
    )
    age_fit = uniformity(age_counts)
    out["age"] = {
        "min": int(ages.min()),
        "max": int(ages.max()),
        "mean": float(ages.mean()),
        "distinct_values": age_fit["n_categories"],
        "p_value_vs_uniform": age_fit["p_value_vs_uniform"],
        "max_min_share_ratio": age_fit["max_min_share_ratio"],
    }

    domains = df["Customer Email"].str.split("@").str[1].str.lower()
    out["emails"] = {
        "share_reserved_example_domains": float(
            domains.isin(RESERVED_EMAIL_DOMAINS).mean()
        ),
        "top_domains": {k: int(v) for k, v in domains.value_counts().head(5).items()},
        "unique_names_share": float(df["Customer Name"].nunique() / len(df)),
    }

    desc = df["Ticket Description"].fillna("")
    sentences = Counter(
        s.strip() for d in desc for s in re.split(r"(?<=[.!?])\s+|\n+", d) if s.strip()
    )
    out["description_text"] = {
        "share_with_placeholder": float(
            desc.str.contains(PLACEHOLDER, regex=False).mean()
        ),
        "other_curly_placeholders": sorted(
            {m for d in desc for m in re.findall(r"\{[a-z_]+\}", d)} - {PLACEHOLDER}
        ),
        "share_mentioning_actual_product": float(
            np.mean([p in d for p, d in zip(df["Product Purchased"], desc)])
        ),
        "unique_descriptions": int(desc.nunique()),
        "top_sentences": [
            {"sentence": s[:120], "count": c} for s, c in sentences.most_common(5)
        ],
    }

    res = df["Resolution"].dropna()
    rng = np.random.default_rng(SEED)
    out["resolution_text"] = {
        "present": len(res),
        "unique": int(res.nunique()),
        "mean_words": float(res.str.split().str.len().mean()),
        "random_examples": [
            res.iloc[i] for i in rng.choice(len(res), size=5, replace=False)
        ],
    }

    purchase = pd.to_datetime(df["Date of Purchase"])
    frt = pd.to_datetime(df["First Response Time"])
    ttr = pd.to_datetime(df["Time to Resolution"])
    all_ts = pd.concat([frt.dropna(), ttr.dropna()])
    closed = df["Ticket Status"].eq("Closed")
    both = closed & frt.notna() & ttr.notna()
    hours = (ttr - frt).dt.total_seconds() / 3600
    out["timestamps"] = {
        "purchase_range": [str(purchase.min().date()), str(purchase.max().date())],
        "response_and_resolution_range": [str(all_ts.min()), str(all_ts.max())],
        "response_and_resolution_span_hours": float(
            (all_ts.max() - all_ts.min()).total_seconds() / 3600
        ),
        "closed_with_both_timestamps": int(both.sum()),
        "share_resolution_before_first_response": float((hours[both] < 0).mean()),
        "resolution_minus_response_hours": {
            "min": float(hours[both].min()),
            "median": float(hours[both].median()),
            "max": float(hours[both].max()),
        },
        "first_response_present_by_status": {
            s: int(g.notna().sum()) for s, g in frt.groupby(df["Ticket Status"])
        },
    }

    csat = df["Customer Satisfaction Rating"]
    valid = both & csat.notna()
    nonneg = valid & (hours >= 0)
    out["csat"] = {
        "present": int(csat.notna().sum()),
        "present_only_when_closed": bool(
            csat.notna().equals(closed) or (csat.notna() <= closed).all()
        ),
        "distribution": uniformity(
            csat.dropna().astype(int).value_counts().sort_index()
        ),
        "spearman_resolution_hours_vs_csat_all_valid_pairs": spearman_with_permutation(
            hours[valid].to_numpy(), csat[valid].to_numpy()
        ),
        "spearman_resolution_hours_vs_csat_nonnegative_only": spearman_with_permutation(
            hours[nonneg].to_numpy(), csat[nonneg].to_numpy()
        ),
    }

    out["associations"] = {
        "subject_vs_type": cramers_v(df["Ticket Subject"], df["Ticket Type"]),
        "type_vs_priority": cramers_v(df["Ticket Type"], df["Ticket Priority"]),
        "channel_vs_priority": cramers_v(df["Ticket Channel"], df["Ticket Priority"]),
        "channel_vs_type": cramers_v(df["Ticket Channel"], df["Ticket Type"]),
        "product_vs_subject": cramers_v(df["Product Purchased"], df["Ticket Subject"]),
    }

    out["text_signal"] = {
        "description_predicts_type": text_predicts_label(desc, df["Ticket Type"]),
        "description_predicts_subject": text_predicts_label(desc, df["Ticket Subject"]),
        "description_predicts_priority": text_predicts_label(
            desc, df["Ticket Priority"]
        ),
    }
    return out


# ---------------------------------------------------------------- Dataset 2


def audit_d2(path) -> dict:
    df = pd.read_csv(path)
    doc = df["Document"].fillna("")
    label = df["Topic_group"]
    tokens = doc.str.split()
    n_tokens = tokens.str.len()
    all_tokens = [t for ts in tokens for t in ts]
    vocab = Counter(all_tokens)

    dup = df[doc.duplicated(keep=False)]
    groups = dup.groupby("Document")["Topic_group"].nunique()
    conflicting_docs = groups[groups > 1].index
    out: dict = {
        "counts": {
            "rows": len(df),
            "empty_documents": int((doc.str.strip() == "").sum()),
            "documents_under_5_tokens": int((n_tokens < 5).sum()),
            "exact_duplicate_rows": int(df.duplicated().sum()),
            "documents_appearing_more_than_once": int(dup["Document"].nunique()),
            "rows_in_duplicate_groups": len(dup),
            "duplicate_texts_with_conflicting_labels": len(conflicting_docs),
            "rows_in_conflicting_groups": int(
                df["Document"].isin(conflicting_docs).sum()
            ),
        },
        "classes": uniformity(label.value_counts()),
        "tokens_per_document": {
            "min": int(n_tokens.min()),
            "median": float(n_tokens.median()),
            "p95": float(n_tokens.quantile(0.95)),
            "max": int(n_tokens.max()),
        },
        "text_form": {
            "vocabulary_size": len(vocab),
            "share_lowercase_only": float((doc == doc.str.lower()).mean()),
            "share_tokens_that_are_english_stopwords": float(
                sum(vocab[w] for w in ENGLISH_STOP_WORDS if w in vocab)
                / max(len(all_tokens), 1)
            ),
            "share_documents_with_digits": float(doc.str.contains(r"\d").mean()),
            "share_documents_with_punctuation": float(
                doc.str.contains(r"[.,;:!?]").mean()
            ),
            "most_common_tokens": [w for w, _ in vocab.most_common(15)],
        },
    }
    return out
