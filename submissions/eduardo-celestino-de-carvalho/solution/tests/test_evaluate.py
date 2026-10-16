"""Backtest: o corte só enxerga o que se sabia naquela data."""

from datetime import date
from decimal import Decimal
from unittest import TestCase

from evaluate_focus import evaluate_cutoff, open_at, quantile_days
from leadscore.data import Dataset, Opportunity, Product, SalesAgent


def deal(identifier, stage, engaged, closed=None, value=None):
    return Opportunity(identifier, "Ana", "P", "P", "Conta", stage, engaged, closed, value)


class EvaluateTests(TestCase):
    def setUp(self):
        self.dataset = Dataset(
            "fixture", {}, {"P": Product("P", "S", Decimal("100"))},
            {"Ana": SalesAgent("Ana", "M", "R")},
            (
                deal("OLD_WIN", "Won", date(2017, 1, 1), date(2017, 2, 10), Decimal("100")),
                deal("LATER_WIN", "Won", date(2017, 5, 1), date(2017, 7, 15), Decimal("100")),
                deal("STUCK", "Engaging", date(2017, 1, 15)),
                deal("FUTURE", "Engaging", date(2017, 8, 1)),
            ),
            {},
        )

    def test_open_at_hides_future_outcomes_and_future_deals(self):
        seen = {as_seen.opportunity_id: as_seen for as_seen, _ in open_at(self.dataset, date(2017, 6, 30))}
        self.assertEqual(set(seen), {"LATER_WIN", "STUCK"})
        self.assertEqual(seen["LATER_WIN"].deal_stage, "Engaging")
        self.assertIsNone(seen["LATER_WIN"].close_value)

    def test_cutoff_reference_and_lanes_use_only_past_closures(self):
        result = evaluate_cutoff(self.dataset, date(2017, 6, 30))
        self.assertEqual(result["reference"]["closed"], 1)
        self.assertEqual(result["reference"]["max_cycle_days"], 40)
        self.assertEqual(result["lanes"]["encerrar"]["deals"], 2)  # 60 e 166 dias > 40

    def test_percentile_threshold_uses_only_past_cycles(self):
        # Até 30/09 fecharam ciclos de 40 e 75 dias; o percentil não enxerga o futuro.
        self.assertEqual(quantile_days(self.dataset, date(2017, 6, 30), 0.95), 40)
        self.assertEqual(quantile_days(self.dataset, date(2017, 9, 30), 0.50), 40)
        self.assertEqual(quantile_days(self.dataset, date(2017, 9, 30), 0.95), 75)

    def test_robustness_max_threshold_matches_main_rule(self):
        result = evaluate_cutoff(self.dataset, date(2017, 6, 30))
        robust = result["robustness"]
        self.assertEqual(robust["threshold"]["max"]["focus_rule"], result["top5_per_agent"]["focus_rule"])
        self.assertEqual(robust["tie_break"]["recent_first"], result["top5_per_agent"]["focus_rule"])
