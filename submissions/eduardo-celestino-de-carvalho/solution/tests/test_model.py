"""Garantias do experimento que protegem a interpretação do resultado."""

from dataclasses import replace
from datetime import date
from decimal import Decimal
from unittest import SkipTest, TestCase
import importlib.util

# O experimento do G2 é a única parte com dependência externa; o Lead Kanban não a usa.
if importlib.util.find_spec("sklearn") is None:
    raise SkipTest("scikit-learn não instalado; ver requirements-model.txt")

from leadscore.data import Dataset, Opportunity
from leadscore.model import evaluate, features, known_outcomes, resolved_cohort


def opportunity(identifier, engaged, closed, stage, product="P"):
    return Opportunity(
        opportunity_id=identifier, sales_agent="A", product_raw=product,
        product=product, account=None, deal_stage=stage,
        engage_date=engaged, close_date=closed,
        close_value=Decimal("100") if stage == "Won" else
        Decimal("0") if stage == "Lost" else None,
    )


class TemporalModelTests(TestCase):
    def setUp(self):
        self.rows = (
            opportunity("early", date(2017, 5, 1), date(2017, 5, 20), "Won"),
            opportunity("too-recent", date(2017, 6, 15), date(2017, 6, 25), "Lost"),
            opportunity("slow", date(2017, 5, 1), date(2017, 6, 20), "Lost"),
            opportunity("open", date(2017, 7, 5), None, "Engaging"),
            opportunity("val-fast", date(2017, 7, 3), date(2017, 7, 20), "Won"),
            opportunity("val-slow", date(2017, 7, 3), date(2017, 8, 10), "Lost"),
        )
        self.dataset = Dataset("fixture", {}, {}, {}, self.rows, {})

    def test_training_needs_full_horizon_before_cutoff(self):
        self.assertEqual([o.opportunity_id for o in known_outcomes(
            self.dataset, date(2017, 6, 30))], ["early"])

    def test_validation_requires_observable_window(self):
        with self.assertRaisesRegex(ValueError, "incompleta"):
            resolved_cohort(self.dataset, date(2017, 7, 1),
                            date(2017, 7, 31), date(2017, 8, 1))
        cohort = resolved_cohort(self.dataset, date(2017, 7, 1),
                                 date(2017, 7, 31), date(2017, 8, 30))
        self.assertEqual([o.opportunity_id for o in cohort], ["val-fast"])

    def test_outcome_and_final_stage_cannot_be_features(self):
        row = self.rows[0]
        self.assertEqual(features(row, frozenset({"product", "sales_agent"})),
                         {"product": "P", "sales_agent": "A"})
        for prohibited in ("close_value", "close_date", "deal_stage", "account"):
            with self.subTest(prohibited=prohibited):
                with self.assertRaisesRegex(ValueError, "não permitidas"):
                    features(row, frozenset({prohibited}))
        self.assertEqual(features(self.rows[3], frozenset({"product"})),
                         {"product": "P"})

    def test_tied_scores_share_last_slot_independently_of_row_order(self):
        rows = [replace(self.rows[0], opportunity_id=f"W{i}") for i in range(3)]
        rows += [replace(self.rows[1], opportunity_id=f"L{i}") for i in range(3)]
        first = evaluate(rows, [0.5] * len(rows))
        second = evaluate(list(reversed(rows)), [0.5] * len(rows))
        self.assertEqual(first["wins_at_5"], 2.5)
        self.assertEqual(first["wins_at_5"], second["wins_at_5"])
