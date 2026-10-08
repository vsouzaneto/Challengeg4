import copy
import hashlib
import unittest

from data import DATA_DIR, load_data
from scoring import assign_priority_scores, confidence, score_open_opportunities


class ScoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = load_data()

    def test_dataset_regression_and_source_integrity(self):
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in DATA_DIR.glob("*.csv")}
        result = score_open_opportunities(load_data())
        after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in DATA_DIR.glob("*.csv")}
        self.assertEqual(before, after)
        self.assertEqual(result.historical_count, 6711)
        self.assertAlmostEqual(result.historical_win_rate, 4238 / 6711)
        self.assertEqual(len(result.opportunities), 2089)
        self.assertEqual(len({r['opportunity_id'] for r in result.opportunities}), 2089)
        self.assertEqual(result.confidence_counts, {"Alta": 1407, "Média": 667, "Baixa": 15})
        self.assertEqual(sum(r["watchlist"] for r in result.opportunities), 15)
        self.assertEqual(result.watchlist_price_threshold, 4821)
        self.assertNotIn("GTXPro", {r["product"] for r in result.opportunities})
        self.assertTrue(all(0 <= r["priority_score"] <= 100 for r in result.opportunities))

    def test_forbidden_fields_do_not_affect_ranking(self):
        changed = copy.deepcopy(self.dataset)
        for row in changed.opportunities:
            row["close_value"] = "999999999"
            row["account"] = ""
            if row["deal_stage"] in {"Prospecting", "Engaging"}:
                row["close_date"] = "2099-01-01"
        for row in changed.accounts.values():
            row["sector"] = "alterado"
        for row in changed.sales_teams.values():
            row["manager"] = row["regional_office"] = "alterado"
        original = score_open_opportunities(self.dataset).opportunities
        updated = score_open_opportunities(changed).opportunities
        for left, right in zip(original, updated):
            for key in ("opportunity_id", "historical_fit", "balanced_priority", "priority_score", "watchlist"):
                self.assertEqual(left[key], right[key])

    def test_future_outcomes_are_excluded(self):
        changed = copy.deepcopy(self.dataset)
        future = copy.deepcopy(changed.closed_opportunities[0])
        future.update(opportunity_id="FUTURE", close_date="2099-01-01", deal_stage="Won")
        changed.opportunities.append(future)
        self.assertEqual(score_open_opportunities(self.dataset), score_open_opportunities(changed))

    def test_unseen_groups_use_baseline_without_dropping_opportunity(self):
        changed = copy.deepcopy(self.dataset)
        row = changed.open_opportunities[0]
        row["product"] = "NEW"
        row["sales_agent"] = "NEW"
        changed.products["NEW"] = {"sales_price": "100000"}
        result = score_open_opportunities(changed)
        scored = next(r for r in result.opportunities if r["opportunity_id"] == row["opportunity_id"])
        self.assertEqual(len(result.opportunities), 2089)
        self.assertEqual((scored["n_product"], scored["n_sales_agent"]), (0, 0))
        self.assertEqual(scored["historical_fit"], result.historical_win_rate)
        self.assertEqual(scored["confidence"], "Baixa")
        self.assertTrue(scored["watchlist"])

    def test_shrinkage_uses_observed_counts(self):
        result = score_open_opportunities(self.dataset)
        row = next(r for r in result.opportunities if r["product"] == "GTK 500")
        self.assertEqual(row["n_product"], 25)
        self.assertAlmostEqual(row["product_adjusted_rate"], (15 + 50 * (4238 / 6711)) / 75)
        self.assertAlmostEqual(row["historical_fit"], (row["product_adjusted_rate"] + row["sales_agent_adjusted_rate"]) / 2)

    def test_rank_ties_and_edge_cases(self):
        rows = [{"balanced_priority": v} for v in [10, 20, 20, 30]]
        assign_priority_scores(rows)
        self.assertEqual([r["priority_score"] for r in rows], [0, 50, 50, 100])
        for values in ([10], [10, 10, 10]):
            rows = [{"balanced_priority": v} for v in values]
            assign_priority_scores(rows)
            self.assertTrue(all(r["priority_score"] == 50 for r in rows))
        assign_priority_scores([])

    def test_confidence_boundaries(self):
        for counts, expected in [((200, 200), "Alta"), ((200, 199), "Média"), ((50, 50), "Média"), ((49, 200), "Baixa"), ((0, 500), "Baixa")]:
            self.assertEqual(confidence(*counts), expected)

    def test_empty_history_fails_explicitly(self):
        changed = copy.deepcopy(self.dataset)
        changed.opportunities = changed.open_opportunities
        with self.assertRaisesRegex(ValueError, "Sem resultados históricos"):
            score_open_opportunities(changed)


if __name__ == "__main__":
    unittest.main()
