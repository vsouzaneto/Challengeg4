from __future__ import annotations

import unittest

from analysis import analyze, decision_baseline, observe_evidence
from tests.helpers import (aggregate_effect_rows, default_scope, frame_from_rows,
                           frame_with_target, make_cohort, make_post, sponsorship_rows)


class DecisionEvidenceTests(unittest.TestCase):
    def baseline(self, frame, **scope):
        result = analyze(frame, default_scope(**scope), str(frame["source_hash"].iloc[0]))
        snapshot = result["recommendations"][0]["evidence_snapshot"]
        return decision_baseline(snapshot), snapshot

    def test_sponsorship_snapshot_and_creator_statistic_exclude_organic_and_audience_distractors(self):
        frame = sponsorship_rows()
        baseline, snapshot = self.baseline(frame, target_start="2025-01-01", target_end="2025-01-31", filters={"audience_location": ["BR"]})
        self.assertEqual(snapshot["family"], "sponsorship")
        self.assertEqual((baseline["median"], baseline["n_rate"], baseline["creators"]), (8.0, 30, 5))
        self.assertEqual(snapshot["target"]["creator_median_erv"], 8.0)
        self.assertEqual(snapshot["comparator"]["creator_median_erv"], 4.0)
        self.assertEqual(len(snapshot["references"]["target"]), 30)
        self.assertEqual(len(snapshot["references"]["comparator"]), 30)
        self.assertEqual(baseline["evidence_snapshot"], snapshot)
        self.assertTrue(baseline["contract"]["context"]["is_sponsored"])
        self.assertEqual(baseline["statistic"], "median_creator_erv")
        # Unequal creator posting frequency: post median 90, creator median 9.
        rows = [make_post(id=f"observed-{i}", content_id=f"observed-{i}", creator_id="heavy" if i < 40 else f"c-{i % 4}",
                         post_date="2025-02-15T12:00:00", likes=90 if i < 40 else 9,
                         shares=0, comments_count=0, is_sponsored="TRUE") for i in range(64)]
        rows += [make_post(id=f"organic-{i}", content_id=f"organic-{i}", post_date="2025-02-15T12:00:00", likes=99) for i in range(80)]
        rows += [make_post(id=f"other-audience-{i}", content_id=f"other-audience-{i}", post_date="2025-02-15T12:00:00", likes=99, is_sponsored="TRUE", audience_location="US") for i in range(80)]
        observed = observe_evidence(frame_from_rows(rows), baseline, {"target_start": "2025-02-01", "target_end": "2025-02-28"}, "later")
        self.assertEqual((observed["median"], observed["median_erv"], observed["n_rate"]), (9.0, 90.0, 64))
        self.assertEqual(observed["contract"], baseline["contract"])

    def test_editorial_reapplies_all_segment_controls_and_counts_only_defined_creators(self):
        frame = aggregate_effect_rows()
        baseline, snapshot = self.baseline(frame, target_start="2025-01-08", target_end="2025-01-14")
        self.assertEqual(snapshot["family"], "editorial")
        self.assertEqual((baseline["median"], baseline["n_rate"]), (8.0, 100))
        self.assertEqual(len(snapshot["references"]["comparator"]), 100)
        rows = [make_post(id=f"target-{i}", content_id=f"target-{i}", creator_id=f"c-{i % 4}",
                         post_date="2025-01-18T12:00:00", likes=9, shares=0, comments_count=0) for i in range(30)]
        for kind, change in enumerate(({"content_category": "beauty"}, {"is_sponsored": "TRUE"},
                                      {"follower_count": 2_000_000}, {"audience_location": "US"},
                                      {"audience_gender_distribution": "male"}, {"audience_age_distribution": "26-35"})):
            rows += [make_post(id=f"d-{kind}-{i}", content_id=f"d-{kind}-{i}", creator_id=f"d-{i}",
                               post_date="2025-01-18T12:00:00", likes=99, shares=0, comments_count=0, **change) for i in range(30)]
        rows.append(make_post(id="undefined", content_id="undefined", creator_id="fifth-undefined", post_date="2025-01-18T12:00:00", views=0))
        observed = observe_evidence(frame_from_rows(rows), baseline, {"target_start": "2025-01-15", "target_end": "2025-01-21", "filters": {"content_category": ["beauty"]}}, "later")
        self.assertEqual((observed["median"], observed["n_rate"], observed["creators"], observed["posts"]), (9.0, 30, 4, 31))
        self.assertEqual(observed["median"] - baseline["median"], 1.0)
        self.assertEqual(observed["contract"], baseline["contract"])

    def test_post_snapshot_keeps_target_benchmark_and_separate_context_baseline(self):
        frame = frame_with_target(make_cohort(erv_values=[2, 4, 6, 8, 10, 12], audience_location="US"), 30)
        baseline, snapshot = self.baseline(frame)
        self.assertEqual(snapshot["family"], "post")
        self.assertEqual(snapshot["target"]["erv"], 30)
        self.assertEqual(snapshot["comparator"]["effective_level"], "core+age+gender/365d")
        self.assertEqual(snapshot["comparator"]["n_rate"], 30)
        self.assertIn("q1", snapshot["comparator"])
        self.assertIn("strength", snapshot)
        self.assertEqual(len(snapshot["references"]["comparator"]), 30)
        self.assertEqual(snapshot["context_aggregate"]["n_rate"], 1)
        self.assertEqual(baseline["creators"], 1)
        self.assertEqual(baseline["evidence_snapshot"], snapshot)

    def test_editorial_snapshot_excludes_sponsored_rows_of_the_same_context(self):
        rows = aggregate_effect_rows().drop(columns=["source_hash", "source_row_id", "source_line"]).to_dict("records")
        for row in rows:
            row["is_sponsored"] = "FALSE"
        sponsored = [{**row, "id": "s-" + row["id"], "content_id": "s-" + row["content_id"], "is_sponsored": "TRUE", "likes": 99} for row in rows]
        frame = frame_from_rows(rows + sponsored)
        result = analyze(frame, default_scope(target_start="2025-01-08", target_end="2025-01-14"), "mixed")
        recommendation = next(item for item in result["recommendations"] if item["evidence_snapshot"]["family"] == "editorial")
        baseline = decision_baseline(recommendation["evidence_snapshot"])
        self.assertEqual((baseline["median"], baseline["n_rate"]), (8.0, 100))
        self.assertFalse(baseline["contract"]["context"]["is_sponsored"])
