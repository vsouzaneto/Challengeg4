from dataclasses import asdict, replace
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline

import support_copilot.modeling as modeling
from support_copilot.data import canonical_json, make_split
from support_copilot.decision import TAXONOMIES, base_policy, lock_policy
from support_copilot.modeling import (
    Prediction,
    candidate_pipelines,
    evaluate_frozen_test,
    select_candidate,
    select_routing_policy,
    train_domain_model,
)


def fixture_frame(domain="customer", n=10):
    words = ("alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota",
             "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", "rho", "sigma", "tau", "phi")
    # Distinct canonical words, no raw real-world data or label-dependent metadata features.
    tokens = ("billing", "cancellation", "product", "refund", "technical") if domain == "customer" \
        else ("access", "administrative", "hr", "hardware", "project", "miscellaneous",
              "purchase", "storage")
    return pd.DataFrame([{"ticket_id": f"{domain}:{j}:{i}", "domain": domain,
                          "text": f"{token} {token} {words[i]}", "target": label,
                          "text_group_id": "untrusted", "Ticket Priority": "Low"}
                         for j, (label, token) in enumerate(zip(TAXONOMIES[domain], tokens,
                                                               strict=True)) for i in range(n)])


@pytest.fixture(scope="module")
def trained():
    split = make_split(fixture_frame(n=20), "target")
    return split, train_domain_model("customer", split)


def test_shared_folds_vectorizer_fit_only_training_ids(monkeypatch):
    split = make_split(fixture_frame(), "target")
    seen = []
    original = TfidfVectorizer.fit_transform

    def spy(self, documents, y=None):
        seen.append(tuple(documents))
        return original(self, documents, y)

    monkeypatch.setattr(TfidfVectorizer, "fit_transform", spy)
    selected = select_candidate(split.train)
    assert len(seen) == 20
    for i in range(5):
        assert seen[i] == seen[i + 5] == seen[i + 10] == seen[i + 15]
        fold = selected.folds[i]
        assert not set(fold["train_ids"]) & set(fold["validation_ids"])
        assert set(fold["train_ids"]) | set(fold["validation_ids"]) == set(split.train.ticket_id)
    assert selected.candidate == "nb"  # equally perfect LR/SVC do not displace simpler NB
    assert all(len(values) == 5 for values in selected.scores.values())
    assert "subject_requires_proxy_audit" in selected.subject_ablation
    with pytest.raises(ValueError, match="not_approved"):
        select_candidate(split.train, text="Ticket Subject")


@pytest.mark.parametrize("gain,expected", [(0.019, "classification_unsupported"),
                                         (0.020, "supported")])
def test_minimum_gain(gain, expected, monkeypatch):
    split = make_split(fixture_frame(), "target")
    selection = replace(select_candidate(split.train), gain=gain)
    monkeypatch.setattr(modeling, "select_candidate", lambda _: selection)
    result = train_domain_model("customer", split)
    assert result.status == expected
    assert (result.model is None) == (expected != "supported")


def test_calibrator_and_threshold_only_see_frozen_halves(monkeypatch):
    split = make_split(fixture_frame(), "target")
    fitted, selected, pipeline_fits = [], [], []
    original_fit = modeling.CalibratedClassifierCV.fit
    original_select = modeling.select_routing_policy
    original_pipeline_fit = Pipeline.fit

    def pipeline_fit(self, texts, labels, **kwargs):
        pipeline_fits.append(tuple(texts))
        return original_pipeline_fit(self, texts, labels, **kwargs)

    def fit(self, texts, labels, **kwargs):
        fitted.extend(texts)
        assert isinstance(self.estimator, modeling.FrozenEstimator)
        frozen = self.estimator.estimator
        idf = frozen.named_steps["tfidf"].idf_.copy()
        result = original_fit(self, texts, labels, **kwargs)
        assert self.calibrated_classifiers_[0].estimator.estimator is frozen
        np.testing.assert_array_equal(idf, frozen.named_steps["tfidf"].idf_)
        return result

    def select(frame, predictions, policy):
        selected.extend(frame.ticket_id)
        return original_select(frame, predictions, policy)

    monkeypatch.setattr(modeling.CalibratedClassifierCV, "fit", fit)
    monkeypatch.setattr(modeling, "select_routing_policy", select)
    monkeypatch.setattr(Pipeline, "fit", pipeline_fit)
    # Any attempt to access test columns will fail; training needs only manifest sealed IDs.
    result = train_domain_model("customer", replace(split, test=None))
    assert fitted == list(split.calibration_fit.text)
    assert selected == list(split.policy_selection.ticket_id)
    assert not set(fitted) & set(split.train.text)
    assert not set(selected) & set(split.calibration_fit.ticket_id)
    assert len(pipeline_fits) == 21  # 4 candidates x 5 folds, then final training only
    assert pipeline_fits[-1] == tuple(split.train.text)
    assert all(set(texts) <= set(split.train.text) for texts in pipeline_fits)
    assert result.policy.locked and result.configuration_sha256
    assert result.development["calibration_method"] == "sigmoid"
    assert result.policy.risk_evidence["denominator"] == len(split.train)


def test_predictions_and_ood_use_own_fitted_vocabulary(trained):
    split, result = trained
    model = result.model
    known = split.train.text.iloc[0]
    batch = model.predict_batch([known, "zzzzunknownword", "", known])
    assert batch[0] == model.predict_one(known) == batch[3]
    assert batch[1].status == "invalid_input" and batch[1].zero_vector is True
    assert batch[1].probabilities is None
    assert "ood_zero_vector" in batch[1].reason_codes
    assert batch[2].status == "invalid_input"
    assert model.predict_batch([]) == []
    assert not hasattr(model, "predict")
    with pytest.raises(ValueError):
        model.predict_batch(known)
    broken = replace(model, pipeline=Pipeline([]))
    for pred in broken.predict_batch([known, known]):
        assert pred.zero_vector is None and pred.reason_codes == ("ood_check_unavailable",)


def test_model_failure_has_no_fabricated_probabilities(trained):
    split, result = trained
    broken = replace(result.model, calibrator=None)
    prediction = broken.predict_one(split.train.text.iloc[0])
    assert prediction.status == "unavailable" and prediction.zero_vector is False
    assert prediction.confidence is prediction.label is prediction.probabilities is None


def confident(label="Technical issue", confidence=.99):
    values = dict.fromkeys(TAXONOMIES["customer"], (1 - confidence) / 4)
    values[label] = confidence
    return Prediction("customer", "ok", label, confidence, values, "fixture", False)


def test_threshold_selection_applies_risk_first_and_empty_is_not_zero_risk():
    frame = fixture_frame().iloc[:10].copy()
    frame["text"] = "device broken"
    frame["target"] = "Technical issue"
    pol = base_policy("customer", "fixture")
    preds = [confident(confidence=.7)] * 9 + [confident("Product inquiry", .6)]
    chosen = select_routing_policy(frame, preds, pol)
    assert chosen.threshold == .5  # exactly 10% error is eligible
    frame.loc[frame.index[:2], "target"] = "Product inquiry"
    chosen = select_routing_policy(frame, preds, pol)
    assert chosen.threshold is None
    frame["Ticket Priority"] = "Critical"
    chosen = select_routing_policy(frame, [confident(confidence=1)] * 10, pol)
    assert chosen.threshold is None and not chosen.automation_enabled
    assert all(row["selective_risk"] is None for row in chosen.selection_evidence["grid"])


def test_missing_class_mixed_domain_and_contamination(trained):
    split, _ = trained
    missing = split.train[split.train.target != "Refund request"]
    assert select_candidate(missing).reason == "insufficient_support"
    with pytest.raises(ValueError, match="domain_mismatch"):
        train_domain_model("it", split)
    with pytest.raises(ValueError, match="overlap"):
        train_domain_model("customer", replace(split, calibration_fit=split.train))
    missing_fit = split.calibration_fit[split.calibration_fit.target != "Refund request"]
    manifest = {**split.manifest, "partitions": {**split.manifest["partitions"],
                "calibration_fit": {"ids": missing_fit.ticket_id.tolist()}}}
    result = train_domain_model("customer", replace(split, calibration_fit=missing_fit,
                                                   manifest=manifest))
    assert result.status == "insufficient_support" and result.model is None


def test_it_model_is_independent(trained):
    _, customer = trained
    it = train_domain_model("it", make_split(fixture_frame("it"), "target"))
    assert it.model.domain == "it" and it.model.model_version != customer.model.model_version
    assert set(it.model.calibrator.classes_) == set(TAXONOMIES["it"])
    assert it.policy.risk_evidence["rationale"] == "semantic_risk_without_operational_outcomes"


@pytest.mark.parametrize("domain", ["customer", "it"])
def test_frozen_metrics_are_domain_specific_and_taxonomy_complete(domain):
    raw = fixture_frame(domain, n=20)
    split = make_split(raw, "target")
    result = train_domain_model(domain, split)
    test = raw[raw.ticket_id.isin(split.test.ticket_id)]
    metrics = evaluate_frozen_test(result, test, result.policy)
    assert metrics.domain == domain
    assert set(metrics.classes) == set(TAXONOMIES[domain])
    assert len(metrics.confusion) == len(TAXONOMIES[domain])
    assert metrics.denominators["n_total"] == len(test)
    assert metrics.denominators["n_predicted"] + metrics.denominators["n_excluded"] == len(test)


def test_final_evaluation_is_pure_and_requires_lock(trained):
    split, result = trained
    raw_fixture = fixture_frame(n=20)
    test = raw_fixture[raw_fixture.ticket_id.isin(split.test.ticket_id)]
    before = canonical_json(asdict(result.policy))
    metrics = evaluate_frozen_test(result, test, result.policy)
    assert canonical_json(asdict(result.policy)) == before
    assert metrics.status == "evaluated"
    assert metrics.denominators["n_total"] == len(test)
    assert sum(sum(row) for row in metrics.confusion) == len(test)
    assert set(metrics.classes) == set(TAXONOMIES["customer"])
    assert metrics.log_loss >= 0 and 0 <= metrics.ece <= 1
    assert len(metrics.calibration_bins) == 10
    assert sum(row["n"] for row in metrics.calibration_bins) == len(test)
    assert len(metrics.risk_coverage) == 10
    assert np.isfinite(metrics.macro_f1)
    with pytest.raises(ValueError, match="locked"):
        evaluate_frozen_test(result, test, replace(result.policy, threshold=.95))
    with pytest.raises(ValueError, match="locked"):
        evaluate_frozen_test(result, test, replace(result.policy, locked=False))
    with pytest.raises(ValueError, match="overlap"):
        evaluate_frozen_test(result, split.train, result.policy)


def test_unavailable_metrics_are_null_and_empty_accepted_risk_is_null(trained):
    split, result = trained
    test = fixture_frame(n=20)
    test = test[test.ticket_id.isin(split.test.ticket_id)].copy()
    disabled = lock_policy(replace(result.policy, automation_enabled=False, threshold=None,
                                   disabled_reason="test_disabled"))
    result = replace(result, policy=disabled, configuration_sha256=disabled.configuration_sha256)
    metrics = evaluate_frozen_test(result, test, disabled)
    assert all(row["selective_risk"] is None for row in metrics.risk_coverage)
    unavailable = replace(result, model=None, reason_codes=("classification_unsupported",))
    metrics = evaluate_frozen_test(unavailable, test, disabled)
    assert metrics.macro_f1 is metrics.log_loss is metrics.ece is None
    assert metrics.denominators["n_predicted"] == 0
    test["text"] = "zzzzunknownword"
    metrics = evaluate_frozen_test(result, test, disabled)
    assert metrics.reason_codes == ("no_valid_predictions",)


def test_candidate_instances_are_independent():
    a, b = candidate_pipelines(), candidate_pipelines()
    assert tuple(a) == ("dummy", "nb", "lr", "svc")
    assert a["nb"] is not b["nb"]


@pytest.mark.parametrize("advantage,expected", [(.010, "nb"), (.011, "lr")])
def test_simplicity_tolerance_is_inclusive(advantage, expected, monkeypatch):
    scores = iter([.1] * 5 + [.5] * 5 + [.5 + advantage] * 5 + [.5] * 5)
    monkeypatch.setattr(modeling, "f1_score", lambda *args, **kwargs: next(scores))
    selected = select_candidate(make_split(fixture_frame(), "target").train)
    assert selected.candidate == expected


def test_locked_policy_cannot_be_retuned_and_threshold_changes_rules_version():
    frame = fixture_frame().iloc[:1].copy()
    frame["text"], frame["target"] = "device broken", "Technical issue"
    chosen = select_routing_policy(frame, [confident()], base_policy("customer", "fixture"))
    with pytest.raises(ValueError, match="already_locked"):
        select_routing_policy(frame, [confident()], chosen)
    assert lock_policy(chosen) == chosen
    assert lock_policy(replace(chosen, threshold=.95)).rules_version != chosen.rules_version


def test_zero_vector_and_missing_measurement_propagate_scalar_and_batch(trained):
    from support_copilot.decision import decide_route, derive_signals

    split, result = trained
    for model, text, reason in (
        (result.model, "zzzzunknownword", "ood_zero_vector"),
        (replace(result.model, pipeline=Pipeline([])), split.train.text.iloc[0],
         "ood_check_unavailable"),
    ):
        outputs = [model.predict_one(text), *model.predict_batch([text, text])]
        for pred in outputs:
            signals = derive_signals(text, domain="customer", ticket_id="customer:fixture",
                                     priority="Low", prediction=pred, policy=result.policy,
                                     artifact_valid=True, privacy_passed=True)
            route = decide_route(pred, signals, result.policy)
            assert route.action == "human_review" and reason in route.reason_codes


def test_empty_development_returns_insufficient_support():
    result = train_domain_model("customer", make_split(fixture_frame(n=1), "target"))
    assert result.status == "insufficient_support"
    assert result.model is None and not result.policy.automation_enabled
    assert result.policy.threshold is None


def test_metrics_denominators_nulls_and_numerical_values(trained):
    split, result = trained
    test = fixture_frame(n=20)
    test = test[test.ticket_id.isin(split.test.ticket_id)
                & test.target.eq("Technical issue")].copy()
    calibrator = SimpleNamespace(
        classes_=TAXONOMIES["customer"],
        predict_proba=lambda texts: np.tile([.05, .05, .05, .05, .8], (len(texts), 1)),
    )
    result = replace(result, model=replace(result.model, calibrator=calibrator))
    metrics = evaluate_frozen_test(result, test, result.policy)
    assert metrics.macro_f1 == pytest.approx(.2)  # macro over all five declared classes
    assert metrics.log_loss == pytest.approx(-np.log(.8))
    assert metrics.ece == pytest.approx(.2)
    assert metrics.classes["Billing inquiry"]["precision"] is None
    assert metrics.classes["Billing inquiry"]["null_reasons"]["precision"] == "zero_denominator"
    assert metrics.classes["Technical issue"]["support"] == len(test)
    canonical_json(asdict(metrics))  # no non-standard JSON NaN for undefined metrics
    empty = evaluate_frozen_test(result, test.iloc[:0], result.policy)
    assert empty.macro_f1 is empty.log_loss is empty.ece is None
    assert all(row["coverage"] is None and row["selective_risk"] is None
               for row in empty.risk_coverage)
