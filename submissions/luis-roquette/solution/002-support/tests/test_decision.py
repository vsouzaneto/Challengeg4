from dataclasses import replace

import pytest

from support_copilot.decision import (
    SENSITIVE_LABELS,
    TAXONOMIES,
    base_policy,
    decide_route,
    derive_signals,
    priority_score,
)
from support_copilot.modeling import Prediction


def prediction(domain="customer", label="Technical issue", confidence=0.99, zero=False):
    labels = TAXONOMIES[domain]
    probabilities = {key: (1 - confidence) / (len(labels) - 1) for key in labels}
    probabilities[label] = confidence
    return Prediction(domain, "ok", label, confidence, probabilities, "fixture-model", zero)


def policy(domain="customer", threshold=0.8):
    return replace(base_policy(domain, "fixture-model"), automation_enabled=True,
                   threshold=threshold, disabled_reason=None)


def signals(pred, pol, **changes):
    args = dict(domain=pred.domain, ticket_id=f"{pred.domain}:fixture",
                priority="High" if pred.domain == "customer" else None,
                prediction=pred, policy=pol, artifact_valid=True, privacy_passed=True)
    text = changes.pop("text", "device stopped working")
    args.update(changes)
    return derive_signals(text, **args)


@pytest.mark.parametrize("confidence,action", [(0.79, "human_review"), (0.8, "auto_route"),
                                              (0.81, "auto_route"), (1.0, "auto_route")])
def test_threshold_boundaries(confidence, action):
    pred, pol = prediction(confidence=confidence), policy()
    assert decide_route(pred, signals(pred, pol), pol).action == action


@pytest.mark.parametrize("zero,reason", [(True, "ood_zero_vector"),
                                         (None, "ood_check_unavailable")])
def test_ood_beats_adversarial_high_confidence(zero, reason):
    pred, pol = prediction(zero=zero), policy()
    derived = signals(pred, pol)
    assert derived.zero_vector is zero and not derived.input_valid
    assert reason in derived.validation_reasons
    assert reason in decide_route(pred, derived, pol).reason_codes
    forged = replace(derived, input_valid=True, zero_vector=False, validation_reasons=())
    assert decide_route(pred, forged, pol).action == "human_review"


@pytest.mark.parametrize("domain,label", [(domain, label) for domain, labels in
                                         SENSITIVE_LABELS.items() for label in labels])
def test_every_sensitive_category_beats_confidence(domain, label):
    pred, pol = prediction(domain, label), policy(domain)
    result = decide_route(pred, signals(pred, pol), pol)
    assert result.action == "human_review" and f"category:{label}" in result.reason_codes


@pytest.mark.parametrize("changes,reason", [
    ({"priority": "Critical"}, "critical_priority"),
    ({"priority": "urgent"}, "unknown_priority"),
    ({"priority": None}, "unknown_priority"),
    ({"privacy_passed": False}, "privacy_failed"),
    ({"artifact_valid": False}, "artifact_invalid"),
    ({"text": ""}, "empty_or_tokenless_input"),
    ({"text": "!!!"}, "empty_or_tokenless_input"),
    ({"text": "my name is jane"}, "privacy_failed"),
    ({"domain": "it"}, "domain_mismatch"),
])
def test_invalidation_and_risk(changes, reason):
    pred, pol = prediction(), policy()
    decision = decide_route(pred, signals(pred, pol, **changes), pol)
    assert decision.action == "human_review"
    assert reason in decision.reason_codes


@pytest.mark.parametrize("domain,text", [("customer", "please refund payment"),
                                         ("it", "reset password"), ("it", "hr issue")])
def test_text_risk_even_when_predicted_class_is_safe(domain, text):
    pred = prediction(domain, "Technical issue" if domain == "customer" else "Hardware")
    pol = policy(domain)
    assert decide_route(pred, signals(pred, pol, text=text), pol).action == "human_review"


def test_disabled_threshold_missing_detector_and_ambiguous():
    pred = prediction(confidence=1)
    for pol in (replace(policy(), automation_enabled=False), replace(policy(), threshold=None),
                replace(policy(), sensitive_expressions=None),
                replace(policy(), model_version="other")):
        assert decide_route(pred, signals(pred, pol), pol).action == "human_review"
    pred = prediction(confidence=0.51)
    probabilities = dict.fromkeys(TAXONOMIES["customer"], 0.0)
    probabilities.update({"Technical issue": .51, "Product inquiry": .49})
    pred = replace(pred, probabilities=probabilities)
    pol = policy(threshold=.5)
    assert decide_route(pred, signals(pred, pol), pol).reason_codes == ("ambiguous_input",)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -0.1, 1.1])
def test_probability_adversaries_rejected(value):
    pred = prediction()
    probabilities = dict(pred.probabilities)
    probabilities["Technical issue"] = value
    with pytest.raises(ValueError):
        replace(pred, probabilities=probabilities)
    pred.probabilities["Technical issue"] = value
    pol = policy()
    assert decide_route(pred, signals(pred, pol), pol).action == "human_review"


def test_invalid_prediction_sum_label_confidence_and_non_ok_payload():
    pred = prediction()
    for change in ({"confidence": .8}, {"label": "Hardware"}, {"status": "unsupported"},
                   {"probabilities": {"Technical issue": 1.0}}):
        with pytest.raises(ValueError):
            replace(pred, **change)
    probabilities = dict(pred.probabilities)
    probabilities["Product inquiry"] = .5
    with pytest.raises(ValueError):
        replace(pred, probabilities=probabilities)


def test_priority_components_and_stable_tie_break():
    assert priority_score("Critical", None, 2) == (4, 2, 1)
    assert priority_score(None, .9, 0) == (0, 0, pytest.approx(.1))
    tickets = [("c", "Low", .9, 0), ("b", "High", .8, 1), ("a", "High", .8, 1)]
    ordered = sorted(tickets, key=lambda row: (*(-x for x in priority_score(*row[1:])), row[0]))
    assert [row[0] for row in ordered] == ["a", "b", "c"]
    for args in (("urgent", .8, 0), (None, float("nan"), 0), (None, None, -1)):
        with pytest.raises(ValueError):
            priority_score(*args)


def test_forged_signals_cannot_hide_ambiguity_or_missing_detector():
    pred, pol = prediction(confidence=.51), policy(threshold=.5)
    probabilities = dict.fromkeys(TAXONOMIES["customer"], 0.0)
    probabilities.update({"Technical issue": .51, "Product inquiry": .49})
    pred = replace(pred, probabilities=probabilities)
    forged = replace(signals(pred, pol), ambiguous=False)
    assert "ambiguous_input" in decide_route(pred, forged, pol).reason_codes
    pred = prediction()
    safe = signals(pred, pol)
    for change in ({"sensitive_expressions": ()}, {"sensitive_labels": ()},
                   {"ambiguity_margin": float("nan")}):
        broken = replace(pol, **change)
        assert "risk_detector_unavailable" in decide_route(pred, safe, broken).reason_codes


def test_risk_precedes_disabled_model_and_privacy_precedes_risk():
    pred = Prediction("customer", "unsupported", zero_vector=False,
                      reason_codes=("classification_unsupported",))
    pol = base_policy("customer")
    risky = signals(pred, pol, priority="Critical", text="refund payment")
    decision = decide_route(pred, risky, pol)
    assert "critical_priority" in decision.reason_codes
    assert "model_unavailable" not in decision.reason_codes
    private = signals(pred, pol, priority="Critical", privacy_passed=False)
    assert "privacy_failed" in decide_route(pred, private, pol).reason_codes
    assert "critical_priority" not in decide_route(pred, private, pol).reason_codes
