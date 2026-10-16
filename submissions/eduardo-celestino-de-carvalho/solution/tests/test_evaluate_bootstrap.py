"""Bootstrap pareado do backtest: determinístico e coerente com os totais."""

from unittest import TestCase

from evaluate_focus import bootstrap, price_recency, price_only


class _Item:
    def __init__(self, price, days):
        self.catalog_price, self.days_in_engaging = price, days


class BootstrapTests(TestCase):
    def test_same_seed_same_interval_and_point_matches_totals(self):
        units = [(120.0, 100.0), (90.0, 100.0), (150.0, 100.0), (110.0, 100.0)]
        first, second = bootstrap(units, reps=500), bootstrap(units, reps=500)
        self.assertEqual(first, second)
        self.assertAlmostEqual(first["lift"], 470 / 400 - 1, places=4)
        self.assertLessEqual(first["ci95"][0], first["lift"])
        self.assertGreaterEqual(first["ci95"][1], first["lift"])

    def test_recency_breaks_price_ties_but_not_price(self):
        new, old, pricey = (_Item(100, 10), None), (_Item(100, 90), None), (_Item(200, 300), None)
        self.assertEqual(sorted([old, new, pricey], key=price_recency), [pricey, new, old])
        self.assertEqual(price_only(new), price_only(old))  # só valor: empate, a vaga é dividida
