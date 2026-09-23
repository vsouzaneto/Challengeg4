"""Versioned, fail-closed routing rules; pure functions with no external effects.

Lexical rules and TF-IDF zero vectors only detect some sensitive/OOD inputs.
IT categories express semantic risk, not measured operational outcomes.
"""

from __future__ import annotations

import math
import re
from dataclasses import asdict, dataclass, field, replace
from typing import TYPE_CHECKING, Literal

from support_copilot.data import (
    CUSTOMER_TAXONOMY,
    IT_TAXONOMY,
    Domain,
    content_hash,
    sanitize_text,
)

if TYPE_CHECKING:
    from support_copilot.modeling import Prediction

TAXONOMIES = {"customer": CUSTOMER_TAXONOMY, "it": IT_TAXONOMY}
PRIORITIES = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
THRESHOLDS = tuple(i / 100 for i in range(50, 100, 5))
SENSITIVE_LABELS = {
    "customer": ("Billing inquiry", "Refund request", "Cancellation request"),
    "it": ("HR Support", "Access", "Administrative rights"),
}
SENSITIVE_EXPRESSIONS = {
    "customer": (r"\bbilling\b", r"\brefund\b", r"\bcancel(?:lation)?\b",
                 r"\bpayment\b", r"\bcredit card\b", r"\bfraud\b"),
    "it": (r"\bhr\b", r"\bhuman resources\b", r"\baccess\b", r"\bpermission\w*\b",
           r"\badmin(?:istrative|istrator)?\b", r"\bpassword\b", r"\bpayroll\b"),
}


@dataclass(frozen=True)
class RoutingPolicy:
    domain: Domain
    rules_version: str
    model_version: str | None
    automation_enabled: bool = False
    threshold: float | None = None
    disabled_reason: str | None = "pending_selection"
    sensitive_labels: tuple[str, ...] = ()
    sensitive_expressions: tuple[str, ...] | None = None
    ambiguity_margin: float = 0.10
    selection_evidence: dict = field(default_factory=dict)
    risk_evidence: dict = field(default_factory=dict)
    locked: bool = False
    configuration_sha256: str | None = None


def policy_hash(policy: RoutingPolicy) -> str:
    payload = asdict(policy)
    payload.pop("configuration_sha256")
    payload.pop("locked")
    return content_hash(payload)


def lock_policy(policy: RoutingPolicy) -> RoutingPolicy:
    rules = {key: value for key, value in asdict(policy).items() if key in {
        "domain", "automation_enabled", "threshold", "disabled_reason", "sensitive_labels",
        "sensitive_expressions", "ambiguity_margin",
    }}
    policy = replace(policy, rules_version=content_hash(rules))
    return replace(policy, locked=True, configuration_sha256=policy_hash(policy))


def base_policy(domain: Domain, model_version: str | None = None) -> RoutingPolicy:
    if domain not in TAXONOMIES:
        raise ValueError("domain_mismatch")
    rules = {"domain": domain, "labels": SENSITIVE_LABELS[domain],
             "expressions": SENSITIVE_EXPRESSIONS[domain], "ambiguity_margin": 0.10,
             "critical_blocks": True, "ood": "fitted_tfidf_zero_vector",
             "threshold_grid": THRESHOLDS, "maximum_selective_error": 0.10}
    return RoutingPolicy(domain, content_hash(rules), model_version,
                         sensitive_labels=SENSITIVE_LABELS[domain],
                         sensitive_expressions=SENSITIVE_EXPRESSIONS[domain])


@dataclass(frozen=True)
class TicketSignals:
    domain: Domain
    ticket_id: str
    input_valid: bool
    privacy_passed: bool
    artifact_valid: bool
    priority: Literal["Low", "Medium", "High", "Critical"] | None
    zero_vector: bool | None
    ambiguous: bool
    sensitive_matches: tuple[str, ...]
    validation_reasons: tuple[str, ...]


@dataclass(frozen=True)
class RouteDecision:
    action: Literal["auto_route", "human_review"]
    reason_codes: tuple[str, ...]
    threshold: float | None
    rules_version: str
    model_version: str | None


def _risk_detector_available(policy: RoutingPolicy) -> bool:
    try:
        return (policy.domain in TAXONOMIES and policy.ambiguity_margin == 0.10
                and set(SENSITIVE_LABELS[policy.domain]) <= set(policy.sensitive_labels)
                and set(SENSITIVE_EXPRESSIONS[policy.domain]) <= set(policy.sensitive_expressions)
                and all(re.compile(pattern) for pattern in policy.sensitive_expressions))
    except (TypeError, re.error):
        return False


def derive_signals(text, *, domain, ticket_id, priority, prediction, policy,
                   artifact_valid, privacy_passed) -> TicketSignals:
    reasons, matches = [], []
    clean = ""
    try:
        clean = sanitize_text(text)
    except ValueError:
        privacy_passed = False
    if not re.search(r"\b\w\w+\b", re.sub(r"\[[A-Z]+\]", "", clean)):
        reasons.append("empty_or_tokenless_input")
    if not privacy_passed:
        reasons.append("privacy_failed")
    if not artifact_valid:
        reasons.append("artifact_invalid")
    if domain not in TAXONOMIES or prediction.domain != domain or policy.domain != domain:
        reasons.append("domain_mismatch")
    try:
        prediction.validate()
    except (ValueError, TypeError):
        reasons.append("invalid_prediction")
    if prediction.zero_vector is True:
        reasons.append("ood_zero_vector")
    elif prediction.zero_vector is not False:
        reasons.append("ood_check_unavailable")
    if domain == "customer" and priority not in PRIORITIES:
        reasons.append("unknown_priority")
    if domain == "it" and priority is not None:
        reasons.append("it_priority_not_observed")
    if not _risk_detector_available(policy):
        reasons.append("risk_detector_unavailable")
    else:
        try:
            matches.extend(f"text:{pattern}" for pattern in policy.sensitive_expressions
                           if re.search(pattern, clean, flags=re.I))
        except (re.error, TypeError):
            reasons.append("risk_detector_unavailable")
    if prediction.label in policy.sensitive_labels:
        matches.append(f"category:{prediction.label}")
    ambiguous = False
    if prediction.status == "ok" and "invalid_prediction" not in reasons:
        values = sorted(prediction.probabilities.values(), reverse=True)
        ambiguous = len(values) > 1 and values[0] - values[1] < policy.ambiguity_margin
    return TicketSignals(domain, ticket_id, not reasons, privacy_passed, artifact_valid,
                         priority, prediction.zero_vector, ambiguous, tuple(sorted(set(matches))),
                         tuple(dict.fromkeys(reasons)))


def decide_route(prediction: Prediction, signals: TicketSignals,
                 policy: RoutingPolicy) -> RouteDecision:
    """Revalidate numerical/domain invariants even for a forged signal object."""
    reasons = list(signals.validation_reasons)
    if not signals.input_valid:
        reasons.append("invalid_input")
    if not signals.privacy_passed:
        reasons.append("privacy_failed")
    if not signals.artifact_valid:
        reasons.append("artifact_invalid")
    if signals.domain != prediction.domain or signals.domain != policy.domain:
        reasons.append("domain_mismatch")
    if not _risk_detector_available(policy):
        reasons.append("risk_detector_unavailable")
    try:
        prediction.validate()
    except (ValueError, TypeError):
        reasons.append("invalid_prediction")
    for zero in (prediction.zero_vector, signals.zero_vector):
        if zero is not False:
            reasons.append("ood_zero_vector" if zero is True else "ood_check_unavailable")
    if signals.domain == "customer" and signals.priority not in PRIORITIES:
        reasons.append("unknown_priority")
    if signals.domain == "it" and signals.priority is not None:
        reasons.append("it_priority_not_observed")
    if not reasons:
        reasons.extend(signals.sensitive_matches)
        if prediction.label in policy.sensitive_labels:
            reasons.append(f"category:{prediction.label}")
        if signals.priority == "Critical":
            reasons.append("critical_priority")
        probabilities = sorted((prediction.probabilities or {}).values(), reverse=True)
        if signals.ambiguous or (len(probabilities) > 1
                                 and probabilities[0] - probabilities[1]
                                 < policy.ambiguity_margin):
            reasons.append("ambiguous_input")
    if not reasons:
        if prediction.status != "ok":
            reasons.extend(("model_unavailable", *prediction.reason_codes))
        elif not prediction.model_version or prediction.model_version != policy.model_version:
            reasons.append("model_version_mismatch")
        elif not policy.automation_enabled or policy.threshold not in THRESHOLDS:
            reasons.append(policy.disabled_reason or "automation_disabled")
        elif prediction.confidence < policy.threshold:
            reasons.append("below_threshold")
    return RouteDecision("human_review" if reasons else "auto_route",
                         tuple(dict.fromkeys(reasons)) or ("validated_threshold",),
                         policy.threshold, policy.rules_version, policy.model_version)


def priority_score(priority, confidence: float | None, risk_count: int) -> tuple[int, int, float]:
    if priority is not None and priority not in PRIORITIES:
        raise ValueError("unknown_priority")
    if isinstance(risk_count, bool) or not isinstance(risk_count, int) or risk_count < 0:
        raise ValueError("invalid_risk_count")
    if confidence is not None and (not math.isfinite(confidence) or not 0 <= confidence <= 1):
        raise ValueError("invalid_confidence")
    return PRIORITIES.get(priority, 0), risk_count, 1 if confidence is None else 1 - confidence
