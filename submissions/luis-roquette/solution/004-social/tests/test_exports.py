from __future__ import annotations

import csv
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from contextlib import closing

from analysis import METHOD_VERSION, executive_summary, export_evidence, analysis_report, analyze, load_csv
from tests.helpers import (aggregate_effect_rows, csv_bytes, default_scope,
                           default_scope_all_history, driver_rows, frame_from_rows,
                           make_post, sponsorship_frequency_rows)
from storage import connect, list_decisions, record_decision, record_import, record_outcome
from tests.test_storage import decision_event, import_event, outcome_event


APP_ROOT = Path(__file__).resolve().parents[1]


def sample_result() -> dict[str, object]:
    return {
        "source": {"source_hash": "abc", "rows": 1, "period_start": "2025-01-01", "period_end": "2025-01-01", "platforms": ["Instagram"]},
        "scope": {"method_version": "1.0.0", "target_start": "2025-01-01", "target_end": "2025-01-01"},
        "metrics": {"posts": 1, "views": 100, "interactions": 10, "median_erv": 10.0},
        "dimensions": {"platform": [{"evidence_id": "dimension-1", "dimension": "platform", "value": "Instagram", "posts": 1, "views": 100, "interactions": 10, "median_erv": 10.0, "source_row_ids": ["abc:1"]}]},
        "alerts": [], "cohorts": {"editorial": []},
        "sponsorship": {"strata": [], "uncovered_strata": [], "coverage": 0.0, "required_financial_data": ["investment"]},
        "recommendations": [{"evidence_id": "dimension-1", "action": "Testar padrão", "owner": "Gestor", "execution_window": "7 dias", "review_window": "7 dias", "priority": 10.0}],
        "pending": [], "row_references": {"abc:1": 2},
    }


def result_with_texts(texts: list[str]) -> dict[str, object]:
    result = sample_result()
    result["dimensions"] = {"text": [{"evidence_id": f"text-{index}", "dimension": "text", "value": text, "posts": 1, "metric_value": 10.0, "source_row_ids": []} for index, text in enumerate(texts)]}
    return result


def parse_export(payload: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(payload.decode("utf-8"))))


def sample_decisions() -> list[dict[str, object]]:
    return [{"decision_id": "d-1", "evidence_id": "dimension-1", "status": "accepted", "owner": "Gestor"}]


def historical_log(path: Path) -> tuple[str, str, str]:
    with closing(connect(path)) as conn:
        for source in ("source-a", "source-b"):
            record_import(conn, import_event(source))
        scope = {"filters": {"platform": ["Instagram"]}, "target_start": "2025-01-01", "target_end": "2025-01-07"}
        original = record_decision(conn, decision_event(scope=scope, original_text="=Original", owner="@Gestor"))
        revision = record_decision(conn, decision_event(
            event_id="revision-event", revision_of=original, scope=scope,
            decided_at="2025-01-07T21:00:00+00:00", status="edited",
            original_text="=Original", edited_text="+Editado", owner="@Gestor",
        ))
        outcome = record_outcome(conn, outcome_event(
            decision_id=revision, scope={**scope, "target_start": "2025-01-08", "target_end": "2025-01-14"},
        ))
    return original, revision, outcome


def run_cli(path: Path) -> tuple[int, tuple[bytes, ...]]:
    with tempfile.TemporaryDirectory() as directory:
        output_csv = Path(directory) / "evidence.csv"
        output_html = Path(directory) / "summary.html"
        output_report = Path(directory) / "analysis.md"
        completed = subprocess.run(
            [sys.executable, str(APP_ROOT / "analysis.py"), str(path), "--evidence", str(output_csv), "--summary", str(output_html), "--report", str(output_report)],
            capture_output=True,
            check=False,
        )
        return completed.returncode, tuple(output.read_bytes() if output.exists() else b"" for output in (output_csv, output_html, output_report))


class ExportTests(unittest.TestCase):
    def test_driver_and_strategy_are_exported_as_deterministic_evidence(self):
        rows = driver_rows([1.0, 1.2, 0.8])
        result = analyze(frame_from_rows(rows), default_scope_all_history(rows), "hash")
        first = parse_export(export_evidence(result, []))
        second = parse_export(export_evidence(result, []))
        self.assertEqual(first, second)
        metrics = [row["metric_name"] for row in first if row["record_type"] == "evidence"]
        self.assertEqual(metrics.count("driver_overview"), 1)
        self.assertIn("driver_context", metrics)
        self.assertEqual(metrics.count("strategy_30d"), 1)
        self.assertEqual(metrics.count("strategy_week"), 4)
        driver = next(row for row in first if row["metric_name"] == "driver_context")
        self.assertEqual(driver["unit"], "percentage_points")

    def test_reopened_history_retains_abc_provenance_chronology_and_revision(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.sqlite3"
            original_id, revision_id, outcome_id = historical_log(path)
            with closing(connect(path)) as conn:
                history = list_decisions(conn)
            result = sample_result()
            result["source"]["source_hash"] = "source-c"
            result["scope"] = {"filters": {"platform": ["TikTok"]}, "method_version": "active-only"}
            payload = export_evidence(result, history)
            self.assertEqual(payload, export_evidence(result, history))
            with closing(connect(path)) as conn:
                self.assertEqual(payload, export_evidence(result, list_decisions(conn)))
            rows = parse_export(payload)
            decisions = {row["decision_id"]: row for row in rows if row["record_type"] == "decision"}
            revision = decisions[revision_id]
            self.assertEqual(revision["revision_of"], original_id)
            self.assertEqual(revision["event_id"], "revision-event")
            self.assertEqual(revision["decided_at"], "2025-01-07T21:00:00+00:00")
            self.assertEqual(revision["status"], "edited")
            self.assertEqual(revision["original_text"], "'=Original")
            self.assertEqual(revision["edited_text"], "'+Editado")
            self.assertEqual(revision["effective_text"], "'+Editado")
            self.assertEqual(revision["text"], revision["effective_text"])
            self.assertEqual(revision["owner"], "'@Gestor")
            self.assertEqual(revision["execution_window"], "próximos 7 dias")
            for decision in decisions.values():
                self.assertEqual(decision["source_hash"], "source-a")
                self.assertEqual(decision["method_version"], METHOD_VERSION)
                self.assertEqual(json.loads(decision["scope"])["target_start"], "2025-01-01")
                self.assertEqual(json.loads(decision["baseline"])["source_row_ids"], ["source-a:1"])
                self.assertEqual(decision["recommendation_key"], "recommendation-1")
            outcome = next(row for row in rows if row["record_type"] == "outcome")
            expected = {
                "outcome_id": outcome_id, "decision_id": revision_id, "revision_of": original_id,
                "source_hash": "source-b", "decision_source_hash": "source-a", "method_version": METHOD_VERSION,
                "recorded_at": "2026-09-21T20:10:00+00:00", "execution_status": "yes", "execution_date": "2025-01-07",
                "period_start": "2025-01-08", "period_end": "2025-01-14", "status": "observed",
                "reason": "comparable_after_declared_execution", "metric_name": "erv", "metric_value": "5.0",
                "coverage_days": "7", "baseline_coverage_days": "7", "coverage_equal": "true", "comparable": "true",
                "median_delta": "1.0", "baseline_volume_per_day": "100.0", "observed_volume_per_day": "120.0", "non_causal": "true",
            }
            self.assertEqual({key: outcome[key] for key in expected}, expected)
            self.assertEqual(json.loads(outcome["scope"])["target_start"], "2025-01-08")
            self.assertEqual(json.loads(outcome["decision_scope"]), json.loads(revision["scope"]))
            self.assertEqual(json.loads(outcome["comparison"])["median_delta"], 1.0)
            self.assertEqual(json.loads(outcome["observed"])["views"], 840)
            self.assertIn("não demonstra causalidade", outcome["text"])
            self.assertTrue(all(row["source_hash"] == "source-c" for row in rows if row["record_type"] not in {"decision", "outcome"}))

    def test_large_history_fields_round_trip_with_default_reader(self):
        history = [{**decision_event(), "decision_id": "decision-long", "original_text": "=\n" + "á" * 140_000}]
        history[0]["baseline"]["source_row_ids"] = [f"source-a:{index}" for index in range(20_000)]
        payload = export_evidence(sample_result(), history)
        rows = parse_export(payload)
        decision = next(row for row in rows if row["record_type"] == "decision")
        for name in ("baseline", "original_text", "effective_text", "text"):
            self.assertEqual(decision[name], "")
            chunks = [row for row in rows if row["record_type"] == "history_field" and row["field_name"] == name]
            self.assertEqual([int(row["field_chunk"]) for row in chunks], list(range(1, len(chunks) + 1)))
            self.assertTrue(all(row["source_hash"] == "source-a" and row["decision_id"] == "decision-long" for row in chunks))
            value = "".join(json.loads(row["field_value"]) for row in chunks)
            if name == "baseline":
                self.assertEqual(json.loads(value), history[0]["baseline"])
            else:
                self.assertEqual(value, "'" + history[0]["original_text"])
        self.assertEqual(payload, export_evidence(sample_result(), history))
        self.assertLess(max(len(value) for row in rows for value in row.values()), 131_072)

    def test_legacy_history_never_inherits_active_provenance(self):
        rows = parse_export(export_evidence(sample_result(), [{"decision_id": "legacy", "outcomes": [{"observed": {}}]}]))
        for row in rows:
            if row["record_type"] in ("decision", "outcome"):
                self.assertEqual((row["source_hash"], row["scope"], row["method_version"]), ("", "", ""))

    def test_zero_view_rate_remains_undefined_in_all_exports(self):
        for views, expected in ((0, "não definida"), (100, "0.00%")):
            frame, errors = load_csv(csv_bytes([make_post(views=views, likes=0, shares=0, comments_count=0)]))
            self.assertEqual(errors, [])
            result = analyze(frame, {"include_post_alerts": False}, str(frame["source_hash"].iloc[0]))
            page = executive_summary(result, [])
            self.assertIn(f"mediana ERv {expected}", page)
            if views == 0:
                self.assertNotIn("mediana ERv 0.00%", page)
                self.assertIn("views=0", page)
                self.assertIn("Mediana ERv: não definida", analysis_report(result))
            dimensions = [row for row in parse_export(export_evidence(result, [])) if row["record_type"] == "evidence" and row["evidence_id"].startswith("dimension-")]
            for row in dimensions:
                self.assertEqual(row["metric_name"], "median_erv")
                self.assertEqual(row["metric_value"], "" if views == 0 else "0.0")

    def test_empty_filter_intersection_and_time_window_have_explicit_shared_state(self):
        frame = frame_from_rows([
            make_post(id="instagram-tech", content_id="instagram-tech"),
            make_post(id="tiktok-beauty", content_id="tiktok-beauty", platform="TikTok", content_category="beauty"),
        ])
        source_hash = str(frame["source_hash"].iloc[0])
        scopes = (
            default_scope(filters={"platform": ["Instagram"], "content_category": ["beauty"]}),
            default_scope(target_start="2025-02-01", target_end="2025-02-01", reference_date="2025-02-01"),
        )
        for scope in scopes:
            with self.subTest(scope=scope):
                result = analyze(frame, scope, source_hash)
                expected = {
                    "status": "empty_scope",
                    "has_observations": False,
                    "reason": "no_matching_records",
                    "message": "Nenhum registro corresponde aos filtros/período selecionados. Ajuste o recorte para continuar.",
                }
                self.assertEqual(result["analysis_state"], expected)
                self.assertEqual(result["metrics"]["posts"], 0)
                self.assertEqual(result["source"]["rows"], 2)
                self.assertEqual(result["target_source_row_ids"], [])
                self.assertEqual(result["pending"][0]["action_type"], "adjust_scope")
                self.assertEqual(result["pending"][0]["reason"], "no_matching_records")

                page, report = executive_summary(result, []), analysis_report(result)
                for output in (page, report):
                    self.assertIn(expected["message"], output)
                    self.assertIn("ΔERv não definido — sem comparador elegível", output)
                    self.assertNotIn("ΔERv +0", output)
                self.assertNotIn("<b>0 posts</b>", page)
                self.assertNotIn("0 posts; 0 creators; 0 views; 0 interações", report)

                rows = parse_export(export_evidence(result, []))
                summary = next(row for row in rows if row["record_type"] == "summary")
                self.assertEqual(summary["metric_name"], "analysis_state")
                self.assertEqual(summary["metric_value"], "")
                self.assertEqual(summary["unit"], "")
                self.assertEqual(json.loads(summary["statistics"]), expected)

        observed_zero = frame_from_rows([
            make_post(id="observed-zero", content_id="observed-zero", likes=0, shares=0, comments_count=0),
        ])
        measured = analyze(observed_zero, default_scope(), str(observed_zero["source_hash"].iloc[0]))
        self.assertEqual(measured["analysis_state"], {
            "status": "ready", "has_observations": True, "reason": None, "message": None,
        })
        self.assertIn("<b>0 interações</b>", executive_summary(measured, []))
        summary = next(row for row in parse_export(export_evidence(measured, [])) if row["record_type"] == "summary")
        self.assertEqual((summary["metric_name"], summary["metric_value"], summary["unit"]), ("posts", "1", "posts"))

    def test_missing_delta_and_legitimate_zero_remain_distinct_in_reports(self):
        sparse = frame_from_rows([make_post()])
        pending = analyze(sparse, default_scope(), str(sparse["source_hash"].iloc[0]))
        self.assertNotIn("delta_erv_pp", pending["pending"][0])
        for output in (executive_summary(pending, []), analysis_report(pending)):
            self.assertIn("ΔERv não definido — sem comparador elegível", output)
            self.assertNotIn("ΔERv +0", output)

        equal_effect = aggregate_effect_rows(before_interactions=4, current_interactions=4)
        compared = analyze(
            equal_effect,
            default_scope(target_start="2025-01-08", target_end="2025-01-14", reference_date="2025-01-14"),
            "hash",
        )
        zero = next(item for item in compared["recommendations"] if item["delta_erv_pp"] == 0)
        self.assertEqual(zero["action_type"], "test")
        for output in (executive_summary(compared, []), analysis_report(compared)):
            self.assertIn("ΔERv +0 p.p.", output)

    def test_large_reference_export_round_trips_with_default_csv_limit(self):
        result = sample_result()
        ids = [f"abc:id:{index}" for index in range(20_000)] + ["abc:= " + "x" * 140_000]
        result["row_references"] = {source_id: index + 2 for index, source_id in enumerate(ids)}
        result["dimensions"]["platform"][0]["source_row_ids"] = ids
        limit = csv.field_size_limit()
        self.assertEqual(limit, 131_072)
        payload = export_evidence(result, [])
        rows = parse_export(payload)
        self.assertEqual(csv.field_size_limit(), limit)
        self.assertEqual(payload, export_evidence(result, []))
        refs = [row for row in rows if row["record_type"] == "source_ref" and row["evidence_id"] == "dimension-1"]
        self.assertGreater(len(refs), 1)
        reconstructed = {}
        for chunk, row in enumerate(refs, 1):
            self.assertEqual(int(row["reference_chunk"]), chunk)
            for index, source_id, line in zip(json.loads(row["reference_index"]), json.loads(row["source_row_id"]), json.loads(row["source_line"]), strict=True):
                prior, prior_line = reconstructed.get(index, ("", line))
                self.assertEqual(line, prior_line)
                reconstructed[index] = (prior + source_id, line)
        self.assertEqual(list(reconstructed.values()), [(source_id.split(":", 1)[1], result["row_references"][source_id]) for source_id in ids])

    def test_formula_prefix_after_whitespace_and_controls_preserves_original_text(self):
        unsafe = [prefix + marker + "1" for prefix in ("  ", "\n", " \t\r\n\x00\x7f\ufeff", "\u00a0") for marker in "=+-@"]
        safe = ["  texto", "   ", ""]
        result = result_with_texts(unsafe + safe)
        rows = parse_export(export_evidence(result, [{"text": value} for value in unsafe + safe]))
        for record_type in ("evidence", "decision"):
            actual = [row["text"] for row in rows if row["record_type"] == record_type and (record_type == "decision" or row["evidence_id"].startswith("text-"))]
            self.assertEqual(actual, ["'" + value for value in unsafe] + safe)
        result["recommendations"][0]["delta_erv_pp"] = -0.25
        recommendation = next(row for row in parse_export(export_evidence(result, [])) if row["record_type"] == "recommendation")
        self.assertEqual(recommendation["delta_erv_pp"], "-0.25")

    def test_initial_controls_are_prefixed_without_formula_markers(self):
        unsafe = [spaces + control + suffix
                  for spaces in ("", "  ")
                  for control in ("\t", "\r", "\n", "\x00", "\x7f", "\ufeff", "\u200b")
                  for suffix in ("texto", "")]
        safe = ["texto\tcontinuação", " texto\ncontinuação", "   ", ""]
        rows = parse_export(export_evidence(result_with_texts(unsafe + safe), [{"text": value} for value in unsafe + safe]))
        for record_type in ("evidence", "decision"):
            actual = [row["text"] for row in rows if row["record_type"] == record_type and (record_type == "decision" or row["evidence_id"].startswith("text-"))]
            self.assertEqual(actual, ["'" + value for value in unsafe] + safe)

    def test_frequency_is_reconciled_in_csv_and_reports_for_test_and_collect(self):
        for weeks, end, expected_status in ((2, "2025-01-19", "test"), (1, "2025-01-12", "collect")):
            with self.subTest(status=expected_status):
                result = analyze(sponsorship_frequency_rows(weeks), default_scope(target_start="2025-01-06", target_end=end, reference_date=end), "hash")
                item = result["recommendations"][0]
                frequency = item["frequency_hypothesis"]
                row = next(row for row in parse_export(export_evidence(result, [])) if row["record_type"] == "recommendation")
                self.assertEqual(json.loads(row["frequency_hypothesis"]), frequency)
                for report in (analysis_report(result), executive_summary(result, [])):
                    self.assertIn(item["evidence_id"], report)
                    self.assertIn(f"status {expected_status}", report)
                    self.assertIn(f"mês {frequency['period_month']}", report)
                    for key in ("unit", "method", "action_type", "window_start", "window_end", "limitation", "coverage_rule"):
                        self.assertIn(str(frequency[key]), report)
                    for label, key in (("creator-semanas", "sample_creator_weeks"), ("creators", "sample_creators"), ("semanas completas disponíveis", "complete_weeks_available"), ("semanas observadas", "observed_complete_weeks")):
                        self.assertIn(f"{frequency[key]} {label}", report)
                    self.assertIn(f"mínimo de {frequency['collection_requirement_weeks']} semanas", report)
                    self.assertIn("ausência de linha não equivale a zero", report)
                    if expected_status == "test":
                        self.assertIn("Testar 3 posts por creator por semana ISO completa", report)
                    else:
                        self.assertIn("Coletar antes de sugerir cadência; valor não definido", report)

    def test_recommendations_reconcile_csv_markdown_and_html_in_engine_order(self):
        result = sample_result()
        result["recommendations"] = [
            {"evidence_id": f"recommendation-{index}", "recommendation_key": f"recommendation-{index}",
             "context": {"platform": "TikTok", "content_type": "video", "content_category": str(index), "follower_band": "500,000+"},
             "priority": 100 * 0.5 * 0.8 * recency, "priority_components": {"impact": 0.5, "strength": 0.8, "recency": recency},
             "priority_values": {"views": 100, "interactions": 20, "followers": 50},
             "normalization": {"views": 200, "interactions": 40, "followers": 100},
             "delta_erv_pp": -0.1, "representative_date": "2024-01-01", "action_type": "test", "topic": "sponsorship",
             "action": f"Teste {index}", "owner": "Gestor", "execution_window": "próximos 7 dias", "review_window": "7 dias após o teste", "metric": "ERv e volume"}
            for index, recency in [(2, 1e-12), (1, 5e-13), (3, 2e-13)]
        ]
        rows = [row for row in parse_export(export_evidence(result, [])) if row["record_type"] == "recommendation"]
        self.assertEqual([row["evidence_id"] for row in rows], [item["evidence_id"] for item in result["recommendations"]])
        for rank, (row, item) in enumerate(zip(rows, result["recommendations"], strict=True), 1):
            self.assertEqual(int(row["rank"]), rank)
            for key in ("priority", "delta_erv_pp"):
                self.assertEqual(float(row[key]), item[key])
            for key, value in item["priority_components"].items():
                self.assertEqual(float(row[key]), value)
            for key in ("normalization", "priority_values", "context"):
                self.assertEqual(json.loads(row[key]), item[key])
            for key in ("action", "action_type", "owner", "execution_window", "review_window", "representative_date", "metric"):
                self.assertEqual(row[key], item[key])
            self.assertAlmostEqual(float(row["priority"]), 100 * float(row["impact"]) * float(row["strength"]) * float(row["recency"]), delta=1e-25)
        for output in (analysis_report(result), executive_summary(result, [])):
            positions = [output.index(item["evidence_id"]) for item in result["recommendations"]]
            self.assertEqual(positions, sorted(positions))
            for item in result["recommendations"]:
                self.assertIn(f"{item['priority']:.6g}", output)
                self.assertIn(item["execution_window"], output)
                self.assertIn(item["review_window"], output)

    def test_compact_references_round_trip_opaque_ids_and_physical_lines(self):
        frame, errors = load_csv(csv_bytes([
            make_post(id="id:one", content_description="first line\nsecond line"),
            make_post(id="two", content_id="different"),
        ]))
        self.assertEqual(errors, [])
        self.assertEqual(frame["source_line"].tolist(), [2, 4])
        result = analyze(frame, {"include_post_alerts": False}, str(frame["source_hash"].iloc[0]))
        references = [row for row in parse_export(export_evidence(result, [])) if row["record_type"] == "source_ref"]
        self.assertTrue(references)
        for row in references:
            ids, lines = json.loads(row["source_row_id"]), json.loads(row["source_line"])
            self.assertEqual(len(ids), len(lines))
            for source_id, line in zip(ids, lines, strict=True):
                self.assertEqual(result["row_references"][f"{row['source_hash']}:{source_id}"], line)

    def test_export_csv_keeps_numbers_numeric_and_neutralizes_formula_text(self):
        rows = parse_export(export_evidence(result_with_texts(["=1+1", "+cmd", "-2+3", "@SUM(A1)", "\t=1"]), []))
        evidence = [row for row in rows if row["record_type"] == "evidence" and row["evidence_id"].startswith("text-")]
        self.assertTrue(all(row["text"].startswith("'") for row in evidence))
        self.assertEqual(float(next(row for row in evidence if row["metric_value"])["metric_value"]), 10.0)

    def test_export_rows_join_through_evidence_and_source_ids(self):
        rows = parse_export(export_evidence(sample_result(), sample_decisions()))
        evidence_ids = {row["evidence_id"] for row in rows if row["record_type"] == "evidence"}
        self.assertTrue(all(row["evidence_id"] in evidence_ids for row in rows if row["record_type"] in {"source_ref", "decision"}))

    def test_executive_html_escapes_input_and_has_no_active_content(self):
        page = executive_summary(result_with_texts(["<script>alert(1)</script>"]), [])
        self.assertIn("&lt;script&gt;", page)
        self.assertNotIn("<script", page.lower())
        self.assertNotRegex(page, r"https?://")

    def test_cli_is_deterministic_and_invalid_csv_returns_exit_two(self):
        with tempfile.TemporaryDirectory() as directory:
            valid = Path(directory) / "valid.csv"
            invalid = Path(directory) / "invalid.csv"
            valid.write_bytes(csv_bytes([make_post()]))
            invalid.write_bytes(b"invalid")
            first_code, first_bytes = run_cli(valid)
            second_code, second_bytes = run_cli(valid)
            invalid_code, _ = run_cli(invalid)
        self.assertEqual((first_code, second_code), (0, 0))
        self.assertEqual(first_bytes, second_bytes)
        self.assertEqual(invalid_code, 2)


if __name__ == "__main__":
    unittest.main()
