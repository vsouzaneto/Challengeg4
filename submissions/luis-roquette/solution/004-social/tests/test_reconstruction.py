from __future__ import annotations

import csv
import html
import io
import json
import sqlite3
import unittest
from unittest.mock import patch

from analysis import ACTION_TEXT, EXPORT_COLUMNS, HISTORY_EXPORT_COLUMNS, analyze, analysis_report, executive_summary, export_evidence
from storage import initialize, list_decisions, record_decision, record_import
from tests.helpers import (aggregate_effect_rows, default_scope, frame_from_rows,
                           frame_with_target, make_cohort, make_post)
from tests.test_exports import sample_result
from tests.test_storage import decision_event, import_event


def exported(result, decisions=None):
    return list(csv.DictReader(io.StringIO(export_evidence(result, decisions or []).decode())))


def references(rows, evidence_id, role):
    chunks = sorted((row for row in rows if row["record_type"] == "source_ref" and row["evidence_id"] == evidence_id
                     and row["reference_role"] == role), key=lambda row: int(row["reference_chunk"]))
    restored = {}
    for row in chunks:
        for index, fragment, line in zip(json.loads(row["reference_index"]), json.loads(row["source_row_id"]),
                                         json.loads(row["source_line"]), strict=True):
            previous = restored.get(index, ("", line))
            assert previous[1] == line
            restored[index] = (previous[0] + fragment, line)
    return [restored[index] for index in sorted(restored)]


def adversarial_decisions(source="abc"):
    events = [{**decision_event(event_id=f"e-{index}", source_hash=source,
                               decided_at=f"2025-01-{index + 1:02d}T12:00:00+00:00",
                               original_text=f"ação-{index} <script>" + "a" * 140_000),
               "decision_id": f"d-{index}"} for index in range(6)]
    events[-1].update(revision_of="d-0", status="edited", edited_text="REVISÃO RECENTE " + "b" * 140_000)
    return events + [{**events[0], "decision_id": "foreign", "source_hash": "other", "original_text": "NÃO EXIBIR OUTRA FONTE"}]


def long_label_result():
    label = "Plataforma" + "P" * 140000
    fields = ("platform", "content_type", "content_category", "audience_age_distribution",
              "audience_gender_distribution", "audience_location")
    frame = frame_from_rows([make_post(**dict.fromkeys(fields, label))])
    result = analyze(frame, default_scope(filters={"platform": [label]}), str(frame["source_hash"].iloc[0]))
    return label, result


class ReconstructionTests(unittest.TestCase):
    def test_real_long_filter_scope_round_trips_including_summary(self):
        label = "Plataforma" + "P" * 140000
        result = analyze(frame_from_rows([make_post(platform=label)]), default_scope(filters={"platform": [label]}), "hash")
        limit = csv.field_size_limit()
        payload = export_evidence(result, [])
        rows = list(csv.DictReader(io.StringIO(payload.decode())))
        summary = rows[0]
        self.assertEqual(summary["record_type"], "summary")
        self.assertEqual(summary["scope"], "")
        fragments = [row for row in rows if row["record_type"] == "analysis_field" and row["evidence_id"] == "" and row["field_name"] == "summary.scope"]
        scope = json.loads("".join(json.loads(row["field_value"]) for row in fragments))
        self.assertEqual(scope, result["scope"])
        self.assertEqual(scope["filters"]["platform"], [label])
        self.assertLessEqual(max(len(value) for row in rows for value in row.values()), 32768)
        self.assertEqual(csv.field_size_limit(), limit)
        self.assertEqual(limit, 131072)
        self.assertEqual(payload, export_evidence(result, []))

    def test_final_export_boundary_bounds_every_column_even_fragment_metadata(self):
        columns = EXPORT_COLUMNS + HISTORY_EXPORT_COLUMNS
        original = {name: "'\n=" + name + "á" * 140000 for name in columns}
        with patch("analysis._iter_export_rows", return_value=iter([dict(original)])):
            payload = export_evidence(sample_result(), [{}])
        rows = list(csv.DictReader(io.StringIO(payload.decode())))
        restored = dict(rows[0])
        for name in columns:
            parts = [row for row in rows[1:] if row["field_name"] == name]
            self.assertTrue(parts)
            self.assertEqual({row["record_type"] for row in parts}, {"export_field"})
            self.assertEqual({row["evidence_id"] for row in parts}, {"export-row-1"})
            restored[name] = "".join(json.loads(row["field_value"]) for row in parts)
        self.assertEqual(restored, original)
        self.assertLessEqual(max(len(value) for row in rows for value in row.values()), 32768)
        self.assertEqual(csv.field_size_limit(), 131072)

    def test_printed_source_labels_are_bounded_and_full_values_remain_in_csv(self):
        from html.parser import HTMLParser

        class PrintedText(HTMLParser):
            def __init__(self):
                super().__init__()
                self.hidden = 0
                self.text = []

            def handle_starttag(self, tag, attrs):
                if tag in ("details", "style"):
                    self.hidden += 1

            def handle_endtag(self, tag):
                if tag in ("details", "style"):
                    self.hidden -= 1

            def handle_data(self, value):
                if not self.hidden:
                    self.text.append(value)

        label, result = long_label_result()
        content = executive_summary(result, adversarial_decisions(result["source"]["source_hash"]))
        printed = PrintedText()
        printed.feed(content)
        text = " ".join(printed.text)
        self.assertNotIn(label, text)
        self.assertIn(label[:79] + "…", text)
        self.assertLess(len(text), 6500)
        for required in ("REVISÃO RECENTE", "SUPERADA", "outras fontes", "sem investimento", "não há ROI financeiro nem causalidade"):
            self.assertIn(required, text)
        dimension = next(item for item in result["dimensions"]["platform"] if item["value"] == label)
        rows = exported(result)
        parts = [row for row in rows if row["record_type"] == "analysis_field" and row["evidence_id"] == dimension["evidence_id"] and row["field_name"] == "evidence.text"]
        self.assertEqual("".join(json.loads(row["field_value"]) for row in parts), label)

    def test_large_analytical_fields_reconstruct_safely_with_default_reader(self):
        result = sample_result()
        text = " =" + "á" * 140000
        result["dimensions"]["platform"][0]["value"] = text
        rows = exported(result)
        base = next(row for row in rows if row["record_type"] == "evidence" and row["evidence_id"] == "dimension-1")
        self.assertEqual(base["text"], "")
        parts = [row for row in rows if row["record_type"] == "analysis_field" and row["evidence_id"] == "dimension-1" and row["field_name"] == "evidence.text"]
        self.assertEqual("".join(json.loads(row["field_value"]) for row in parts), "'" + text)
        self.assertLessEqual(max(len(value) for row in rows for value in row.values()), 32768)
        self.assertEqual(csv.field_size_limit(), 131072)

    def test_alert_target_comparator_statistics_and_filtered_summary(self):
        frame = frame_with_target(make_cohort(5, 6, [2, 4, 6, 8, 10]), 70)
        result = analyze(frame, default_scope(filters={"platform": ["Instagram"]}), "hash")
        alert = next(item for item in result["alerts"] if item["source_id"] == "target")
        rows = exported(result)
        self.assertEqual(len(references(rows, alert["evidence_id"], "target")), 1)
        self.assertEqual(len(references(rows, alert["evidence_id"], "comparator")), 30)
        summary = next(row for row in rows if row["record_type"] == "evidence" and row["evidence_id"].startswith("summary-"))
        self.assertEqual([value[0] for value in references(rows, summary["evidence_id"], "target")], ["target"])
        comparator = next(row for row in rows if row["record_type"] == "evidence_detail" and row["evidence_id"] == alert["evidence_id"] and row["reference_role"] == "comparator")
        self.assertEqual(json.loads(comparator["statistics"]), {key: value for key, value in alert["benchmark"].items() if key != "source_row_ids"})
        self.assertIn("median", json.loads(comparator["statistics"]))
        self.assertIn("effective_level", json.loads(comparator["statistics"]))

    def test_editorial_both_periods_complete_statistics_and_physical_lines(self):
        frame = aggregate_effect_rows(creators=20)
        result = analyze(frame, default_scope(target_start="2025-01-08", target_end="2025-01-14"), "hash")
        item = result["cohorts"]["editorial"][0]
        rows = exported(result)
        for role, period in (("target", "current"), ("comparator", "previous")):
            refs = references(rows, item["evidence_id"], role)
            expected = item[f"{period}_source_row_ids"]
            self.assertEqual(refs, [(key.split(":", 1)[1], result["row_references"][key]) for key in expected])
            detail = next(row for row in rows if row["record_type"] == "evidence_detail" and row["evidence_id"] == item["evidence_id"] and row["reference_role"] == role)
            self.assertEqual(json.loads(detail["statistics"]), item[period])
        self.assertEqual(len(refs), 100)

    def test_scope_recent_revisions_bounded_safe_text_and_complete_csv(self):
        result = sample_result()
        result["scope"].update(filters={"platform": ["TikTok"]}, reference_date="2025-01-15")
        decisions = adversarial_decisions()
        for content in (executive_summary(result, decisions), analysis_report(result, decisions)):
            self.assertIn("TikTok", content)
            self.assertIn("Escopo efetivo", content)
            self.assertIn("Cobertura parcial", content)
            self.assertIn("REVISÃO RECENTE", content)
            self.assertIn("SUPERADA por d-5", content)
            self.assertLess(content.index("REVISÃO RECENTE"), content.index("ação-4"))
            self.assertIn("2025-01-06", content)
            self.assertIn("outras fontes", content)
            self.assertNotIn("NÃO EXIBIR OUTRA FONTE", content)
            self.assertNotIn("<script>", content)
            self.assertNotIn("a" * 101, content)
        rows = exported(result, decisions)
        chunks = [row for row in rows if row["record_type"] == "history_field" and row["decision_id"] == "d-5" and row["field_name"] == "effective_text"]
        self.assertEqual("".join(json.loads(row["field_value"]) for row in chunks), decisions[5]["edited_text"])
        self.assertEqual(csv.field_size_limit(), 131072)

    def test_action_semantics_render_and_persist(self):
        cases = [(20, 8, "scale_test"), (20, 2, "review_stop"), (5, 8, "test")]
        for creators, interactions, action in cases:
            result = analyze(aggregate_effect_rows(creators=creators, current_interactions=interactions),
                             default_scope(target_start="2025-01-08", target_end="2025-01-14"), "source-a")
            item = next(item for item in result["recommendations"] if item["evidence_id"].startswith("editorial-"))
            self.assertEqual(item["action_type"], action)
            self.assertEqual(item["action"], ACTION_TEXT[action])
            for content in (analysis_report(result), executive_summary(result, [])):
                self.assertIn(html.escape(item["action"]), content)
                self.assertIn(item["owner"], content)
                self.assertIn(item["review_window"], content)
            conn = sqlite3.connect(":memory:")
            try:
                initialize(conn)
                record_import(conn, import_event())
                record_decision(conn, decision_event(original_text=item["action"], recommendation_key=item["recommendation_key"]))
                self.assertEqual(list_decisions(conn)[0]["original_text"], ACTION_TEXT[action])
            finally:
                conn.close()
        self.assertEqual(len(set(ACTION_TEXT.values())), len(ACTION_TEXT))

    def test_sponsorship_action_semantics_with_guard_and_persistence(self):
        for sponsored_rate, action in ((8, "sponsorship_test_after_costs"), (2, "review_renewal")):
            posts = [make_post(id=f"{flag}-{index}", content_id=f"c-{flag}-{index}", creator_id=f"creator-{index % 20}",
                               is_sponsored=str(flag).upper(), likes=sponsored_rate if flag else 4,
                               comments_count=0, shares=0)
                     for flag in (False, True) for index in range(100)]
            result = analyze(frame_from_rows(posts), default_scope(), "source-a")
            item = result["recommendations"][0]
            self.assertEqual(item["action_type"], action)
            self.assertIn(ACTION_TEXT[action], analysis_report(result))
            self.assertIn(ACTION_TEXT[action], executive_summary(result, []))
            conn = sqlite3.connect(":memory:")
            try:
                initialize(conn)
                record_import(conn, import_event())
                record_decision(conn, decision_event(original_text=item["action"]))
                self.assertEqual(list_decisions(conn)[0]["original_text"], ACTION_TEXT[action])
            finally:
                conn.close()

    def test_post_review_and_collection_actions_are_visible(self):
        result = analyze(frame_with_target(make_cohort(5, 6, [20, 21, 22, 23, 24]), 0), default_scope(), "hash")
        item = result["recommendations"][0]
        self.assertEqual(item["action_type"], "test")
        self.assertEqual(item["topic"], "creator")
        self.assertEqual(item["action"], ACTION_TEXT["test"])
        self.assertIn(ACTION_TEXT["test"], executive_summary(result, []))
        conn = sqlite3.connect(":memory:")
        try:
            initialize(conn)
            record_import(conn, import_event())
            record_decision(conn, decision_event(original_text=item["action"]))
            self.assertEqual(list_decisions(conn)[0]["original_text"], ACTION_TEXT["test"])
        finally:
            conn.close()
        sparse = analyze(frame_from_rows([make_post()]), default_scope(), "hash")
        self.assertEqual(sparse["pending"][0]["action"], ACTION_TEXT["collect"])
        self.assertIn(ACTION_TEXT["collect"], analysis_report(sparse))

    def test_audience_conditioned_effect_and_sparse_coverage(self):
        posts = [make_post(id=f"{label}-{index}", content_id=f"c-{label}-{index}", creator_id=f"creator-{index % 5}", audience_age_distribution=label,
                           likes=rate, comments_count=0, shares=0)
                 for label, rate in (("19-25", 4), ("26-35", 8)) for index in range(30)]
        for size, expected in ((60, 1), (59, 0)):
            result = analyze(frame_from_rows(posts[:size]), default_scope(), "hash")
            overview = result["audience"][0]
            self.assertEqual(overview["eligible_strata"], expected)
            self.assertEqual(overview["total_strata"], 1)
            self.assertEqual(overview["coverage"], float(expected))
            rows = exported(result)
            evidence = next(row for row in rows if row["evidence_id"] == overview["evidence_id"] and row["record_type"] == "evidence")
            self.assertEqual(json.loads(evidence["statistics"])["eligible_strata"], expected)
            self.assertIn(overview["evidence_id"], analysis_report(result))
            if expected:
                pair = overview["comparisons"][0]
                self.assertEqual(pair["delta_erv_pp"], 4)
                self.assertEqual(pair["target"]["views"], 3000)
                self.assertEqual(len(references(rows, pair["evidence_id"], "comparator")), 30)
                self.assertEqual(pair["context"]["period_month"], "2025-01")
        # Different month/platform/sponsorship cannot create a comparable label pair.
        for column, value in (("post_date", "2025-02-15"), ("platform", "TikTok"), ("is_sponsored", "TRUE")):
            separated = [dict(post) for post in posts]
            for post in separated[30:]:
                post[column] = value
            result = analyze(frame_from_rows(separated), default_scope(target_end="2025-02-28"), "hash")
            self.assertEqual(result["audience"][0]["eligible_strata"], 0)

    def test_quality_diagnostics_warnings_and_uncovered_are_scalar_rows(self):
        frame = frame_with_target(make_cohort(4, 6), 70)
        frame["engagement_rate"] = 10
        result = analyze(frame, default_scope(), "hash")
        rows = exported(result)
        diagnostics = [json.loads(row["statistics"]) for row in rows if row["record_type"] == "benchmark_diagnostic"]
        self.assertEqual(diagnostics, result["quality"]["benchmark_diagnostics"])
        self.assertEqual(len([row for row in rows if row["record_type"] == "warning"]), 1)
        uncovered = [json.loads(row["statistics"]) for row in rows if row["record_type"] == "sponsorship_uncovered"]
        self.assertEqual(uncovered, result["sponsorship"]["uncovered_strata"])
        self.assertIn("engagement_rate", executive_summary(result, []))
        self.assertIn("engagement_rate", analysis_report(result))


if __name__ == "__main__":
    unittest.main()
