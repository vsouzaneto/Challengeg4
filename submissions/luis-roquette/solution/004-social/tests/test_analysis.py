from __future__ import annotations

import csv
from copy import deepcopy
import sys
import time
import unittest

import pandas as pd

from analysis import METHOD_VERSION, align_scope_timestamp, analyze, content_strategy_30d, derive_metrics, executive_answers, export_evidence, follower_band, load_csv, sponsorship_break_even
from tests.helpers import (
    aggregate_effect_rows,
    alert_for_target,
    concentrated_reference,
    csv_bytes,
    default_scope,
    default_scope_all_history,
    driver_rows,
    duplicate_driver_context,
    frame_from_rows,
    frame_with_target,
    make_cohort,
    make_post,
    monthly_sponsorship_frequency_rows,
    monthly_sponsorship_rows,
    sponsorship_frequency_rows,
    sponsorship_rows,
)


def result_with_stable_driver() -> dict[str, object]:
    rows = driver_rows([1.0, 1.2, 0.8])
    return analyze(frame_from_rows(rows), default_scope_all_history(rows), "hash")


def result_without_stable_driver() -> dict[str, object]:
    rows = driver_rows([1.0, -1.0, 1.0, -1.0])
    return analyze(frame_from_rows(rows), default_scope_all_history(rows), "hash")


class CsvBoundaryTests(unittest.TestCase):
    def test_load_csv_accepts_valid_single_platform_subset(self):
        frame, errors = load_csv(csv_bytes([make_post(platform="Instagram")]))
        self.assertEqual(errors, [])
        self.assertEqual(frame["platform"].unique().tolist(), ["Instagram"])

    def test_executive_answers_have_four_complete_unambiguous_decisions(self):
        frame = frame_from_rows([
            make_post(id="text", content_id="text", content_type="text", likes=9, shares=0, comments_count=0),
            make_post(id="video", content_id="video", content_type="video", likes=3, shares=0, comments_count=0),
        ])
        result = analyze(frame, {"include_post_alerts": False}, str(frame["source_hash"].iloc[0]))
        answers = executive_answers(result)
        self.assertEqual([item["question"] for item in answers], [
            "O que gera engajamento?", "Vale patrocinar influenciadores?", "Qual deve ser a estratégia?",
            "Qual perfil de audiência mais engaja?",
        ])
        self.assertTrue(all(set(item) == {
            "question", "verdict", "kpi", "comparison", "sample", "action",
            "strength", "coverage", "stability", "evidence_id", "change_trigger",
        }
                            and all(item.values()) for item in answers))
        self.assertIn("NÃO EXISTE VENCEDOR SUSTENTADO", answers[0]["verdict"])
        self.assertEqual(answers[1]["verdict"], "NÃO ESCALAR PATROCÍNIO AGORA")
        self.assertIn("COLETAR", answers[2]["verdict"])
        self.assertIn("NÃO HÁ PERFIL GLOBAL COMPROVADO", answers[3]["verdict"])

    def test_load_csv_reports_missing_required_column_without_partial_frame(self):
        row = make_post()
        del row["views"]
        frame, errors = load_csv(csv_bytes([row]))
        self.assertIsNone(frame)
        self.assertEqual(errors[0]["column"], "views")

    def test_load_csv_reports_negative_nonfinite_and_duplicate_identity(self):
        invalid = [
            make_post(id="1", content_id="a", views=-1),
            make_post(id="1", content_id="b", views="NaN"),
        ]
        frame, errors = load_csv(csv_bytes(invalid))
        self.assertIsNone(frame)
        self.assertEqual({error["column"] for error in errors}, {"id", "views"})

    def test_load_csv_accepts_zero_metrics_and_utf8_bom(self):
        raw = b"\xef\xbb\xbf" + csv_bytes(
            [make_post(views=0, likes=0, shares=0, comments_count=0)]
        )
        frame, errors = load_csv(raw)
        self.assertEqual(errors, [])
        self.assertEqual(int(frame.iloc[0]["views"]), 0)

    def test_load_csv_rejects_over_fifty_mib_before_parse(self):
        frame, errors = load_csv(b"x" * (50 * 1024 * 1024 + 1))
        self.assertIsNone(frame)
        self.assertEqual(errors[0]["problem"], "file_too_large")

    def test_load_csv_accepts_large_optional_text_and_restores_field_limit(self):
        original_limit = csv.field_size_limit()
        csv.field_size_limit(131_072)
        try:
            raw = csv_bytes([make_post(comments_text="x" * 140_000)])
            frame, errors = load_csv(raw)
            self.assertEqual(errors, [])
            self.assertIsNotNone(frame)
            self.assertEqual(len(frame.iloc[0]["comments_text"]), 140_000)
            self.assertEqual(csv.field_size_limit(), 131_072)
        finally:
            csv.field_size_limit(original_limit)

    def test_load_csv_rejects_mixed_timezone_semantics(self):
        raw = csv_bytes(
            [
                make_post(id="1", content_id="a", post_date="2025-01-01T00:00:00"),
                make_post(id="2", content_id="b", post_date="2025-01-02T00:00:00Z"),
            ]
        )
        frame, errors = load_csv(raw)
        self.assertIsNone(frame)
        self.assertEqual(errors[0]["column"], "post_date")

    def test_load_csv_rejects_nat_and_incompatible_timezone_offsets(self):
        cases = (
            [make_post(post_date="NaT")],
            [
                make_post(id="1", content_id="a", post_date="2025-01-01T00:00:00+00:00"),
                make_post(id="2", content_id="b", post_date="2025-01-02T00:00:00-03:00"),
            ],
        )
        for rows in cases:
            with self.subTest(rows=rows):
                frame, errors = load_csv(csv_bytes(rows))
                self.assertIsNone(frame)
                self.assertTrue(any(error["column"] == "post_date" for error in errors))

    def test_load_csv_returns_diagnostic_for_integer_outside_int64(self):
        frame, errors = load_csv(csv_bytes([make_post(views=2**63)]))
        self.assertIsNone(frame)
        self.assertEqual(errors[0]["row"], 2)
        self.assertEqual(errors[0]["column"], "views")
        self.assertEqual(errors[0]["problem"], "integer_out_of_range")

    def test_load_csv_rejects_nul_in_any_field_without_second_interpretation(self):
        for column in ("views", "id", "comments_text"):
            with self.subTest(column=column):
                frame, errors = load_csv(csv_bytes([make_post(**{column: "1\x002"})]))
                self.assertIsNone(frame)
                self.assertEqual(errors[0]["row"], 2)
                self.assertEqual(errors[0]["column"], column)
                self.assertEqual(errors[0]["problem"], "nul_character")

    def test_integer_grammar_is_exact_above_float_precision(self):
        exact = 9_007_199_254_740_993
        frame, errors = load_csv(csv_bytes([make_post(views=str(exact))]))
        self.assertEqual(errors, [])
        self.assertEqual(int(frame.iloc[0]["views"]), exact)
        for value in (f"{exact}.0", "1e3", "+1", " 1"):
            with self.subTest(value=value):
                rejected, diagnostics = load_csv(csv_bytes([make_post(views=value)]))
                self.assertIsNone(rejected)
                self.assertEqual(diagnostics[0]["problem"], "invalid_nonnegative_integer")

    def test_integer_range_is_checked_lexically_before_python_conversion(self):
        digit_limit = sys.get_int_max_str_digits()
        huge_zero = "0" * 5_000
        frame, errors = load_csv(csv_bytes([make_post(views=huge_zero)]))
        self.assertEqual(errors, [])
        self.assertEqual(int(frame.iloc[0]["views"]), 0)

        frame, errors = load_csv(csv_bytes([make_post(views="9" * 5_000)]))
        self.assertIsNone(frame)
        self.assertEqual(errors[0]["row"], 2)
        self.assertEqual(errors[0]["column"], "views")
        self.assertEqual(errors[0]["problem"], "integer_out_of_range")
        frame, errors = load_csv(csv_bytes([make_post(views="0" * 5_000 + str(2**63))]))
        self.assertIsNone(frame)
        self.assertEqual(errors[0]["problem"], "integer_out_of_range")
        self.assertEqual(sys.get_int_max_str_digits(), digit_limit)

    def test_date_grammar_rejects_relative_and_unknown_timezone_values(self):
        for value in (
            "today", "now", "2025-01-15 12:00 XYZ", "2025-01-15T12:00:00+15:00",
            "2025-01-15T12:00:00+00:99", "2025-01-15T12:00:00+13:60",
            "2025-01-15T12:00:00-00:99", "2025-01-15T12:00:00+14:01",
        ):
            with self.subTest(value=value):
                frame, errors = load_csv(csv_bytes([make_post(post_date=value)]))
                self.assertIsNone(frame)
                self.assertEqual(errors[0]["row"], 2)
                self.assertEqual(errors[0]["column"], "post_date")
                self.assertEqual(errors[0]["problem"], "invalid_date")

        accepted = (
            "05/29/23 12:15 AM",
            "2025-01-15",
            "2025-01-15T12:00:00.123456789",
            "2025-01-15T12:00:00.123456789+02:00",
            "2025-01-15T12:00:00Z",
            "2025-01-15T12:00:00-0300",
            "2025-01-15T12:00:00+01:30",
            "2025-01-15T12:00:00+14:00",
            "2025-01-15T12:00:00-1400",
        )
        for value in accepted:
            with self.subTest(value=value):
                frame, errors = load_csv(csv_bytes([make_post(post_date=value)]))
                self.assertEqual(errors, [])
                self.assertIsNotNone(frame)

    def test_operational_date_range_supports_all_derived_windows(self):
        lower = "1971-01-01T12:00:00"
        upper = "2262-04-10T12:00:00"
        for rejected in ("1677-09-22T12:00:00", "2262-04-11T12:00:00"):
            with self.subTest(rejected=rejected):
                frame, errors = load_csv(csv_bytes([make_post(post_date=rejected)]))
                self.assertIsNone(frame)
                self.assertEqual(errors[0]["problem"], "date_out_of_operational_range")

        lower_frame, errors = load_csv(csv_bytes([make_post(post_date=lower)]))
        self.assertEqual(errors, [])
        self.assertEqual(analyze(lower_frame, {}, "lower")["metrics"]["posts"], 1)

        upper_frame, errors = load_csv(csv_bytes([make_post(post_date=upper)]))
        self.assertEqual(errors, [])
        custom = default_scope(target_start="2262-04-10", target_end="2262-04-10")
        self.assertEqual(analyze(upper_frame, custom, "upper")["metrics"]["posts"], 1)

        history, errors = load_csv(csv_bytes([
            make_post(id="lower", content_id="lower", post_date=lower),
            make_post(id="upper", content_id="upper", post_date=upper),
        ]))
        self.assertEqual(errors, [])
        result = analyze(
            history,
            default_scope(target_start="1971-01-01", target_end="2262-04-10", reference_date=upper),
            "history",
        )
        self.assertEqual(result["metrics"]["posts"], 2)

    def test_load_csv_rejects_dates_outside_nanosecond_range(self):
        for value in ("0001-01-01", "9999-01-01"):
            with self.subTest(value=value):
                frame, errors = load_csv(csv_bytes([make_post(post_date=value)]))
                self.assertIsNone(frame)
                self.assertEqual(errors[0]["column"], "post_date")
                self.assertEqual(errors[0]["problem"], "invalid_date")

    def test_load_csv_accepts_one_explicit_offset_with_datetime_dtype(self):
        raw = csv_bytes([
            make_post(id="1", content_id="a", post_date="2025-01-01T00:00:00+02:00"),
            make_post(id="2", content_id="b", post_date="2025-01-02T00:00:00+02:00"),
        ])
        frame, errors = load_csv(raw)
        self.assertEqual(errors, [])
        self.assertTrue(str(frame["post_date"].dtype).startswith("datetime64"))
        explicit_scope = {
            "target_start": "2025-01-01",
            "target_end": "2025-01-02",
            "reference_date": "2025-01-02",
            "filters": {},
        }
        result = analyze(frame, explicit_scope, str(frame.iloc[0]["source_hash"]))
        self.assertEqual(result["source"]["rows"], 2)
        self.assertTrue(str(result["scope"]["target_start"]).endswith("+02:00"))
        aligned = align_scope_timestamp(pd.Timestamp("2025-01-01"), frame["post_date"])
        self.assertEqual(aligned.isoformat(), "2025-01-01T00:00:00+02:00")

    def test_scope_includes_last_nanosecond_with_semi_open_end(self):
        frame, errors = load_csv(
            csv_bytes([make_post(post_date="2025-01-01T23:59:59.999999999")])
        )
        self.assertEqual(errors, [])
        result = analyze(
            frame,
            default_scope(target_start="2025-01-01", target_end="2025-01-01"),
            str(frame.iloc[0]["source_hash"]),
        )
        self.assertEqual(result["metrics"]["posts"], 1)
        self.assertEqual(result["scope"]["target_end_exclusive"], "2025-01-02T00:00:00")

    def test_load_csv_diagnostics_use_physical_line_after_multiline_field(self):
        raw = csv_bytes([
            make_post(id="1", content_id="a", content_description="linha 1\nlinha 2"),
            make_post(id="2", content_id="b", content_description="simples", views=-1, post_date="invalid"),
        ])
        frame, errors = load_csv(raw)
        self.assertIsNone(frame)
        locations = {(error["column"], error["row"]) for error in errors}
        self.assertIn(("views", 4), locations)
        self.assertIn(("post_date", 4), locations)

    def test_load_csv_rejects_empty_malformed_and_duplicate_headers(self):
        for raw in (b"", b'"unterminated', b"id,id,platform\n1,2,Instagram\n"):
            with self.subTest(raw=raw[:20]):
                frame, errors = load_csv(raw)
                self.assertIsNone(frame)
                self.assertTrue(errors)

    def test_metrics_use_views_denominator_and_preserve_undefined_rate(self):
        frame, _ = load_csv(
            csv_bytes(
                [
                    make_post(id="1", content_id="a", views=100, likes=5, shares=3, comments_count=2),
                    make_post(id="2", content_id="b", views=0, likes=0, shares=0, comments_count=0),
                ]
            )
        )
        result = derive_metrics(frame)
        self.assertEqual(int(result.iloc[0]["interactions"]), 10)
        self.assertEqual(float(result.iloc[0]["erv"]), 10.0)
        self.assertTrue(pd.isna(result.iloc[1]["erv"]))

    def test_int64_boundaries_do_not_wrap_derived_or_aggregate_metrics(self):
        maximum = 2**63 - 1
        frame, errors = load_csv(
            csv_bytes(
                [
                    make_post(
                        id=f"boundary-{index}",
                        content_id=f"boundary-content-{index}",
                        creator_id=f"boundary-creator-{index}",
                        views=maximum,
                        likes=maximum,
                        shares=1,
                        comments_count=0,
                        follower_count=maximum,
                    )
                    for index in range(2)
                ]
            )
        )
        self.assertEqual(errors, [])
        derived = derive_metrics(frame)
        self.assertEqual(int(derived.iloc[0]["interactions"]), maximum + 1)
        self.assertGreater(float(derived.iloc[0]["erv"]), 99.0)

        result = analyze(frame, default_scope(), str(frame.iloc[0]["source_hash"]))
        self.assertEqual(result["metrics"]["views"], 2 * maximum)
        self.assertEqual(result["metrics"]["interactions"], 2 * (maximum + 1))
        self.assertEqual(result["metrics"]["creator_exposure"], 2 * maximum)
        self.assertGreater(result["metrics"]["weighted_erv"], 99.0)
        platform = result["dimensions"]["platform"][0]
        self.assertEqual(platform["views"], 2 * maximum)
        self.assertEqual(platform["interactions"], 2 * (maximum + 1))
        self.assertEqual(platform["creator_exposure"], 2 * maximum)

    def test_follower_band_boundaries(self):
        values = [0, 9_999, 10_000, 49_999, 50_000, 99_999, 100_000, 499_999, 500_000]
        self.assertEqual(
            [follower_band(value) for value in values],
            ["0–9,999", "0–9,999", "10,000–49,999", "10,000–49,999", "50,000–99,999", "50,000–99,999", "100,000–499,999", "100,000–499,999", "500,000+"],
        )


class ContextEvidenceTests(unittest.TestCase):
    def test_break_even_calculates_thresholds_from_manual_assumptions(self):
        evidence = {
            "evidence_id": "sponsorship-test",
            "context": {
                "platform": "YouTube", "content_type": "mixed",
                "content_category": "finance", "follower_band": "10,000–49,999",
                "period_month": "2025-01",
            },
            "sponsored": {"median_views_per_post": 10_000},
        }
        original = deepcopy(evidence)
        scenario = sponsorship_break_even(evidence, {
            "sponsorship_cost": 1_000, "incremental_production_cost": 200,
            "value_per_conversion": 100, "organic_conversion_rate": .01,
            "sponsored_conversion_rate": .013,
        })
        self.assertEqual(scenario["incremental_conversions"], 30)
        self.assertEqual(scenario["max_sponsorship_cost"], 2_800)
        self.assertEqual(scenario["required_uplift_pp"], 0.12)
        self.assertEqual(scenario["status"], "meets_break_even_scenario")
        self.assertEqual(evidence, original)

    def test_break_even_abstains_on_missing_or_invalid_inputs(self):
        invalid = {
            "sponsorship_cost": -1, "value_per_conversion": 0,
            "organic_conversion_rate": 0, "sponsored_conversion_rate": 1.01,
        }
        scenario = sponsorship_break_even({"sponsored": {"median_views_per_post": 0}}, invalid)
        self.assertEqual(scenario["status"], "invalid_or_missing_assumptions")
        self.assertTrue(scenario["missing"])

    def test_sponsorship_answer_names_best_and_worst_comparable_contexts(self):
        rows = monthly_sponsorship_rows(3)
        result = analyze(frame_from_rows(rows), default_scope_all_history(rows), "hash")
        answer = executive_answers(result)[1]
        self.assertIn("melhor contexto comparável", answer["comparison"].lower())
        self.assertIn("pior contexto comparável", answer["comparison"].lower())
        self.assertIn("YouTube", answer["comparison"])
        self.assertNotIn(b"value_per_conversion", export_evidence(result, []))

    def test_driver_ranking_requires_multivariate_peers_and_three_eligible_months(self):
        rows = driver_rows([1.0, 1.2, 0.8])
        result = analyze(frame_from_rows(rows), default_scope_all_history(rows), "hash")
        leader = result["engagement_drivers"]["leader"]
        self.assertEqual(leader["context"], {
            "platform": "Instagram", "content_type": "text",
            "content_category": "tech", "follower_band": "10,000–49,999",
        })
        self.assertEqual(leader["eligible_months"], 3)
        self.assertGreaterEqual(leader["stability"], 2 / 3)
        self.assertEqual(set(leader["volume_guard"]), {
            "target_median_views", "peer_median_views", "delta_views",
            "target_median_interactions", "peer_median_interactions", "delta_interactions",
            "status",
        })
        self.assertEqual(result["engagement_drivers"]["laggard"]["context"]["content_type"], "video")

    def test_driver_ranking_abstains_for_unstable_or_immaterial_effect(self):
        for deltas in ([1.0, -1.0, 1.0, -1.0], [0.01, 0.02, 0.01]):
            with self.subTest(deltas=deltas):
                rows = driver_rows(list(deltas))
                ranking = analyze(frame_from_rows(rows), default_scope_all_history(rows), "hash")["engagement_drivers"]
                self.assertIsNone(ranking["leader"])
                self.assertEqual(ranking["verdict"], "no_sustained_winner")

    def test_driver_strength_penalizes_creator_concentration(self):
        balanced_rows = driver_rows([1, 1, 1])
        concentrated_rows = driver_rows([1, 1, 1], concentrated=True)
        balanced = analyze(frame_from_rows(balanced_rows), default_scope_all_history(balanced_rows), "hash")
        concentrated = analyze(frame_from_rows(concentrated_rows), default_scope_all_history(concentrated_rows), "hash")
        balanced_text = next(item for item in balanced["engagement_drivers"]["contexts"] if item["context"]["content_type"] == "text")
        concentrated_text = next(item for item in concentrated["engagement_drivers"]["contexts"] if item["context"]["content_type"] == "text")
        self.assertGreater(balanced_text["strength"], concentrated_text["strength"])

    def test_driver_ranking_is_stable_under_row_shuffle_and_exact_tie(self):
        rows = driver_rows([1, 1, 1])
        tied = duplicate_driver_context(rows, platform="TikTok")
        first_rows = rows + tied
        frame = frame_from_rows(first_rows)
        first = analyze(frame, default_scope_all_history(first_rows), "hash")
        second = analyze(frame.iloc[::-1].copy(), default_scope_all_history(first_rows), "hash")
        self.assertEqual(first["engagement_drivers"], second["engagement_drivers"])

    def test_editorial_uses_same_platform_and_audience_filter_universe(self):
        frames = []
        for platform, location in (("Instagram", "BR"), ("TikTok", "BR"), ("TikTok", "US")):
            frame = aggregate_effect_rows(creators=5)
            frame["platform"] = platform
            frame["audience_location"] = location
            marker = f"{platform}-{location}"
            frame["id"] = [f"{marker}-{index}" for index in range(len(frame))]
            frame["content_id"] = [f"{marker}-content-{index}" for index in range(len(frame))]
            frame["source_row_id"] = [f"hash:{value}" for value in frame["id"]]
            frames.append(frame)
        combined = pd.concat(frames, ignore_index=True)
        scope = default_scope(
            target_start="2025-01-08",
            target_end="2025-01-14",
            filters={"platform": ["TikTok"], "audience_location": ["BR"]},
        )
        result = analyze(combined, scope, "hash")
        self.assertTrue(result["recommendations"])
        self.assertTrue(all(item["context"]["platform"] == "TikTok" for item in result["recommendations"]))
        self.assertTrue(all(item["context"]["audience_location"] == "BR" for item in result["recommendations"]))

    def test_analysis_exposes_auditable_required_dimensions(self):
        frame = frame_from_rows([
            make_post(id="a", content_id="a", platform="Instagram", content_type="video"),
            make_post(id="b", content_id="b", platform="TikTok", content_type="image"),
        ])
        result = analyze(frame, default_scope(target_start="2025-01-15", target_end="2025-01-15"), str(frame.iloc[0]["source_hash"]))
        self.assertEqual(set(result["dimensions"]), {"platform", "content_type", "content_category", "creator_band", "audience_age", "audience_gender", "audience_location", "month"})
        self.assertTrue(all(item["evidence_id"] and item["source_row_ids"] for items in result["dimensions"].values() for item in items))

    def test_post_alert_uses_post_distribution_not_creator_medians(self):
        frame = make_cohort(erv_values=[2, 4, 6, 8, 10, 12] * 5)
        ordinary = analyze(frame_with_target(frame, 8), default_scope(), "hash")
        extreme = analyze(frame_with_target(frame, 20), default_scope(), "hash")
        self.assertFalse(alert_for_target(ordinary)["is_outlier"])
        self.assertTrue(alert_for_target(extreme)["is_outlier"])

    def test_post_action_applies_strength_guard_before_negative_direction(self):
        weak = analyze(
            frame_with_target(make_cohort(5, 6, [20, 21, 22, 23, 24]), 0),
            default_scope(),
            "weak",
        )["recommendations"][0]
        strong = analyze(
            frame_with_target(make_cohort(20, 5, [20, 21, 22, 23, 24]), 0),
            default_scope(),
            "strong",
        )["recommendations"][0]
        self.assertLess(weak["priority_components"]["strength"], 0.40)
        self.assertEqual((weak["action_type"], weak["topic"]), ("test", "creator"))
        self.assertGreaterEqual(strong["priority_components"]["strength"], 0.40)
        self.assertEqual((strong["action_type"], strong["topic"]), ("review", "stop"))

    def test_benchmark_fallback_and_sufficiency(self):
        base = make_cohort(5, 6, [4], audience_location="US")
        target = frame_with_target(base, 8, audience_location="BR")
        alert = alert_for_target(analyze(target, default_scope(), "hash"))
        self.assertIn("audience_location", alert["benchmark"]["removed_controls"])
        for key in ("platform", "content_type", "content_category", "follower_band", "is_sponsored"):
            self.assertEqual(alert["benchmark"]["effective_context"][key], alert["context"][key])
        for frame in (make_cohort(4, 10), make_cohort(5, 5)):
            self.assertEqual(analyze(frame, default_scope(target_start="2024-12-01", target_end="2024-12-31"), "hash")["alerts"], [])

    def test_target_creator_is_excluded_and_constant_iqr_is_not_strong(self):
        base = make_cohort(6, 6, [4])
        excluded_refs = set(base.loc[base["creator_id"] == "creator-0", "source_row_id"])
        target = frame_with_target(base, 20, creator_id="creator-0")
        result = analyze(target, default_scope(), "hash")
        alert = alert_for_target(result)
        self.assertTrue(excluded_refs.isdisjoint(alert["benchmark"]["source_row_ids"]))
        self.assertEqual(alert["benchmark"]["iqr"], 0)
        self.assertNotEqual(alert["strength_label"], "strong")

    def test_sponsorship_is_stratified_and_reports_uncovered_groups(self):
        result = analyze(
            sponsorship_rows(),
            default_scope(target_start="2025-01-01", target_end="2025-01-31", reference_date="2025-01-31"),
            "hash",
        )
        self.assertEqual(len(result["sponsorship"]["strata"]), 1)
        self.assertGreater(len(result["sponsorship"]["uncovered_strata"]), 0)
        self.assertLess(result["sponsorship"]["coverage"], 1.0)
        self.assertEqual(result["sponsorship"]["period_granularity"], "calendar_month")
        self.assertEqual(result["sponsorship"]["strata"][0]["context"]["period_month"], "2025-01")
        self.assertEqual(result["sponsorship"]["strata"][0]["delta_erv_pp"], 4.0)

    def test_sponsorship_requires_both_arms_in_the_same_month(self):
        organic = make_cohort(5, 6, [4], sponsored=False, start="2025-01-01T12:00:00")
        sponsored = make_cohort(5, 6, [14], sponsored=True, start="2025-02-01T12:00:00")
        organic.loc[:, "post_date"] = pd.Timestamp("2025-01-05T12:00:00")
        sponsored.loc[:, "post_date"] = pd.Timestamp("2025-02-05T12:00:00")
        frame = pd.concat([organic, sponsored], ignore_index=True)
        frame["id"] = [f"temporal-{index}" for index in range(len(frame))]
        frame["content_id"] = [f"temporal-content-{index}" for index in range(len(frame))]
        frame["source_row_id"] = [f"hash:temporal-{index}" for index in range(len(frame))]

        result = analyze(
            frame,
            default_scope(target_start="2025-01-01", target_end="2025-02-28", reference_date="2025-02-28"),
            "hash",
        )
        sponsorship = result["sponsorship"]
        self.assertEqual(sponsorship["eligible_strata"], 0)
        self.assertEqual(sponsorship["coverage"], 0.0)
        self.assertEqual(sponsorship["uncovered_count"], 2)
        self.assertEqual(
            {(item["period_month"], item["organic_posts"], item["sponsored_posts"]) for item in sponsorship["uncovered_strata"]},
            {("2025-01", 30, 0), ("2025-02", 0, 30)},
        )

    def test_sponsorship_recency_uses_sponsored_target_group_median_date(self):
        frame = sponsorship_rows()
        sponsored_target = frame["is_sponsored"] & frame["content_type"].eq("video")
        frame.loc[:, "post_date"] = pd.Timestamp("2025-01-01T12:00:00")
        frame.loc[sponsored_target, "post_date"] = pd.Timestamp("2025-01-31T12:00:00")
        result = analyze(
            frame,
            default_scope(target_start="2025-01-01", target_end="2025-01-31", reference_date="2025-01-31"),
            "hash",
        )
        evidence = result["sponsorship"]["strata"][0]
        recommendation = next(
            item for item in result["recommendations"]
            if item["evidence_id"] == evidence["evidence_id"]
        )
        self.assertEqual(pd.Timestamp(evidence["representative_date"]), pd.Timestamp("2025-01-31T12:00:00"))
        self.assertEqual(pd.Timestamp(recommendation["representative_date"]), pd.Timestamp("2025-01-31T12:00:00"))
        self.assertEqual(recommendation["priority_components"]["recency"], 1.0)

    def test_sponsorship_volume_guard_uses_post_medians_not_extreme_means(self):
        rows = []
        for sponsored in (False, True):
            for index in range(100):
                extreme = sponsored and index == 99
                views = 100_000 if extreme else 1 if sponsored else 100
                interactions = 200_000 if extreme else 2 if sponsored else 100
                marker = f"{'s' if sponsored else 'o'}-{index}"
                rows.append(make_post(
                    id=marker,
                    content_id=f"content-{marker}",
                    creator_id=f"creator-{index % 20}",
                    post_date="2025-01-15T12:00:00",
                    views=views,
                    likes=interactions,
                    shares=0,
                    comments_count=0,
                    is_sponsored=str(sponsored).upper(),
                ))
        result = analyze(
            frame_from_rows(rows),
            default_scope(target_start="2025-01-01", target_end="2025-01-31", reference_date="2025-01-31"),
            "hash",
        )
        evidence = result["sponsorship"]["strata"][0]
        recommendation = next(item for item in result["recommendations"] if item["evidence_id"] == evidence["evidence_id"])
        self.assertEqual(evidence["volume_guard"]["delta_views"], -99.0)
        self.assertEqual(evidence["volume_guard"]["delta_interactions"], -98.0)
        self.assertEqual(recommendation["action_type"], "test")
        self.assertEqual(recommendation["evidence_snapshot"]["target"]["creator_median_erv"], 200.0)
        self.assertEqual(recommendation["evidence_snapshot"]["comparator"]["creator_median_erv"], 100.0)

    def test_aggregate_normalization_includes_large_ineligible_nonempty_group(self):
        scope = default_scope(target_start="2025-01-01", target_end="2025-01-31", reference_date="2025-01-31")
        baseline_frame = sponsorship_rows()
        baseline = analyze(baseline_frame, scope, "hash")
        evidence_id = baseline["sponsorship"]["strata"][0]["evidence_id"]
        baseline_item = next(item for item in baseline["recommendations"] if item["evidence_id"] == evidence_id)

        large_group = frame_from_rows([
            make_post(
                id=f"large-{index}",
                content_id=f"large-content-{index}",
                creator_id=f"large-creator-{index}",
                content_type="text",
                post_date="2025-01-31T12:00:00",
                views=1_000_000,
                likes=100_000,
                shares=0,
                comments_count=0,
                follower_count=1_000_000,
                is_sponsored="TRUE",
            )
            for index in range(10)
        ])
        augmented = analyze(pd.concat([baseline_frame, large_group], ignore_index=True), scope, "hash")
        augmented_item = next(item for item in augmented["recommendations"] if item["evidence_id"] == evidence_id)

        self.assertGreater(augmented_item["normalization"]["views"], baseline_item["normalization"]["views"])
        self.assertLess(augmented_item["priority"], baseline_item["priority"])
        self.assertFalse(any(item["context"]["content_type"] == "text" for item in augmented["recommendations"]))

    def test_frequency_hypothesis_uses_creator_weeks_from_two_complete_iso_weeks(self):
        result = analyze(
            sponsorship_frequency_rows(2),
            default_scope(target_start="2025-01-06", target_end="2025-01-19", reference_date="2025-01-19"),
            "hash",
        )
        frequency = result["recommendations"][0]["frequency_hypothesis"]
        self.assertEqual(frequency["status"], "test")
        self.assertEqual(frequency["value"], 3.0)
        self.assertEqual(frequency["unit"], "posts_per_creator_per_complete_iso_week")
        self.assertEqual(frequency["sample_creator_weeks"], 10)
        self.assertEqual(frequency["observed_complete_weeks"], 2)
        self.assertEqual(frequency["window_start"], "2025-01-06T00:00:00")
        self.assertEqual(frequency["window_end"], "2025-01-19T00:00:00")

    def test_frequency_hypothesis_collects_before_suggesting_one_week_cadence(self):
        result = analyze(
            sponsorship_frequency_rows(1),
            default_scope(target_start="2025-01-06", target_end="2025-01-12", reference_date="2025-01-12"),
            "hash",
        )
        frequency = result["recommendations"][0]["frequency_hypothesis"]
        self.assertEqual(frequency["status"], "collect")
        self.assertIsNone(frequency["value"])
        self.assertEqual(frequency["observed_complete_weeks"], 1)
        self.assertEqual(frequency["action_type"], "collect_two_complete_weeks")

    def test_frequency_hypothesis_does_not_overflow_at_upper_date_boundary(self):
        boundary = "2262-04-09T12:00:00"
        sponsorship = frame_from_rows([
            make_post(
                id=f"{flag}-{index}",
                content_id=f"{flag}-content-{index}",
                creator_id=f"{flag}-creator-{index % 5}",
                is_sponsored=flag,
                post_date=boundary,
                likes=8 if flag == "TRUE" else 4,
            )
            for flag in ("TRUE", "FALSE")
            for index in range(30)
        ])
        editorial = aggregate_effect_rows(creators=20)
        editorial.loc[editorial["id"].str.startswith("before-"), "post_date"] = pd.Timestamp("2262-04-08T12:00:00")
        editorial.loc[editorial["id"].str.startswith("now-"), "post_date"] = pd.Timestamp(boundary)
        post = frame_with_target(
            make_cohort(20, 5, [2, 4, 6, 8, 10], start="2262-03-01T12:00:00"),
            30,
            post_date=boundary,
        )
        cases = (
            (sponsorship, "aggregate", "sponsorship"),
            (editorial, "aggregate", "editorial"),
            (post, "post", "post"),
        )
        scope = default_scope(target_start="2262-04-09", target_end="2262-04-09", reference_date=boundary)
        for frame, evidence_type, family in cases:
            with self.subTest(family=family):
                result = analyze(frame, scope, family)
                recommendation = next(
                    item for item in result["recommendations"]
                    if item["evidence_type"] == evidence_type and item["evidence_snapshot"]["family"] == family
                )
                frequency = recommendation["frequency_hypothesis"]
                self.assertEqual(frequency["status"], "collect")
                self.assertEqual(frequency["complete_weeks_available"], 0)
                self.assertEqual(frequency["observed_complete_weeks"], 0)
                self.assertIsNone(frequency["window_start"])
                self.assertIsNone(frequency["window_end"])

    def test_month_frequency_excludes_boundary_weeks_and_other_months(self):
        scope = default_scope(
            target_start="2025-03-01", target_end="2025-04-30", reference_date="2025-04-30"
        )
        baseline = analyze(
            monthly_sponsorship_frequency_rows((1, 3, 10, 17, 24, 31)), scope, "hash"
        )
        augmented = analyze(
            monthly_sponsorship_frequency_rows(
                (1, 3, 10, 17, 24, 31), extra_april_sponsored_days=(7, 14, 21)
            ),
            scope,
            "hash",
        )
        baseline_frequency = baseline["recommendations"][0]["frequency_hypothesis"]
        augmented_frequency = augmented["recommendations"][0]["frequency_hypothesis"]

        self.assertEqual(baseline_frequency, augmented_frequency)
        self.assertEqual(baseline_frequency["status"], "test")
        self.assertEqual(baseline_frequency["value"], 1.0)
        self.assertEqual(baseline_frequency["complete_weeks_available"], 4)
        self.assertEqual(baseline_frequency["observed_complete_weeks"], 4)
        self.assertEqual(baseline_frequency["sample_creator_weeks"], 20)
        self.assertEqual(baseline_frequency["window_start"], "2025-03-03T00:00:00")
        self.assertEqual(baseline_frequency["window_end"], "2025-03-30T00:00:00")
        self.assertEqual(baseline_frequency["period_month"], "2025-03")
        self.assertEqual(
            baseline_frequency["coverage_rule"],
            "complete_iso_weeks_within_calendar_month_and_scope",
        )

    def test_month_frequency_collects_with_only_one_complete_observed_week(self):
        result = analyze(
            monthly_sponsorship_frequency_rows(
                (1, 2, 3, 31, 31, 31), extra_april_sponsored_days=(7,)
            ),
            default_scope(
                target_start="2025-03-01", target_end="2025-03-31", reference_date="2025-03-31"
            ),
            "hash",
        )
        frequency = result["recommendations"][0]["frequency_hypothesis"]
        self.assertEqual(frequency["status"], "collect")
        self.assertIsNone(frequency["value"])
        self.assertEqual(frequency["complete_weeks_available"], 4)
        self.assertEqual(frequency["observed_complete_weeks"], 1)
        self.assertEqual(frequency["sample_creator_weeks"], 5)
        self.assertEqual(frequency["action_type"], "collect_two_complete_weeks")

    def test_priority_is_reproducible_and_exposes_components(self):
        reference = make_cohort(20, 5, [2, 4, 6, 8, 10])
        frame = frame_with_target(reference, 30)
        first_result = analyze(frame, default_scope(), "hash")
        first = first_result["recommendations"]
        second = analyze(frame, default_scope(), "hash")["recommendations"]
        self.assertEqual(first, second)
        self.assertEqual(set(first[0]["priority_components"]), {"impact", "strength", "recency"})
        self.assertEqual(first[0]["action_type"], "test")
        snapshot = first[0]["evidence_snapshot"]
        self.assertEqual(snapshot["family"], "post")
        self.assertEqual(snapshot["evidence_id"], first[0]["evidence_id"])
        self.assertTrue(snapshot["comparator"]["eligible"])
        alert = next(item for item in first_result["alerts"] if item["evidence_id"] == first[0]["evidence_id"])
        self.assertEqual(set(snapshot["comparator"]["source_row_ids"]), set(alert["benchmark"]["source_row_ids"]))

    def test_evidence_ids_use_canonical_scope_and_current_method(self):
        frame = frame_from_rows([
            make_post(id="a", content_id="a", post_date="2025-01-01T12:00:00"),
            make_post(id="b", content_id="b", post_date="2025-01-15T12:00:00"),
        ])
        first = analyze(frame, default_scope(
            target_start="2025-01-01", target_end="2025-01-15",
            filters={"platform": ["Instagram"], "content_type": ["video", "image"]},
        ), "hash")
        equivalent = analyze(frame, default_scope(
            target_start=pd.Timestamp("2025-01-01"), target_end=pd.Timestamp("2025-01-15"),
            filters={"content_type": ["image", "video"], "platform": ["Instagram"]},
        ), "hash")
        changed = analyze(frame, default_scope(
            target_start="2025-01-15", target_end="2025-01-15",
            filters={"platform": ["Instagram"], "content_type": ["video", "image"]},
        ), "hash")
        first_id = first["dimensions"]["platform"][0]["evidence_id"]
        self.assertEqual(first_id, equivalent["dimensions"]["platform"][0]["evidence_id"])
        self.assertNotEqual(first_id, changed["dimensions"]["platform"][0]["evidence_id"])
        self.assertEqual(first["scope"]["method_version"], METHOD_VERSION)
        self.assertEqual(METHOD_VERSION, "2.5.0")

    def test_insufficiency_diagnostics_and_source_rate_warning_are_preserved(self):
        frame = frame_with_target(make_cohort(4, 6, [4]), 20)
        frame["engagement_rate"] = "source-value"
        result = analyze(frame, default_scope(), "hash")
        self.assertEqual(result["alerts"], [])
        self.assertEqual(result["quality"]["benchmark_levels_attempted"], 5)
        diagnostic = result["quality"]["benchmark_diagnostics"][0]
        self.assertEqual(diagnostic["target_count"], 1)
        self.assertEqual(len(diagnostic["attempts"]), 5)
        self.assertTrue(all("n_rate" in item and "n_creators" in item and item["reason"] for item in diagnostic["attempts"]))
        self.assertEqual(result["quality"]["warnings"][0]["code"], "source_engagement_rate_ignored")

    def test_full_history_post_analysis_is_bounded_and_keeps_diagnostics(self):
        rows = [make_post(
            id=f"history-{index}",
            content_id=f"history-content-{index}",
            creator_id=f"history-creator-{index}",
            post_date="2025-01-01T12:00:00",
        ) for index in range(5_000)]
        frame = frame_from_rows(rows)
        started = time.perf_counter()
        result = analyze(
            frame,
            default_scope(target_start="2025-01-01", target_end="2025-01-01", reference_date="2025-01-01"),
            "hash",
        )
        elapsed = time.perf_counter() - started
        self.assertLess(elapsed, 10.0)
        self.assertEqual(result["alerts"], [])
        self.assertEqual(result["quality"]["benchmark_levels_attempted"], 25_000)
        self.assertEqual(sum(item["target_count"] for item in result["quality"]["benchmark_diagnostics"]), 5_000)

    def test_strength_formula_penalizes_creator_concentration(self):
        balanced = analyze(frame_with_target(make_cohort(20, 5), 20), default_scope(), "hash")
        concentrated = analyze(frame_with_target(concentrated_reference(), 20), default_scope(), "hash")
        balanced_strength = alert_for_target(balanced)["strength"]
        concentrated_strength = alert_for_target(concentrated)["strength"]
        self.assertAlmostEqual(balanced_strength, 0.95)
        self.assertAlmostEqual(concentrated_strength, 0.05)
        self.assertGreater(balanced_strength, concentrated_strength)

    def test_aggregate_recommendation_exists_without_post_outlier(self):
        result = analyze(
            aggregate_effect_rows(),
            default_scope(target_start="2025-01-08", target_end="2025-01-14", reference_date="2025-01-14"),
            "hash",
        )
        self.assertEqual(result["alerts"], [])
        self.assertEqual(result["recommendations"][0]["evidence_type"], "aggregate")
        self.assertEqual(result["recommendations"][0]["action_type"], "test")
        self.assertEqual(result["recommendations"][0]["supporting_topics"], ["audience", "creator", "frequency", "quick_win"])

    def test_strong_aligned_and_conflicting_editorial_signals_map_to_actions(self):
        scope = default_scope(target_start="2025-01-08", target_end="2025-01-14", reference_date="2025-01-14")
        positive = analyze(aggregate_effect_rows(creators=20), scope, "hash")
        negative = analyze(
            aggregate_effect_rows(creators=20, current_interactions=2), scope, "hash"
        )
        conflicting = analyze(
            aggregate_effect_rows(creators=20, current_views=50, current_interactions=3),
            scope,
            "hash",
        )
        self.assertEqual(positive["recommendations"][0]["action_type"], "scale_test")
        self.assertEqual(negative["recommendations"][0]["action_type"], "review_stop")
        self.assertEqual(conflicting["recommendations"][0]["action_type"], "test")
        allowed_topics = {"effort", "audience", "frequency", "sponsorship", "creator", "stop", "quick_win"}
        for result in (positive, negative, conflicting):
            self.assertTrue(all(item["topic"] in allowed_topics for item in result["recommendations"]))
            self.assertTrue(all(item["evidence_id"] for item in result["recommendations"]))

    def test_editorial_recency_uses_true_even_sample_datetime_median(self):
        frame = aggregate_effect_rows(creators=20)
        current_indices = frame.index[frame["id"].str.startswith("now-")].tolist()
        frame.loc[current_indices[:50], "post_date"] = pd.Timestamp("2025-01-08T12:00:00")
        frame.loc[current_indices[50:], "post_date"] = pd.Timestamp("2025-01-14T12:00:00")
        result = analyze(
            frame,
            default_scope(target_start="2025-01-08", target_end="2025-01-14", reference_date="2025-01-14"),
            "editorial-median",
        )
        evidence = result["cohorts"]["editorial"][0]
        recommendation = next(
            item for item in result["recommendations"] if item["evidence_id"] == evidence["evidence_id"]
        )
        expected_recency = 2 ** (-3 / 7)
        self.assertEqual(pd.Timestamp(evidence["representative_date"]), pd.Timestamp("2025-01-11T12:00:00"))
        self.assertEqual(pd.Timestamp(recommendation["representative_date"]), pd.Timestamp("2025-01-11T12:00:00"))
        self.assertAlmostEqual(recommendation["priority_components"]["recency"], expected_recency)
        self.assertAlmostEqual(recommendation["priority"], 100 * 0.95 * expected_recency)

    def test_all_recommendations_preserves_complete_deduplicated_queue(self):
        frames = []
        for category in ("one", "two", "three", "four"):
            frame = aggregate_effect_rows(creators=20)
            frame["content_category"] = category
            frame["id"] = [f"{category}-{value}" for value in frame["id"]]
            frame["content_id"] = [f"{category}-{value}" for value in frame["content_id"]]
            frame["source_row_id"] = [f"hash:{value}" for value in frame["id"]]
            frames.append(frame)
        result = analyze(
            pd.concat(frames, ignore_index=True),
            default_scope(target_start="2025-01-08", target_end="2025-01-14", reference_date="2025-01-14"),
            "all-editorial",
        )
        self.assertEqual(len(result["recommendations"]), 3)
        self.assertEqual(len(result["all_recommendations"]), 4)
        self.assertEqual(result["recommendations"], result["all_recommendations"][:3])
        self.assertEqual(
            {item["context"]["content_category"] for item in result["all_recommendations"]},
            {"one", "two", "three", "four"},
        )
        self.assertTrue(all(item["evidence_snapshot"] for item in result["all_recommendations"]))
        self.assertEqual(
            set(result["evidence_snapshots"]),
            {item["evidence_id"] for item in result["all_recommendations"]},
        )


class ExecutiveAnswerTests(unittest.TestCase):
    def test_executive_answers_use_driver_ranking_and_disclose_decision_trigger(self):
        answers = executive_answers(result_with_stable_driver())
        self.assertEqual(len(answers), 4)
        self.assertTrue(all(set(answer) == {
            "question", "verdict", "kpi", "comparison", "sample", "action",
            "strength", "coverage", "stability", "evidence_id", "change_trigger",
        } for answer in answers))
        self.assertIn("INSTAGRAM / TEXTO / TECH", answers[0]["verdict"])

    def test_strategy_has_four_ordered_weeks_and_no_automatic_scale(self):
        strategy = content_strategy_30d(result_with_stable_driver())
        self.assertEqual([item["week"] for item in strategy["weeks"]], [1, 2, 3, 4])
        self.assertEqual(
            [item["window"] for item in strategy["weeks"]],
            ["D1–D7", "D8–D14", "D15–D21", "D22–D30"],
        )
        self.assertTrue(all("cadence" in item for item in strategy["weeks"]))
        self.assertEqual(strategy["mix_policy"], "preserve_current_mix_outside_tests")
        self.assertTrue(all(item["owner"] == "Gestor de Social Media" for item in strategy["weeks"]))
        self.assertFalse(strategy["automatic_publication_or_spend"])

    def test_no_stable_driver_yields_explicit_collection_strategy(self):
        answers = executive_answers(result_without_stable_driver())
        self.assertIn("NÃO EXISTE VENCEDOR SUSTENTADO", answers[0]["verdict"])
        self.assertIn("mudaria", answers[0]["change_trigger"].lower())

    def test_strategy_collects_on_best_eligible_candidate_when_no_context_is_material(self):
        rows = driver_rows([0.05, 0.06, 0.07])
        result = analyze(frame_from_rows(rows), default_scope_all_history(rows), "hash")
        self.assertIsNone(result["engagement_drivers"]["leader"])
        strategy = content_strategy_30d(result)
        self.assertEqual(strategy["driver_evidence_id"], result["engagement_drivers"]["best_candidate"]["evidence_id"])
        self.assertGreater(result["engagement_drivers"]["best_candidate"]["eligible_months"], 0)
        self.assertFalse(strategy["scale_gate_met"])
        answer = executive_answers(result)[2]
        self.assertIn("PARA VALIDAR", answer["verdict"])
        self.assertIn("3 meses elegíveis", answer["coverage"])


if __name__ == "__main__":
    unittest.main()
