"""Fronteiras da regra de prioridade, com linhas sintéticas (não dependem dos CSVs)."""
import unittest
from datetime import date, timedelta

from scoring import canonical_product, prioritize, rank_open

AS_OF = date(2017, 12, 31)


def engaged(days):
    return (AS_OF - timedelta(days=days)).isoformat()


def deal(stage="Engaging", days=45, account="Conta", price=1000.0, opportunity_id="X"):
    return {
        "opportunity_id": opportunity_id, "deal_stage": stage,
        "engage_date": engaged(days) if days is not None else "",
        "account": account, "catalog_price": price, "product_key": "Produto",
        "sales_agent": "Ana", "manager": "Lia", "region": "Sul", "sector": "",
    }


class PriorityRuleTests(unittest.TestCase):
    def test_ninety_day_limit_splits_advance_from_review(self):
        at_limit = prioritize(deal(days=90), AS_OF)
        past_limit = prioritize(deal(days=91), AS_OF)
        self.assertEqual((at_limit["queue"], at_limit["priority"]), ("Avançar", 75))
        self.assertEqual((past_limit["queue"], past_limit["priority"]), ("Revisar", 60))

    def test_recent_bonus_applies_up_to_thirty_days_in_advance_only(self):
        self.assertEqual(prioritize(deal(days=30), AS_OF)["priority"], 85)
        self.assertEqual(prioritize(deal(days=31), AS_OF)["priority"], 75)

    def test_old_bonus_applies_from_one_hundred_eighty_days_in_review_only(self):
        self.assertEqual(prioritize(deal(days=179), AS_OF)["priority"], 60)
        self.assertEqual(prioritize(deal(days=180), AS_OF)["priority"], 70)

    def test_catalog_price_bonus_starts_at_four_thousand(self):
        below = prioritize(deal(stage="Prospecting", price=3999.99), AS_OF)
        at_limit = prioritize(deal(stage="Prospecting", price=4000), AS_OF)
        self.assertEqual((below["queue"], below["priority"]), ("Qualificar", 45))
        self.assertEqual(at_limit["priority"], 55)

    def test_highest_index_per_queue_stays_below_the_cap(self):
        advance = prioritize(deal(days=0, price=4000), AS_OF)
        review = prioritize(deal(days=180, price=4000), AS_OF)
        qualify = prioritize(deal(stage="Prospecting", days=None, price=4000), AS_OF)
        self.assertEqual([advance["priority"], review["priority"], qualify["priority"]], [95, 80, 55])

    def test_prospecting_ignores_engagement_age(self):
        result = prioritize(deal(stage="Prospecting", days=400), AS_OF)
        self.assertEqual((result["queue"], result["priority"], result["days_engaged"]), ("Qualificar", 45, 400))

    def test_engaging_without_date_enters_advance_without_time_bonus(self):
        result = prioritize(deal(days=None), AS_OF)
        self.assertEqual((result["queue"], result["priority"], result["days_engaged"]), ("Avançar", 75, None))
        self.assertIn("Ainda sem data de engajamento", result["reasons"])

    def test_missing_account_loses_bonus_and_is_explained(self):
        result = prioritize(deal(days=45, account=""), AS_OF)
        self.assertEqual((result["account"], result["priority"]), ("Conta não informada", 65))
        self.assertIn("Conta ausente: preencher antes de avançar", result["reasons"])

    def test_queue_order_beats_index_order(self):
        review_high = deal(days=200, price=4000, opportunity_id="R")
        advance_low = deal(days=45, account="", price=100, opportunity_id="A")
        _, ranked = rank_open([review_high, advance_low], AS_OF)
        self.assertEqual([(r["id"], r["queue"], r["priority"]) for r in ranked],
                         [("A", "Avançar", 65), ("R", "Revisar", 80)])

    def test_closed_deals_are_rejected_and_skipped(self):
        with self.assertRaises(ValueError):
            prioritize(deal(stage="Won"), AS_OF)
        _, ranked = rank_open([deal(stage="Lost", opportunity_id="L"), deal(opportunity_id="O")], AS_OF)
        self.assertEqual([r["id"] for r in ranked], ["O"])

    def test_catalog_alias_is_only_the_documented_one(self):
        self.assertEqual(canonical_product("GTXPro"), "GTX Pro")
        self.assertEqual(canonical_product("GTX Basic"), "GTX Basic")


if __name__ == "__main__":
    unittest.main()
