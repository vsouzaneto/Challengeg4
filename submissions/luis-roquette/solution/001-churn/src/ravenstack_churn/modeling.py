import json
import warnings
from hashlib import sha256
from math import ceil
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from .config import MIN_SEGMENT_ACCOUNTS, RANDOM_SEED, SCORING_CUTOFF

MODEL_FEATURES = (
    "mrr_active",
    "seats",
    "tenure_days",
    "days_to_annual_renewal",
    "usage_count_30d",
    "usage_change_30_vs_90",
    "error_rate_30d",
    "feature_breadth_30d",
    "tickets_30d",
    "ticket_change_30_vs_90",
    "escalations_90d",
    "mean_satisfaction_90d",
    "downgrade_90d",
    "auto_renew_off",
    "industry",
    "country",
    "referral_source",
    "plan_tier",
    "billing_frequency",
    "is_trial",
)

CATEGORICAL_FEATURES = (
    "industry",
    "country",
    "referral_source",
    "plan_tier",
    "billing_frequency",
)
NUMERIC_FEATURES = tuple(
    feature for feature in MODEL_FEATURES if feature not in CATEGORICAL_FEATURES
)


def stable_account_split(account_ids: pd.Series) -> pd.Series:
    buckets = account_ids.astype(str).map(
        lambda account_id: (
            int(sha256(f"{RANDOM_SEED}:{account_id}".encode()).hexdigest()[:8], 16) % 100
        )
    )
    return buckets.map(lambda bucket: "train" if bucket < 80 else "test")


def apply_model_gate(
    average_precision_gain: float,
    lift_at_20pct: float,
    brier_score: float,
    baseline_brier_score: float,
    segment_metrics_complete: bool = True,
) -> tuple[dict[str, object], None]:
    thresholds = {
        "average_precision_gain": 0.05,
        "lift_at_20pct": 1.25,
        "brier_not_worse_than_baseline": True,
        "segment_metrics_complete": True,
    }
    failures = []
    if average_precision_gain < thresholds["average_precision_gain"]:
        failures.append("average_precision_gain")
    if lift_at_20pct < thresholds["lift_at_20pct"]:
        failures.append("lift_at_20pct")
    if brier_score > baseline_brier_score:
        failures.append("brier_score")
    if not segment_metrics_complete:
        failures.append("incomplete_segment_metrics")
    return (
        {
            "publish_model": not failures,
            "thresholds": thresholds,
            "average_precision_gain": average_precision_gain,
            "lift_at_20pct": lift_at_20pct,
            "brier_score": brier_score,
            "baseline_brier_score": baseline_brier_score,
            "segment_metrics_complete": segment_metrics_complete,
            "failure_reasons": failures,
        },
        None,
    )


def _pipeline() -> Pipeline:
    numeric = Pipeline([("imputer", SimpleImputer(strategy="median"))])
    categorical = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    return Pipeline(
        [
            (
                "preprocess",
                ColumnTransformer(
                    [
                        ("numeric", numeric, list(NUMERIC_FEATURES)),
                        ("categorical", categorical, list(CATEGORICAL_FEATURES)),
                    ]
                ),
            ),
            (
                "model",
                LogisticRegression(
                    class_weight="balanced", max_iter=2000, random_state=RANDOM_SEED
                ),
            ),
        ]
    )


def _model_matrix(frame: pd.DataFrame) -> pd.DataFrame:
    matrix = frame[list(MODEL_FEATURES)].copy()
    for feature in NUMERIC_FEATURES:
        matrix[feature] = pd.to_numeric(matrix[feature], errors="coerce").astype(float)
    for feature in CATEGORICAL_FEATURES:
        matrix[feature] = matrix[feature].astype("string").astype(object)
        matrix.loc[matrix[feature].isna(), feature] = np.nan
    return matrix


def _top_twenty_metrics(outcome: pd.Series, probability: np.ndarray) -> tuple[float, float]:
    count = max(1, ceil(len(outcome) * 0.20))
    order = np.argsort(-probability)[:count]
    positives = float(outcome.sum())
    recall = float(outcome.iloc[order].sum() / positives) if positives else 0.0
    overall_rate = positives / len(outcome) if len(outcome) else 0.0
    top_rate = float(outcome.iloc[order].mean()) if count else 0.0
    lift = top_rate / overall_rate if overall_rate else 0.0
    return recall, lift


def _segment_evaluation(
    test: pd.DataFrame, outcome: pd.Series, probability: np.ndarray
) -> tuple[list[dict[str, Any]], bool]:
    frame = test[["plan_tier", "billing_frequency", "mrr_active"]].copy()
    frame["outcome"] = outcome.to_numpy()
    frame["probability"] = probability
    frame["mrr_band"] = pd.cut(
        frame["mrr_active"],
        [-np.inf, 500, 2_000, np.inf],
        labels=["low", "mid", "high"],
    )
    rows = []
    complete = True
    for dimension in ("plan_tier", "billing_frequency", "mrr_band"):
        for segment, group in frame.groupby(dimension, observed=True, dropna=False):
            if len(group) < MIN_SEGMENT_ACCOUNTS:
                continue
            if group["outcome"].nunique() < 2:
                complete = False
                rows.append(
                    {
                        "dimension": dimension,
                        "segment": str(segment),
                        "sample_size": len(group),
                        "status": "single_class",
                    }
                )
                continue
            recall, lift = _top_twenty_metrics(group["outcome"], group["probability"].to_numpy())
            rows.append(
                {
                    "dimension": dimension,
                    "segment": str(segment),
                    "sample_size": len(group),
                    "average_precision": float(
                        average_precision_score(group["outcome"], group["probability"])
                    ),
                    "brier_score": float(brier_score_loss(group["outcome"], group["probability"])),
                    "recall_at_20pct": recall,
                    "lift_at_20pct": lift,
                    "status": "ok",
                }
            )
    return rows, complete


def _failure(reason: str) -> tuple[dict[str, object], None]:
    return {"publish_model": False, "failure_reasons": [reason]}, None


def evaluate_model(panel: pd.DataFrame) -> tuple[dict[str, object], pd.DataFrame | None]:
    if "chronology" in panel and not panel["chronology"].eq("strict").all():
        return _failure("observed_chronology_forbidden")
    missing = sorted(set(MODEL_FEATURES) - set(panel.columns))
    if missing:
        return _failure(f"missing_features:{','.join(missing)}")

    if "has_active_subscription" in panel:
        panel = panel.loc[panel["has_active_subscription"].fillna(False)].copy()

    split = stable_account_split(panel["account_id"])
    labeled = panel.loc[panel["churn_next_30d"].notna()].copy()
    labeled["account_split"] = split.loc[labeled.index]
    train = labeled.loc[
        labeled["account_split"].eq("train") & labeled["cutoff"].le(pd.Timestamp("2024-08-31"))
    ]
    test = labeled.loc[
        labeled["account_split"].eq("test")
        & labeled["cutoff"].between(pd.Timestamp("2024-09-30"), pd.Timestamp("2024-11-30"))
    ]
    if set(train["account_id"]) & set(test["account_id"]):
        return _failure("account_leakage")
    if (
        train.empty
        or test.empty
        or train["churn_next_30d"].nunique() < 2
        or test["churn_next_30d"].nunique() < 2
    ):
        return _failure("single_class_split")

    train_outcome = train["churn_next_30d"].astype(int)
    test_outcome = test["churn_next_30d"].astype(int)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        candidate = _pipeline().fit(_model_matrix(train), train_outcome)
    converged = not any(issubclass(item.category, ConvergenceWarning) for item in caught)
    baseline = DummyClassifier(strategy="prior").fit(np.zeros((len(train), 1)), train_outcome)
    probability = candidate.predict_proba(_model_matrix(test))[:, 1]
    baseline_probability = baseline.predict_proba(np.zeros((len(test), 1)))[:, 1]
    average_precision = float(average_precision_score(test_outcome, probability))
    baseline_average_precision = float(average_precision_score(test_outcome, baseline_probability))
    recall, lift = _top_twenty_metrics(test_outcome, probability)
    segment_metrics, complete = _segment_evaluation(test, test_outcome, probability)
    evaluation, _ = apply_model_gate(
        average_precision_gain=average_precision - baseline_average_precision,
        lift_at_20pct=lift,
        brier_score=float(brier_score_loss(test_outcome, probability)),
        baseline_brier_score=float(brier_score_loss(test_outcome, baseline_probability)),
        segment_metrics_complete=complete,
    )
    evaluation.update(
        {
            "average_precision": average_precision,
            "baseline_average_precision": baseline_average_precision,
            "recall_at_20pct": recall,
            "segment_metrics": segment_metrics,
            "train_rows": len(train),
            "test_rows": len(test),
            "train_cutoff_end": "2024-08-31",
            "test_cutoff_start": "2024-09-30",
            "test_cutoff_end": "2024-11-30",
        }
    )
    if not converged:
        evaluation["publish_model"] = False
        evaluation["failure_reasons"] = [*evaluation["failure_reasons"], "non_converged"]
    if not evaluation["publish_model"]:
        return evaluation, None

    final_labeled = labeled.loc[labeled["cutoff"].le(pd.Timestamp("2024-11-30"))]
    final_model = _pipeline().fit(
        _model_matrix(final_labeled), final_labeled["churn_next_30d"].astype(int)
    )
    scoring = panel.loc[panel["cutoff"].eq(SCORING_CUTOFF)].copy()
    if scoring.empty:
        evaluation["publish_model"] = False
        evaluation["failure_reasons"] = ["missing_scoring_snapshot"]
        return evaluation, None
    scoring_matrix = _model_matrix(scoring)
    scoring_probability = final_model.predict_proba(scoring_matrix)[:, 1]
    transformed = final_model.named_steps["preprocess"].transform(scoring_matrix)
    if hasattr(transformed, "toarray"):
        transformed = transformed.toarray()
    names = final_model.named_steps["preprocess"].get_feature_names_out()
    coefficients = final_model.named_steps["model"].coef_[0]
    contributions = transformed * coefficients
    scores = pd.DataFrame(
        {
            "account_id": scoring["account_id"].to_numpy(),
            "risk_probability": scoring_probability,
            "contributions_json": [
                json.dumps(dict(zip(names, values, strict=True)), sort_keys=True)
                for values in contributions
            ],
        }
    )
    scores["risk_rank"] = (
        scores["risk_probability"].rank(method="first", ascending=False).astype(int)
    )
    return evaluation, scores.sort_values("risk_rank").reset_index(drop=True)
