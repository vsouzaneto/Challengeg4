"""Independent text models and development-only policy selection.

Training never reads test text/labels. Final evaluation requires the exact locked
configuration and cannot adjust it. The reproduction pipeline owns test release.
"""

from __future__ import annotations

import math
import re
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field, replace
from typing import Literal

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.frozen import FrozenEstimator
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, f1_score, log_loss
from sklearn.model_selection import StratifiedKFold
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from support_copilot.data import DatasetSplit, Domain, content_hash, sanitize_text
from support_copilot.decision import (
    TAXONOMIES,
    THRESHOLDS,
    RoutingPolicy,
    base_policy,
    decide_route,
    derive_signals,
    lock_policy,
    policy_hash,
)

SEED = 42
SIMPLICITY_ORDER = ("dummy", "nb", "lr", "svc")


@dataclass(frozen=True)
class Prediction:
    domain: Domain
    status: Literal["ok", "unsupported", "unavailable", "invalid_input"]
    label: str | None = None
    confidence: float | None = None
    probabilities: dict[str, float] | None = None
    model_version: str | None = None
    zero_vector: bool | None = None
    reason_codes: tuple[str, ...] = ()

    def __post_init__(self):
        self.validate()

    def validate(self) -> None:
        if self.domain not in TAXONOMIES or self.status not in {
            "ok", "unsupported", "unavailable", "invalid_input"
        }:
            raise ValueError("invalid_prediction_state")
        if self.zero_vector is not None and type(self.zero_vector) is not bool:
            raise ValueError("invalid_zero_vector")
        if self.status != "ok":
            if any(value is not None for value in
                   (self.label, self.confidence, self.probabilities)):
                raise ValueError("non_ok_prediction_has_values")
            return
        probabilities = self.probabilities
        if (not isinstance(probabilities, dict)
                or set(probabilities) != set(TAXONOMIES[self.domain])):
            raise ValueError("invalid_probability_taxonomy")
        if any(isinstance(p, bool) or not isinstance(p, (float, int)) or not math.isfinite(p)
               or not 0 <= p <= 1 for p in probabilities.values()):
            raise ValueError("invalid_probabilities")
        if not math.isclose(sum(probabilities.values()), 1, rel_tol=0, abs_tol=1e-6):
            raise ValueError("invalid_probability_sum")
        if (self.label not in probabilities or self.confidence is None
                or isinstance(self.confidence, bool)
                or not isinstance(self.confidence, (float, int))
                or not math.isfinite(self.confidence)
                or not 0 <= self.confidence <= 1
                or self.confidence != max(probabilities.values())
                or probabilities[self.label] != self.confidence):
            raise ValueError("invalid_label_or_confidence")


@dataclass(frozen=True)
class SelectionResult:
    candidate: str | None
    scores: dict[str, tuple[float, ...]]
    means: dict[str, float]
    standard_deviations: dict[str, float]
    baseline: float | None
    gain: float | None
    reason: str
    folds: tuple[dict, ...] = ()
    class_support: dict[str, int] = field(default_factory=dict)
    subject_ablation: str = "not_run:subject_requires_proxy_audit;description_only"


@dataclass(frozen=True)
class DomainModel:
    domain: Domain
    pipeline: Pipeline
    calibrator: CalibratedClassifierCV
    model_version: str

    def predict_one(self, text: str) -> Prediction:
        return self.predict_batch([text])[0]

    def predict_batch(self, texts: Sequence[str]) -> list[Prediction]:
        if isinstance(texts, str):
            raise ValueError("predict_batch_requires_sequence")
        outputs = []
        for text in texts:
            try:
                clean = sanitize_text(text)
                if not re.search(r"\b\w\w+\b", re.sub(r"\[[A-Z]+\]", "", clean)):
                    raise ValueError("empty_input")
            except ValueError:
                outputs.append(Prediction(self.domain, "invalid_input",
                                          model_version=self.model_version,
                                          reason_codes=("invalid_or_private_input",)))
                continue
            try:
                vector = self.pipeline.named_steps["tfidf"].transform([clean])
                zero = vector.nnz == 0
            except Exception:
                outputs.append(Prediction(self.domain, "unavailable",
                                          model_version=self.model_version,
                                          reason_codes=("ood_check_unavailable",)))
                continue
            if zero:
                outputs.append(Prediction(self.domain, "invalid_input",
                                          model_version=self.model_version, zero_vector=True,
                                          reason_codes=("ood_zero_vector",)))
                continue
            try:
                values = self.calibrator.predict_proba([clean])[0]
                probabilities = dict(zip(self.calibrator.classes_, map(float, values), strict=True))
                label = max(probabilities, key=probabilities.get)
                outputs.append(Prediction(self.domain, "ok", label, probabilities[label],
                                          probabilities, self.model_version, False))
            except Exception:
                outputs.append(Prediction(self.domain, "unavailable",
                                          model_version=self.model_version, zero_vector=False,
                                          reason_codes=("model_prediction_failed",)))
        return outputs


@dataclass(frozen=True)
class ModelTrainingResult:
    status: Literal["supported", "classification_unsupported", "insufficient_support"]
    model: DomainModel | None
    selection: SelectionResult
    policy: RoutingPolicy
    reason_codes: tuple[str, ...]
    development: dict = field(default_factory=dict)
    configuration_sha256: str | None = None


@dataclass(frozen=True)
class ModelMetrics:
    domain: Domain
    status: str
    macro_f1: float | None
    classes: dict
    confusion: list[list[int]] | None
    log_loss: float | None
    ece: float | None
    calibration_bins: tuple[dict, ...]
    risk_coverage: tuple[dict, ...]
    denominators: dict
    reason_codes: tuple[str, ...]


def candidate_pipelines() -> dict[str, Pipeline]:
    estimators = {"dummy": DummyClassifier(strategy="most_frequent"),
                  "nb": MultinomialNB(),
                  "lr": LogisticRegression(max_iter=1000, random_state=SEED),
                  "svc": LinearSVC(random_state=SEED)}
    return {name: Pipeline([("tfidf", TfidfVectorizer()), ("classifier", estimator)])
            for name, estimator in estimators.items()}


def _validate_frame(frame: pd.DataFrame, domain: Domain) -> None:
    if not {"ticket_id", "domain", "text", "target"} <= set(frame):
        raise ValueError("model_frame_schema")
    if domain not in TAXONOMIES or not frame.domain.eq(domain).all():
        raise ValueError("domain_mismatch")
    if frame.ticket_id.duplicated().any() or frame.ticket_id.isna().any():
        raise ValueError("duplicate_or_missing_id")
    if not frame.target.isin(TAXONOMIES[domain]).all():
        raise ValueError("invalid_taxonomy")
    for text in frame.text:
        if not isinstance(text, str) or sanitize_text(text) != text or not text:
            raise ValueError("unsanitized_training_text")


def select_candidate(train: pd.DataFrame, text: str = "text",
                     target: str = "target") -> SelectionResult:
    if text != "text" or target != "target":
        raise ValueError("features_not_approved:subject_requires_proxy_audit")
    domains = set(train.domain)
    if len(domains) != 1:
        return SelectionResult(None, {}, {}, {}, None, None, "insufficient_support")
    domain = next(iter(domains))
    _validate_frame(train, domain)
    support = train[target].value_counts().sort_index().to_dict()
    if set(support) != set(TAXONOMIES[domain]) or min(support.values(), default=0) < 5:
        return SelectionResult(None, {}, {}, {}, None, None, "insufficient_support",
                               class_support=support)
    folds = tuple(StratifiedKFold(5, shuffle=True, random_state=SEED).split(train[text],
                                                                          train[target]))
    fold_records = tuple({"train_ids": tuple(train.iloc[a].ticket_id),
                          "validation_ids": tuple(train.iloc[b].ticket_id),
                          "train_support": train.iloc[a][target].value_counts().to_dict(),
                          "validation_support": train.iloc[b][target].value_counts().to_dict()}
                         for a, b in folds)
    scores = {}
    for name, pipeline in candidate_pipelines().items():
        scores[name] = tuple(float(f1_score(
            train.iloc[b][target],
            clone(pipeline).fit(train.iloc[a][text], train.iloc[a][target]).predict(
                train.iloc[b][text]),
            labels=TAXONOMIES[domain], average="macro", zero_division=0,
        )) for a, b in folds)
    means = {name: float(np.mean(values)) for name, values in scores.items()}
    deviations = {name: float(np.std(values)) for name, values in scores.items()}
    best = max(means.values())
    candidate = next(name for name in SIMPLICITY_ORDER if best - means[name] <= 0.01 + 1e-12)
    gain = means[candidate] - means["dummy"]
    return SelectionResult(candidate, scores, means, deviations, means["dummy"], gain,
                           "selected" if gain >= 0.02 - 1e-12 else "gain_below_0.02",
                           fold_records, support)


def _risk_evidence(train, policy):
    return {"source": "train_only", "denominator": len(train),
            "rationale": ("semantic_risk_without_operational_outcomes" if policy.domain == "it"
                          else "financial_or_account_changes_require_human_review"),
            "limitations": "lexical_rules_and_zero_vectors_are_not_complete_risk_or_ood_detectors",
            "categories": {label: {"count": int(train.target.eq(label).sum()),
                                    "example_ids": train.loc[train.target.eq(label), "ticket_id"]
                                    .sort_values().head(3).tolist()}
                           for label in policy.sensitive_labels}}


def _routes(frame, predictions, policy):
    return [decide_route(prediction, derive_signals(
        row.text, domain=policy.domain, ticket_id=row.ticket_id,
        priority=row.get("Ticket Priority") if policy.domain == "customer" else None,
        prediction=prediction, policy=policy, artifact_valid=True, privacy_passed=True,
    ), policy) for (_, row), prediction in zip(frame.iterrows(), predictions, strict=True)]


def _coverage(frame, predictions, policy):
    routes = _routes(frame, predictions, policy)
    accepted = [i for i, route in enumerate(routes) if route.action == "auto_route"]
    errors = sum(predictions[i].label != frame.iloc[i].target for i in accepted)
    return {"threshold": policy.threshold, "n_total": len(frame), "n_accepted": len(accepted),
            "n_errors": errors, "coverage": len(accepted) / len(frame) if len(frame) else None,
            "selective_risk": errors / len(accepted) if accepted else None,
            "risk_reason": None if accepted else "empty_accepted_set"}


def select_routing_policy(frame: pd.DataFrame, predictions: Sequence[Prediction],
                          policy: RoutingPolicy) -> RoutingPolicy:
    """Development-only selection; use the exact same derive/gate path as inference."""
    if policy.locked:
        raise ValueError("policy_already_locked")
    _validate_frame(frame, policy.domain)
    measurements = tuple(_coverage(frame, predictions, replace(
        policy, automation_enabled=True, threshold=t, disabled_reason=None)) for t in THRESHOLDS)
    eligible = [row for row in measurements if row["n_accepted"]
                and row["selective_risk"] <= 0.10]
    threshold = eligible[0]["threshold"] if eligible else None
    return lock_policy(replace(
        policy, automation_enabled=bool(eligible), threshold=threshold,
        disabled_reason=None if eligible else "no_eligible_threshold",
        selection_evidence={"kind": "development_not_final", "source": "policy_selection",
                            "ids": frame.ticket_id.tolist(), "grid": measurements},
    ))


def train_domain_model(domain: Domain, split: DatasetSplit) -> ModelTrainingResult:
    if domain != split.domain:
        raise ValueError("domain_mismatch")
    parts = (split.train, split.calibration_fit, split.policy_selection)
    for part in parts:
        _validate_frame(part, domain)
    for column in ("ticket_id", "text_group_id"):
        sets = [set(part[column]) for part in parts]
        if any(sets[i] & sets[j] for i in range(3) for j in range(i)):
            raise ValueError("development_partition_overlap")
        sealed = set(split.manifest["partitions"]["test"][
            "ids" if column == "ticket_id" else "groups"])
        if any(values & sealed for values in sets):
            raise ValueError("frozen_test_overlap")
    for name, part in zip(("train", "calibration_fit", "policy_selection"), parts, strict=True):
        if set(part.ticket_id) != set(split.manifest["partitions"][name]["ids"]):
            raise ValueError("split_manifest_mismatch")
    selection = select_candidate(split.train)
    policy = base_policy(domain)
    policy = replace(policy, risk_evidence=_risk_evidence(split.train, policy))
    development = {"kind": "development_not_final", "split_version": split.split_version,
                   "seed": split.manifest["seed"], "cv_seed": SEED,
                   "features": ["text"], "calibration_method": "sigmoid",
                   "train_ids": split.train.ticket_id.tolist(),
                   "calibration_fit_ids": split.calibration_fit.ticket_id.tolist(),
                   "policy_selection_ids": split.policy_selection.ticket_id.tolist(),
                   "rounding": split.manifest["rounding"]}
    insufficient = selection.candidate is None or any(
        set(part.target) != set(TAXONOMIES[domain]) for part in parts)
    status = ("insufficient_support" if insufficient else
              "classification_unsupported" if selection.gain < 0.02 - 1e-12 else "supported")
    if status != "supported":
        policy = lock_policy(replace(policy, disabled_reason=status))
        return ModelTrainingResult(status, None, selection, policy, (status,), development,
                                   policy.configuration_sha256)
    configuration = {**development, "selection": asdict(selection),
                     "train": split.train[["ticket_id", "text", "target"]].to_dict("records"),
                     "calibration": split.calibration_fit[["ticket_id", "text", "target"]]
                     .to_dict("records"), "rules_version": policy.rules_version}
    version = content_hash(configuration)
    pipeline = candidate_pipelines()[selection.candidate].fit(split.train.text, split.train.target)
    # FrozenEstimator.fit is a no-op: all these held-out rows fit only the sigmoid.
    # An explicit single partition also supports fewer than five examples per class.
    calibration_rows = np.arange(len(split.calibration_fit))
    calibrator = CalibratedClassifierCV(
        FrozenEstimator(pipeline), method="sigmoid", ensemble=False,
        cv=[(calibration_rows, calibration_rows)],
    )
    calibrator.fit(split.calibration_fit.text, split.calibration_fit.target)
    model = DomainModel(domain, pipeline, calibrator, version)
    policy = select_routing_policy(split.policy_selection,
                                   model.predict_batch(split.policy_selection.text.tolist()),
                                   replace(policy, model_version=version))
    version = content_hash({"training": version, "policy_lock": policy.configuration_sha256})
    model = replace(model, model_version=version)
    policy = lock_policy(replace(policy, model_version=version))
    return ModelTrainingResult("supported", model, selection, policy, (), development,
                               policy.configuration_sha256)


def evaluate_frozen_test(model_result: ModelTrainingResult, test: pd.DataFrame,
                         policy: RoutingPolicy) -> ModelMetrics:
    if (not policy.locked or policy.configuration_sha256 != policy_hash(policy)
            or model_result.configuration_sha256 != policy.configuration_sha256
            or policy != model_result.policy):
        raise ValueError("configuration_not_locked_or_changed")
    _validate_frame(test, policy.domain)
    development_ids = set().union(*(model_result.development.get(key, ()) for key in
                                    ("train_ids", "calibration_fit_ids", "policy_selection_ids")))
    for fold in model_result.selection.folds:
        development_ids.update(fold["train_ids"])
        development_ids.update(fold["validation_ids"])
    if development_ids & set(test.ticket_id):
        raise ValueError("evaluation_development_overlap")
    labels = TAXONOMIES[policy.domain]
    classes = {label: {"support": int(test.target.eq(label).sum()), "precision": None,
                       "recall": None, "f1-score": None,
                       "null_reasons": {key: "no_valid_predictions" for key in
                                        ("precision", "recall", "f1-score")}}
               for label in labels}
    if model_result.model is None:
        return ModelMetrics(policy.domain, "unavailable", None, classes, None, None, None, (),
                            (), {"n_total": len(test), "n_predicted": 0,
                                 "n_excluded": len(test)}, model_result.reason_codes)
    if (model_result.model.domain != policy.domain
            or model_result.model.model_version != policy.model_version):
        raise ValueError("model_domain_or_version_mismatch")
    predictions = model_result.model.predict_batch(test.text.tolist())
    valid = [i for i, prediction in enumerate(predictions) if prediction.status == "ok"]
    denominators = {"n_total": len(test), "n_predicted": len(valid),
                    "n_excluded": len(test) - len(valid), "ece_bins": 10}
    curve = tuple(_coverage(test, predictions, replace(policy, threshold=t)) for t in THRESHOLDS)
    if not valid:
        return ModelMetrics(policy.domain, "unavailable", None, classes, None, None, None, (),
                            curve, denominators, ("no_valid_predictions",))
    actual = test.iloc[valid].target.tolist()
    predicted = [predictions[i].label for i in valid]
    probs = [[predictions[i].probabilities[label] for label in labels] for i in valid]
    report = classification_report(actual, predicted, labels=labels, output_dict=True,
                                   zero_division=np.nan)
    classes = {label: {
        **{key: value if math.isfinite(value) else None for key, value in report[label].items()},
        "support_total": int(test.target.eq(label).sum()),
        "null_reasons": {key: "zero_denominator" for key, value in report[label].items()
                         if not math.isfinite(value)},
    } for label in labels}
    bins, ece = [], 0.0
    for index in range(10):
        lower, upper = index / 10, (index + 1) / 10
        rows = [i for i in valid if lower <= predictions[i].confidence
                and (predictions[i].confidence < upper or index == 9)]
        accuracy = sum(predictions[i].label == test.iloc[i].target for i in rows) / len(rows) \
            if rows else None
        confidence = sum(predictions[i].confidence for i in rows) / len(rows) if rows else None
        if rows:
            ece += len(rows) / len(valid) * abs(accuracy - confidence)
        bins.append({"lower": lower, "upper": upper, "n": len(rows), "accuracy": accuracy,
                     "confidence": confidence, "reason": None if rows else "empty_bin"})
    return ModelMetrics(policy.domain, "evaluated", float(f1_score(
        actual, predicted, labels=labels, average="macro", zero_division=0)), classes,
        confusion_matrix(actual, predicted, labels=labels).tolist(),
        float(log_loss(actual, probs, labels=list(labels))), float(ece), tuple(bins), curve,
        denominators, ("invalid_predictions_excluded",) if len(valid) != len(test) else ())
