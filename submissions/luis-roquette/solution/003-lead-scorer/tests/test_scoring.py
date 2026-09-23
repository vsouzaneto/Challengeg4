"""Fixed-policy temporal evidence tests. Real final labels are consumed once here.

Synthetic decision tables exercise policy without choosing it from real outcomes.
Later SDD steps extend this file with active scoring/explanation tests.
"""
from dataclasses import FrozenInstanceError, replace
from datetime import date, timedelta
import hashlib
import json
import math
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import scoring as s


def history_fixture(n=1000):
    rows = []
    for i in range(n):
        won = i % 10 == 0 or i % 10 >= 6
        rows.append(dict(opportunity_id=f"{i:05}", deal_stage="Won" if won else "Lost",
            close_date=date(2020, 1, 1)+timedelta(days=i//10), engage_date=date(2019, 1, 1),
            close_value=float(100+i%7) if won else 0., financial_eligible=True,
            eligible_history=True, eligible_active=False, sales_agent=f"seller-{i%3}",
            manager=f"manager-{i%2}", regional_office=f"region-{i%2}",
            product="low" if i%10 < 5 else "high", series="base", sales_price=100.,
            account=f"account-{i%3}", account_match="both", product_match="both",
            seller_match="both", year_established=1990+i%3, route="full"))
    return rows


def period_fixture():
    return tuple(s.PeriodEvidence(name, tuple(f"{name}-{i}" for i in range(n)), n//2,
        n-n//2, n, ()) for name, n in (("train", 200), ("calibration", 100), ("test", 100)))


def evaluation_fixture(candidate="logistic", route="full", status="passed", **kwargs):
    periods = period_fixture()
    default = dict(evaluation_id=f"fixture-{candidate}-{route}", candidate=candidate, route=route,
        status=status, config_fingerprint=s.DEFAULT_CONFIG.fingerprint, split_fingerprint="fixture-split",
        feature_fingerprint="fixture-features", feature_names=("product_low",), periods=periods,
        train_boundary="2020-01-01", calibration_boundary="2020-02-01", baseline_rate=.5,
        brier=.15, log_loss=.4, baseline_brier=.25, baseline_log_loss=.69,
        bands=(s.BandEvidence("baixa", 50, .2, .2, True, ()),
               s.BandEvidence("media", 0, None, None, False, ("empty_band",)),
               s.BandEvidence("alta", 50, .8, .8, True, ())),
        top_k=(s.TopKMetric(.1, 10, .5, .3, None), s.TopKMetric(.2, 20, .5, .5, None)),
        segments=(), reasons=() if status == "passed" else ("fixture_rejection",),
        unavailable_reasons=(), natural_missing_account_count=0, financial_valid_count=100)
    default.update(kwargs)
    return s.CandidateEvaluation(**default)


def score_fixture(state="calibrated", stage="Engaging", **kwargs):
    """Concrete C3 fixture for independent UI development; never runtime defaults."""
    base = dict(opportunity_id="fixture-001", stage=stage, sales_agent="Vendedor",
        manager="Gestora", regional_office="Sul", product="Produto", account="Conta",
        state=state, potential_revenue=100., fingerprint="fixture-only",
        diagnostics=(), next_action="Sem ação recomendada com os dados atuais")
    if state == "calibrated":
        base.update(route="full", origin="logistic", band="alta", band_kind="probability",
            probability=.8, expected_revenue=80., evaluation_id="fixture-logistic-full",
            observed_n=50, effective_support=50., evidence_strength="moderada",
            explanation_scale="calibrated_log_odds", base_value=0.,
            factors=(s.Factor("product", "Produto", math.log(4), "favoravel", "Referência", True),))
    elif state == "relative":
        base.update(route="prospecting" if stage == "Prospecting" else "fallback",
            origin="historical_evidence", band="media", band_kind="relative", relative_index=.5,
            observed_n=25, prior_strength=20., effective_support=45., evidence_strength="fraca",
            explanation_scale="relative_index", base_value=.5)
    else:
        base.update(diagnostics=(s.diagnostic("unknown_product", "Produto não encontrado",
            "Corrija product no cadastro", field="product", opportunity_id="fixture-001", scope="row"),))
    base.update(kwargs)
    return s.ScoreResult(**base)


def bundle_fixture(scores=None):
    evaluations = tuple(evaluation_fixture(candidate, route) for candidate in ("logistic", "boosting")
        for route in ("full", "fallback"))
    return s.ScoringBundle("fixture-only", s.DEFAULT_CONFIG.version, evaluations,
        tuple(s.select_route(evaluations, route) for route in ("full", "fallback")),
        tuple(scores) if scores is not None else (score_fixture(opportunity_id="fixture-calibrated"),
            score_fixture("relative", "Prospecting", opportunity_id="fixture-prospecting"),
            score_fixture("insufficient_data", opportunity_id="fixture-insufficient")),
        (), {"revision": None, "source_digest": "fixture-only"})


class ContractTests(unittest.TestCase):
    def test_TC13_config_provenance_immutable_and_digest_sensitive(self):
        config = s.DEFAULT_CONFIG
        with self.assertRaises(FrozenInstanceError):
            config.seed = 1
        self.assertNotEqual(config.fingerprint, replace(config, seed=43).fingerprint)
        self.assertEqual(set(s.FEATURE_PROVENANCE), set(config.full_features))
        for name, inputs in s.FEATURE_PROVENANCE.items():
            self.assertEqual(inputs, (name,))
        for field in ("close_value", "close_date", "deal_stage", "sales_agent", "manager",
                      "regional_office", "sales_price", "close_value_log", "days_to_close"):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "provenance"):
                replace(config, full_features=config.full_features+(field,))

    def test_TC12_TC16_mutating_forbidden_fields_cannot_change_feature_vectors(self):
        row = history_fixture(1)[0]
        mutation = dict(row, deal_stage="Engaging", close_value=9999999, close_date=date(2099,1,1),
            sales_agent="Other", manager="Other", regional_office="Other", sales_price=1000000,
            days_to_close=9999, close_value_log=22, account="Other")
        for route in ("full", "fallback"):
            self.assertEqual(s.feature_record(row, route), s.feature_record(mutation, route))
        mutation["year_established"] = None
        self.assertEqual(s.feature_record(row, "fallback"), s.feature_record(mutation, "fallback"))

    def test_C3_variants_serialize_without_unvalidated_probability_keys(self):
        for state, stage in (("calibrated", "Engaging"), ("relative", "Engaging"),
                             ("relative", "Prospecting"), ("insufficient_data", "Engaging")):
            with self.subTest(state=state, stage=stage):
                result = score_fixture(state, stage)
                encoded = json.loads(json.dumps(result.to_dict(), allow_nan=False))
                self.assertEqual("probability" in encoded, state == "calibrated")
                self.assertEqual("expected_revenue" in encoded, state == "calibrated")
                self.assertEqual("relative_index" in encoded, state == "relative")
                with self.assertRaises(FrozenInstanceError):
                    result.state = "relative"
        self.assertEqual(len(bundle_fixture().to_dict()["candidate_evaluations"]), 4)
        self.assertEqual(len({row.opportunity_id for row in bundle_fixture().scores}), 3)
        with self.assertRaises(ValueError):
            replace(bundle_fixture(), candidate_evaluations=())
        with self.assertRaises(ValueError):
            score_fixture("calibrated", "Prospecting")
        with self.assertRaises(ValueError):
            score_fixture("relative", probability=.5)
        with self.assertRaises(ValueError):
            score_fixture("insufficient_data", relative_index=.3)

    def test_C3_bundle_requires_the_dataset_contract(self):
        with self.assertRaisesRegex(ValueError, "dataset"):
            s.build_scoring_bundle(object())

    def test_TC43_probability_bounds_and_invalid_values(self):
        for value in (0., 1e-12, 1-1e-12, 1.):
            with self.subTest(valid=value):
                s.validate_probabilities((value,))
                self.assertEqual(score_fixture(probability=value, expected_revenue=value*100).probability, value)
        for value in (-1e-12, 1+1e-12, float("nan"), float("inf"), None):
            with self.subTest(invalid=value), self.assertRaises(ValueError):
                score_fixture(probability=value, expected_revenue=0.)
        self.assertTrue(all(math.isfinite(value) for value in s.probability_losses((0,1), (1.,0.))))
        with self.assertRaises(ValueError):
            s.probability_losses((1,), (1+1e-12,))


class TemporalTests(unittest.TestCase):
    def test_TC08_closed_membership_disjoint_tied_dates(self):
        rows = history_fixture()
        active = dict(rows[0], opportunity_id="active", deal_stage="Engaging", eligible_history=True)
        invalid = dict(rows[0], opportunity_id="invalid", eligible_history=False)
        split = s.split_closed_history(rows+[active, invalid])
        ids = [set(row["opportunity_id"] for row in period) for period in (split.train, split.calibration, split.test)]
        self.assertEqual([len(part) for part in ids], [600,200,200])
        self.assertFalse(ids[0] & ids[1] or ids[1] & ids[2] or ids[0] & ids[2])
        self.assertEqual(set.union(*ids), {row["opportunity_id"] for row in rows})
        self.assertEqual(split.train_boundary, date(2020,2,29))
        self.assertEqual(split.calibration_boundary, date(2020,3,20))
        self.assertEqual(split.fingerprint, s.split_closed_history(list(reversed(rows))).fingerprint)

    def test_TC09_cutoff_boundary_neighbors(self):
        split = s.split_closed_history(history_fixture())
        membership = {row["close_date"]: name for name in ("train", "calibration", "test") for row in getattr(split, name)}
        for cutoff, expected in ((split.train_boundary, ("train", "train", "calibration")),
                                 (split.calibration_boundary, ("calibration", "calibration", "test"))):
            for delta, name in zip((-1,0,1), expected):
                with self.subTest(cutoff=cutoff, delta=delta):
                    self.assertEqual(membership[cutoff+timedelta(days=delta)], name)
        # One oversized date group cannot be divided merely to obtain 60/20/20.
        rows = history_fixture(100)
        for i, row in enumerate(rows):
            row["close_date"] = date(2020,1,1)+timedelta(days=0 if i<85 else 1 if i<95 else 2)
        tied = s.split_closed_history(rows)
        self.assertEqual(tuple(map(len, (tied.train,tied.calibration,tied.test))), (85,10,5))

    def test_TC10_empty_periods_and_single_class_diagnostics(self):
        for rows in ([], history_fixture(10), history_fixture(20)):
            with self.subTest(count=len(rows)), self.assertRaisesRegex(s.ScoringValidationError, "insufficient_temporal_periods"):
                s.split_closed_history(rows)
        rows = history_fixture()
        for row in rows:
            row["deal_stage"] = "Won"
        split = s.split_closed_history(rows)
        fitted = s.fit_candidate(split, "logistic", "full")
        self.assertIsNone(fitted.pipeline)
        evaluation = s.evaluate_candidate(fitted, split)
        self.assertEqual(evaluation.status, "rejected")
        self.assertIn("training_requires_both_classes", evaluation.reasons)
        self.assertIsNone(evaluation.brier)
        rows = history_fixture()
        for row in rows[600:800]:
            row["deal_stage"] = "Won"
        split = s.split_closed_history(rows)
        fitted = s.fit_candidate(split, "logistic", "fallback")
        self.assertIsNotNone(fitted.pipeline)
        self.assertIsNone(fitted.calibrated)
        self.assertIn("calibration_requires_both_classes", s.evaluate_candidate(fitted, split).reasons)

    def test_TC11_train_frozen_support_exact_exclusions_and_feature_names(self):
        rows = history_fixture()
        rows[610]["product"] = "never-trained"
        rows[620]["series"] = "never-trained"
        rows[810]["year_established"] = 2000
        rows[820]["account_match"] = "left_only"
        split = s.split_closed_history(rows)
        full = s.fit_candidate(split, "logistic", "full")
        fallback = s.fit_candidate(split, "logistic", "fallback")
        excluded_cal = dict(full.evidence[1].excluded)
        self.assertIn("unseen_product", excluded_cal["00610"])
        self.assertIn("unseen_series", excluded_cal["00620"])
        self.assertEqual(dict(full.evidence[2].excluded)["00810"], ("year_outside_training_support",))
        self.assertEqual(dict(full.evidence[2].excluded)["00820"], ("unsupported_account_year",))
        self.assertEqual(fallback.evidence[2].count, 200)
        self.assertEqual(full.evidence[2].count, 198)
        self.assertEqual(full.support.year_max, 1992)
        scaler = full.pipeline.named_steps["preprocessor"].named_transformers_["numeric"]
        self.assertAlmostEqual(scaler.mean_[0], 1991.)
        for fitted in (full, fallback):
            for name in fitted.feature_names:
                self.assertTrue(name.startswith(("categorical__product_", "categorical__series_", "numeric__year_established")))
            self.assertNotIn("never-trained", " ".join(fitted.feature_names))
            self.assertEqual(sum(period.count+len(period.excluded) for period in fitted.evidence), len(rows))
        self.assertFalse(any("year" in name for name in fallback.feature_names))

    def test_TC17_calibration_fit_consumes_only_intermediate_ids(self):
        from sklearn.pipeline import Pipeline
        from sklearn.calibration import CalibratedClassifierCV
        pipeline_fit, calibrated_fit = Pipeline.fit, CalibratedClassifierCV.fit
        seen = {"train": [], "calibration": []}
        def record_train(model, frame, labels, **kwargs):
            seen["train"].append(tuple(frame.index))
            return pipeline_fit(model, frame, labels, **kwargs)
        def record_calibration(model, frame, labels, **kwargs):
            seen["calibration"].append(tuple(frame.index))
            return calibrated_fit(model, frame, labels, **kwargs)
        split = s.split_closed_history(history_fixture())
        with patch.object(Pipeline, "fit", record_train), patch.object(CalibratedClassifierCV, "fit", record_calibration):
            fitted = s.fit_candidate(split, "logistic", "fallback")
        self.assertEqual(seen["train"], [fitted.evidence[0].ids])
        self.assertEqual(seen["calibration"], [fitted.evidence[1].ids])
        coefficients = fitted.pipeline.named_steps["estimator"].coef_.copy()
        evaluated = s.evaluate_candidate(fitted, split)
        self.assertEqual(evaluated.test_ids, fitted.evidence[2].ids)
        self.assertTrue((coefficients == fitted.pipeline.named_steps["estimator"].coef_).all())
        with self.assertRaisesRegex(ValueError, "Policy changed"):
            s.evaluate_candidate(fitted, split, replace(s.DEFAULT_CONFIG, seed=99))

    def test_controlled_convergence_failure_distinct_from_rejection(self):
        from sklearn.exceptions import ConvergenceWarning
        split = s.split_closed_history(history_fixture())
        with patch("sklearn.pipeline.Pipeline.fit", side_effect=ConvergenceWarning("fixture nonconvergence")):
            fitted = s.fit_candidate(split, "logistic", "full")
        result = s.evaluate_candidate(fitted, split)
        self.assertEqual(result.status, "failed")
        self.assertIsNone(result.brier)
        self.assertIn("fit_failed:ConvergenceWarning", " ".join(result.reasons))

    def test_TC43_invalid_estimator_probability_fails_without_clipping(self):
        import numpy as np
        split = s.split_closed_history(history_fixture())
        fitted = s.fit_candidate(split, "logistic", "fallback")
        probabilities = np.tile([-.1, 1.1], (len(split.test), 1))
        with patch.object(fitted.calibrated, "predict_proba", return_value=probabilities):
            result = s.evaluate_candidate(fitted, split)
        self.assertEqual(result.status, "failed")
        self.assertIsNone(result.brier)
        self.assertFalse(result.bands)
        self.assertIn("invalid_probability", " ".join(result.reasons))


class PublicationPolicyTests(unittest.TestCase):
    def test_TC18_probability_publication_decision_table(self):
        periods, bands = period_fixture(), evaluation_fixture().bands
        for name, brier, loss, selected_bands, allowed in (
            ("all_pass", .15, .4, bands, True),
            ("brier_equal", .25, .4, bands, False),
            ("loss_equal", .15, .69, bands, False),
            ("one_band", .15, .4, bands[:1], False),
            ("bad_populated", .15, .4, (replace(bands[0], supported=False), bands[2]), False),
            ("nonmonotonic", .15, .4, (replace(bands[0], observed_rate=.9), bands[2]), False)):
            with self.subTest(name=name):
                self.assertEqual(not s.publication_reasons(periods, brier, loss, .25, .69, selected_bands), allowed)

    def test_TC19_loss_equality_strict_epsilon_boundaries(self):
        periods, bands = period_fixture(), evaluation_fixture().bands
        epsilon = s.DEFAULT_CONFIG.comparison_epsilon
        for metric in ("brier", "log_loss"):
            for difference in (-2*epsilon, 0., epsilon/2, 2*epsilon):
                with self.subTest(metric=metric, baseline_difference=difference):
                    brier, loss = (.25-difference, .4) if metric == "brier" else (.15, .69-difference)
                    reasons = s.publication_reasons(periods, brier, loss, .25, .69, bands)
                    self.assertEqual(f"{metric}_not_strictly_better" not in reasons, difference > epsilon)

    def test_TC20_band_edges_support_and_coherence_boundaries(self):
        for cutoff, lower, upper in ((.4,"baixa","media"),(.7,"media","alta")):
            for delta, expected in ((-1e-12,lower),(0.,upper),(1e-12,upper)):
                with self.subTest(cutoff=cutoff, delta=delta):
                    self.assertEqual(s.probability_band(cutoff+delta), expected)
        for n in (29,30,31):
            evidence = s.band_evidence([0]*n,[.1]*n)[0]
            self.assertEqual(evidence.supported, n >= 30)
        for delta in (-1e-12,0.,1e-12):
            evidence = s.band_evidence([0]*30,[.1+delta]*30)[0]
            self.assertEqual(evidence.supported, delta <= 0)
        periods, bands = period_fixture(), evaluation_fixture().bands
        for index, minimum in ((0,200),(1,100),(2,100)):
            for n in (minimum-1,minimum,minimum+1):
                changed = list(periods)
                changed[index] = replace(changed[index], ids=tuple(str(i) for i in range(n)), wins=n//2, losses=n-n//2)
                reasons = s.publication_reasons(changed,.15,.4,.25,.69,bands)
                self.assertEqual(f"{changed[index].period}_support_below_{minimum}" in reasons, n < minimum)
        for n in (19,20,21):
            changed = tuple(replace(item, wins=n, losses=item.count-n) for item in periods)
            reasons = s.publication_reasons(changed,.15,.4,.25,.69,bands)
            self.assertEqual(any("class_support" in reason for reason in reasons), n < 20)

    def test_TC21_candidate_selection_fixed_rule_cohorts_and_failures(self):
        logistic = evaluation_fixture()
        boosting = evaluation_fixture("boosting", brier=.14, log_loss=.39,
            top_k=(s.TopKMetric(.1,10,.6,.4,None),s.TopKMetric(.2,20,.6,.6,None)))
        self.assertEqual(s.select_route((logistic,boosting),"full").candidate,"boosting")
        for name, changed in (
            ("precision_equal",replace(boosting,top_k=(replace(boosting.top_k[0],precision=.5),boosting.top_k[1]))),
            ("share_equal",replace(boosting,top_k=(boosting.top_k[0],replace(boosting.top_k[1],realized_value_share=.5)))),
            ("loss_worse",replace(boosting,log_loss=.41)),
            ("rejected",replace(boosting,status="rejected")),
            ("failed",replace(boosting,status="failed")),
            ("financial_missing",replace(boosting,top_k=(replace(boosting.top_k[0],realized_value_share=None,financial_unavailable_reason="missing"),boosting.top_k[1]))),
            ("other_cohort",replace(boosting,periods=boosting.periods[:2]+(replace(boosting.periods[2],ids=("other",)+boosting.test_ids[1:]),))),
            ("other_k",replace(boosting,top_k=(replace(boosting.top_k[0],k=11),boosting.top_k[1])))):
            with self.subTest(name=name):
                self.assertEqual(s.select_route((logistic,changed),"full").candidate,"logistic")
        self.assertIsNone(s.select_route((replace(logistic,status="rejected"),replace(boosting,status="failed")),"full").candidate)
        self.assertEqual(s.select_route((replace(logistic,status="rejected"),boosting),"full").candidate,"boosting")

    def test_TC21_top_k_band_then_expected_catalog_revenue_financial_validity(self):
        cases = (
            # Cheap high-band Won must beat an expensive middle-band Lost.
            ("band_before_value", (1., 10000.), (.8, .6), 0),
            # Same band: 0.7 * 200 > 0.9 * 100, despite lower probability.
            ("same_band_expected_revenue_before_probability", (100., 200.), (.9, .7), 1),
            # Same band: 0.99 * 150 > 0.7 * 200, despite lower catalog price.
            ("same_band_expected_revenue_before_catalog_price", (150., 200.), (.99, .7), 0),
        )
        for name, prices, pair_probabilities, expected_first in cases:
            with self.subTest(ordering=name):
                rows = history_fixture(10)
                for row in rows:
                    row.update(deal_stage="Lost", close_value=0., sales_price=1.)
                for row, price in zip(rows[:2], prices):
                    row["sales_price"] = price
                rows[expected_first].update(deal_stage="Won", close_value=30.)
                # A lower-band Won establishes a total of 100 without entering top 2.
                rows[2].update(deal_stage="Won", close_value=70.)
                probabilities = pair_probabilities+(.1,)*8
                top = s.ranking_metrics(rows, probabilities)
                # Reversing the competitors now gives precision 0 and value share 0.
                self.assertEqual((top[0].k, top[0].precision, top[0].realized_value_share),
                                 (1, 1., .3))
                self.assertEqual((top[1].k, top[1].precision, top[1].realized_value_share),
                                 (2, .5, .3))
        rows[5]["financial_eligible"] = False
        self.assertTrue(all(item.realized_value_share is None and item.financial_unavailable_reason == "incomplete_financial_labels"
            for item in s.ranking_metrics(rows,probabilities)))
        for row in rows:
            row.update(close_value=0.,financial_eligible=True)
        self.assertEqual(s.ranking_metrics(rows,probabilities)[0].financial_unavailable_reason,"no_positive_realized_total")


class ActivePriorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.history = history_fixture()
        cls.split, cls.fitted, cls.evaluations, cls.selections = s.evaluate_history(cls.history)

    def active(self, opportunity_id, stage="Engaging", **changes):
        row = dict(self.history[0], opportunity_id=opportunity_id, deal_stage=stage,
            eligible_history=False, eligible_active=True, close_date=None,
            close_value=None, financial_eligible=False)
        row.update(changes)
        return row

    def score(self, rows, *, selections=None, diagnostics=()):
        return s.score_active(tuple(self.history) + tuple(rows), self.fitted, self.evaluations,
            self.selections if selections is None else selections,
            "fixture-fingerprint", diagnostics)

    def test_TC15_full_then_fallback_routing_without_account_imputation(self):
        full = self.active("full")
        fallback = self.active("fallback", account=None, account_match="left_only",
            year_established=None, route="fallback")
        full_score, fallback_score = self.score((full, fallback))
        self.assertEqual((full_score.route, fallback_score.route), ("full", "fallback"))
        self.assertEqual((full_score.origin, fallback_score.origin), ("logistic", "logistic"))
        fallback_fit = next(item for item in self.fitted
                            if item.candidate == "logistic" and item.route == "fallback")
        self.assertFalse(any("year_established" in name for name in fallback_fit.feature_names))

        # A full-route account outside trained year support degrades through the
        # deliberate account-free feature contract instead of mean imputation.
        out_of_support = self.active("year-fallback", year_established=1800, route="full")
        score = self.score((out_of_support,))[0]
        self.assertEqual(score.route, "fallback")
        self.assertTrue(any(item["code"] == "full_route_unsupported" for item in score.diagnostics))

    def test_TC12_TC16_engaging_score_is_invariant_to_forbidden_context(self):
        original = self.active("context-a")
        changed = self.active("context-b", sales_agent="seller-other", manager="manager-other",
                              regional_office="region-other", close_date=date(2099, 1, 1),
                              close_value=999_999.)
        left, right = self.score((original, changed))
        for field in ("state", "route", "origin", "band", "probability",
                      "expected_revenue", "relative_index", "explanation_scale", "base_value"):
            with self.subTest(field=field):
                self.assertEqual(getattr(left, field), getattr(right, field))
        self.assertEqual(tuple(item.contribution for item in left.factors),
                         tuple(item.contribution for item in right.factors))

    def test_TC24_rejected_routes_suppress_probability_and_expected_revenue(self):
        rejected = tuple(replace(item, status="rejected", reasons=("fixture_rejection",))
                         for item in self.evaluations)
        selections = tuple(s.select_route(rejected, route) for route in ("full", "fallback"))
        scores = s.score_active((self.active("engaging"),), self.fitted, rejected,
                                selections, "fixture-fingerprint")
        payload = scores[0].to_dict()
        self.assertEqual(payload["state"], "relative")
        self.assertNotIn("probability", payload)
        self.assertNotIn("expected_revenue", payload)
        self.assertTrue(any(item["code"] == "probability_suppressed"
                            for item in payload["diagnostics"]))

    def test_TC25_prospecting_nested_smoothing_is_hand_reconstructable(self):
        history = []
        for index in range(40):
            product = "A" if index < 20 else "B"
            won = index < 15 or 20 <= index < 25
            history.append(dict(opportunity_id=f"h-{index}", deal_stage="Won" if won else "Lost",
                close_date=date(2020, 1, 1), eligible_history=True, product=product,
                sales_agent="seller-a" if product == "A" else "seller-b",
                account="account-a" if product == "A" else "account-b"))
        prospect = self.active("prospect", "Prospecting", product="A", sales_agent="seller-a",
                               account="account-a", sales_price=200.)
        result = s.score_prospecting(prospect, history, "fixture-fingerprint")
        expected = (15 + 20 * ((15 + 20 * ((15 + 20 * .5) / 40)) / 40)) / 40
        self.assertAlmostEqual(result.relative_index, expected)
        self.assertAlmostEqual(result.base_value + sum(f.contribution for f in result.factors), expected)
        self.assertEqual((result.observed_n, result.prior_strength, result.effective_support), (20, 20., 40.))
        self.assertEqual(result.band, "alta")

    def test_TC26_sparse_backoff_and_support_boundaries(self):
        self.assertAlmostEqual(s.smoothed_rate(1, 1, .5, 20), 11/21)
        self.assertAlmostEqual(s.smoothed_rate(0, 0, .5, 20), .5)
        with self.assertRaisesRegex(ValueError, "counts"):
            s.smoothed_rate(0, -1, .5, 20)
        with self.assertRaisesRegex(ValueError, "strength"):
            s.smoothed_rate(0, 1, .5, 0)

        history = [dict(opportunity_id=f"h-{i}", deal_stage="Won" if i % 2 else "Lost",
            close_date=date(2020, 1, 1), eligible_history=True, product="other",
            sales_agent="other", account="other") for i in range(30)]
        history.append(dict(opportunity_id="only-one", deal_stage="Won", close_date=date(2020, 1, 1),
            eligible_history=True, product="rare", sales_agent="rare", account="rare"))
        result = s.score_prospecting(self.active("rare", "Prospecting", product="rare",
            sales_agent="rare", account="rare"), history, "fixture-fingerprint")
        self.assertEqual(result.backoff_path[-1], "selected:global")
        self.assertEqual(result.prior_strength, 0.)
        self.assertTrue(any("observed_n=1<20" in item for item in result.backoff_path))

    def test_TC20_degraded_margin_quantile_boundaries_and_equal_cutoffs(self):
        for value, expected in ((1-1e-12, "baixa"), (1., "media"),
                                (2-1e-12, "media"), (2., "alta")):
            with self.subTest(value=value):
                self.assertEqual(s._margin_band(value, (0., 3.), s.DEFAULT_CONFIG), expected)
        self.assertEqual(s._margin_band(1., (1., 1., 1.), s.DEFAULT_CONFIG), "media")

    def test_TC27_prospecting_contract_never_exposes_probability_revenue(self):
        prospect = self.active("prospect", "Prospecting")
        result = self.score((prospect,))[0]
        payload = result.to_dict()
        self.assertEqual(result.origin, "historical_evidence")
        self.assertEqual(result.potential_revenue, 100.)
        self.assertIn(result.evidence_strength, ("fraca", "moderada", "forte"))
        self.assertNotIn("probability", payload)
        self.assertNotIn("expected_revenue", payload)

    def test_TC28_logistic_raw_and_calibrated_affine_reconstruct_outputs(self):
        fitted = next(item for item in self.fitted
                      if item.candidate == "logistic" and item.route == "full")
        row = self.active("explain-logistic")
        scale, base, factors = s.explain_score(fitted, row)
        actual = float(fitted.pipeline.decision_function(s.feature_frame((row,), "full"))[0])
        self.assertEqual(scale, "raw_margin")
        self.assertAlmostEqual(base + sum(item.contribution for item in factors), actual, places=8)

        for slope in (0., -2.):
            transformed_base, transformed = s.apply_calibration_explanation(base, factors, slope, .3)
            reconstructed = transformed_base + sum(item.contribution for item in transformed)
            self.assertAlmostEqual(reconstructed, -(slope * actual + .3), places=8)
            self.assertTrue(all(item.reference.endswith("log-odds calibrado") for item in transformed))

    def test_TC29_boosting_tree_paths_reconstruct_raw_margin(self):
        fitted = next(item for item in self.fitted
                      if item.candidate == "boosting" and item.route == "fallback")
        row = self.active("explain-tree", route="fallback", account_match="left_only",
                          year_established=None)
        scale, base, factors = s.explain_score(fitted, row)
        actual = float(fitted.pipeline.decision_function(s.feature_frame((row,), "fallback"))[0])
        self.assertEqual(scale, "raw_margin")
        self.assertAlmostEqual(base + sum(item.contribution for item in factors), actual, places=8)

    def test_TC30_factor_summary_preserves_value_sign_and_absent_direction(self):
        factors = (s.Factor("product", "A", .4, "favoravel", "ref", True),
                   s.Factor("series", "B", -.2, "desfavoravel", "ref", True))
        summary = s.summarize_factors(factors)
        self.assertEqual(summary["favoraveis"][0].observed_value, "A")
        self.assertEqual(summary["desfavoraveis"][0].contribution, -.2)
        absent = s.summarize_factors((factors[0],))
        self.assertEqual(absent["mensagem_desfavoravel"], "Sem fator desfavorável sustentado")
        self.assertEqual(s.summarize_factors((factors[1],))["mensagem_favoravel"],
                         "Sem fator favorável sustentado")

    def test_TC31_TC32_versioned_playbook_uses_only_actionable_evidence(self):
        cases = (
            ("Engaging", "product", "Confirmar com a conta se o produto atende à necessidade e combinar o próximo passo comercial"),
            ("Engaging", "series", "Confirmar com a conta se o produto atende à necessidade e combinar o próximo passo comercial"),
            ("Prospecting", "product", "Validar a necessidade para este produto antes de avançar para engajamento"),
            ("Prospecting", "series", "Validar a necessidade para este produto antes de avançar para engajamento"),
        )
        for stage, field, action in cases:
            with self.subTest(stage=stage, field=field):
                factor = s.Factor(field, "observado", .2, "favoravel", "ref", True)
                self.assertEqual(s.recommend_action(stage, (factor,)), action)
        no_action = "Sem ação recomendada com os dados atuais"
        for factors in ((), (s.Factor("account", "A", 3., "favoravel", "ref", False),),
                        (s.Factor("product", "A", 1e-13, "favoravel", "ref", True),)):
            self.assertEqual(s.recommend_action("Engaging", factors), no_action)

    def test_TC22_TC23_band_first_partitioned_ranking_and_lexical_ties(self):
        low_expensive = score_fixture(opportunity_id="z-low", band="baixa", probability=.39,
                                      expected_revenue=390000., potential_revenue=1_000_000.)
        high_cheap = score_fixture(opportunity_id="a-high", band="alta", probability=.7,
                                   expected_revenue=7., potential_revenue=10.)
        tied_b = score_fixture(opportunity_id="b-tie", band="media", probability=.5,
                               expected_revenue=50., potential_revenue=100.)
        tied_a = replace(tied_b, opportunity_id="a-tie")
        ranked = s.rank_stage((low_expensive, tied_b, high_cheap, tied_a), "Engaging")
        self.assertEqual([item.opportunity_id for item in ranked],
                         ["a-high", "a-tie", "b-tie", "z-low"])

        relative_a = score_fixture("relative", opportunity_id="z", route="full",
                                   origin="logistic", relative_index=999.)
        relative_b = score_fixture("relative", opportunity_id="a", route="fallback",
                                   origin="logistic", relative_index=-999.)
        relative_c = replace(relative_a, opportunity_id="a2", relative_index=1000.)
        ranked = s.rank_stage((relative_a, relative_b, relative_c), "Engaging")
        self.assertEqual([item.opportunity_id for item in ranked], ["a", "a2", "z"])

    def test_TC42_seeded_active_scores_are_deterministic_and_stage_safe(self):
        rows = tuple(self.active(f"e-{i}", sales_price=float(1+i)) for i in range(20)) + tuple(
            self.active(f"p-{i}", "Prospecting", sales_price=float(1+i)) for i in range(20))
        first = self.score(rows)
        second = self.score(tuple(reversed(rows)))
        first_by_id = {item.opportunity_id: item.to_dict() for item in first}
        second_by_id = {item.opportunity_id: item.to_dict() for item in second}
        self.assertEqual(first_by_id, second_by_id)
        for result in first:
            payload = result.to_dict()
            if result.state == "calibrated":
                self.assertTrue(math.isfinite(result.probability) and 0 <= result.probability <= 1)
            if result.stage == "Prospecting":
                self.assertNotIn("probability", payload)
                self.assertNotIn("expected_revenue", payload)

    def test_TC08_TC23_unsupported_active_is_retained_without_invented_score(self):
        row = self.active("unsupported", eligible_active=False, input_status="unsupported_active",
                          product=None, product_match="left_only")
        issue = SimpleNamespace(code="unknown_key", scope="row", file="sales_pipeline.csv",
            opportunity_id="unsupported", field="product", reason="Produto desconhecido",
            correction="Corrija product usando o catálogo")
        result = self.score((row,), diagnostics=(issue,))[0]
        self.assertEqual(result.state, "insufficient_data")
        self.assertEqual(result.opportunity_id, "unsupported")
        self.assertIsNone(result.band)
        self.assertEqual(result.diagnostics[0]["field"], "product")


class ZRealDataEvaluationTests(unittest.TestCase):
    def test_TC14_real_four_routes_frozen_policy_and_complete_evidence(self):
        import data
        # Freeze/check the dependency and policy identities before final-set access.
        self.assertEqual(hashlib.sha256((ROOT/"requirements.txt").read_bytes()).hexdigest(), s.DEFAULT_CONFIG.dependency_digest)
        frozen = s.DEFAULT_CONFIG.fingerprint
        print("FROZEN_POLICY", frozen, "DEPENDENCIES", s.DEFAULT_CONFIG.dependency_digest, flush=True)
        dataset = data.load_dataset(data.read_snapshot(ROOT/"data/raw", ROOT/"data/manifest.json"))
        split, fitted, evaluations, selections = s.evaluate_history(dataset.opportunities)
        self.assertEqual(s.DEFAULT_CONFIG.fingerprint,frozen)
        self.assertEqual({(item.candidate,item.route) for item in evaluations},
            {(candidate,route) for candidate in ("logistic","boosting") for route in ("full","fallback")})
        self.assertTrue(all(item.status in ("passed","rejected","failed") for item in evaluations))
        self.assertTrue(all(item.status != "failed" for item in evaluations), [(item.candidate,item.route,item.reasons) for item in evaluations])
        self.assertEqual(len(selections),2)
        for item, model in zip(evaluations,fitted):
            self.assertEqual(item.split_fingerprint,split.fingerprint)
            self.assertEqual(item.config_fingerprint,frozen)
            self.assertEqual(item.periods,model.evidence)
            self.assertEqual(item.natural_missing_account_count,0)
            self.assertTrue(item.limitations)
            self.assertIsNotNone(item.brier)
            self.assertIsNotNone(item.baseline_brier)
            self.assertEqual(len(item.bands),3)
            self.assertEqual(len(item.top_k),2)
            self.assertTrue(item.segments)
            self.assertEqual(item.baseline_rate,item.periods[0].wins/item.periods[0].count)
            if item.status == "rejected":
                self.assertTrue(item.reasons)
        summaries = [dict(candidate=item.candidate, route=item.route, status=item.status,
            evaluation_id=item.evaluation_id, split_fingerprint=item.split_fingerprint,
            feature_fingerprint=item.feature_fingerprint, counts=[p.count for p in item.periods],
            exclusions=[len(p.excluded) for p in item.periods], brier=item.brier,
            log_loss=item.log_loss, baseline_brier=item.baseline_brier,
            baseline_log_loss=item.baseline_log_loss, bands=s.serialize(item.bands),
            top_k=s.serialize(item.top_k), reasons=item.reasons,
            natural_missing_account_count=item.natural_missing_account_count) for item in evaluations]
        print("REAL_EVALUATIONS",json.dumps(summaries,sort_keys=True,allow_nan=False),flush=True)
        print("REAL_SELECTIONS",json.dumps(s.serialize(selections),sort_keys=True),flush=True)

        bundle = s.build_scoring_bundle(dataset)
        active = dataset.opportunities[dataset.opportunities["deal_stage"].isin(("Engaging", "Prospecting"))]
        self.assertEqual(len(bundle.scores), len(active))
        self.assertEqual(len({item.opportunity_id for item in bundle.scores}), len(bundle.scores))
        self.assertTrue(all(item.state in ("relative", "insufficient_data") for item in bundle.scores))
        self.assertTrue(all("probability" not in item.to_dict() and
                            "expected_revenue" not in item.to_dict() for item in bundle.scores))
        self.assertEqual({item.origin for item in bundle.scores if item.stage == "Prospecting"},
                         {"historical_evidence"})
        print("REAL_ACTIVE_SCORES", json.dumps({"count": len(bundle.scores),
            "states": {state: sum(item.state == state for item in bundle.scores)
                       for state in ("relative", "insufficient_data")},
            "fingerprint": bundle.fingerprint,
            "source_identity": s.serialize(bundle.source_identity)},
            sort_keys=True, allow_nan=False), flush=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
