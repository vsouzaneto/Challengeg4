import copy
import unittest
from pathlib import Path
from unittest.mock import patch

from app import build_payload, summarize_sales


class SalesHistoryTests(unittest.TestCase):
    def setUp(self):
        self.open_deal = {
            "opportunity_id": "OPEN-1", "deal_stage": "Prospecting", "sales_agent": "Ana",
            "account": "Conta", "product_key": "Produto", "manager": "Lia", "region": "Sul",
            "sector": "", "catalog_price": 1000, "engage_date": "", "close_value": "",
        }
        self.rows = [
            self.open_deal,
            {"deal_stage": "Won", "sales_agent": "Ana", "close_value": "125.50"},
            {"deal_stage": "Won", "sales_agent": "Ana", "close_value": "74.25"},
            {"deal_stage": "Lost", "sales_agent": "Ana", "close_value": "9000"},
            {"deal_stage": "Won", "sales_agent": "Beto", "close_value": "20"},
        ]

    def test_historical_sales_are_per_seller_and_only_wins_add_value(self):
        self.assertEqual(summarize_sales(self.rows), {
            "Ana": {"won": 2, "lost": 1, "won_value": 199.75},
            "Beto": {"won": 1, "lost": 0, "won_value": 20.0},
        })

    def test_closed_history_changes_context_without_changing_open_score(self):
        with patch("app.load_data", return_value=self.rows):
            before = build_payload(Path("unused"))
        changed = copy.deepcopy(self.rows)
        changed[1]["close_value"] = "999999"
        changed[1]["deal_stage"] = "Lost"
        changed[2]["close_date"] = "2030-01-01"
        with patch("app.load_data", return_value=changed):
            after = build_payload(Path("unused"))
        self.assertEqual(before["deals"], after["deals"])
        self.assertEqual(before["counts"], after["counts"])
        self.assertEqual(before["as_of"], after["as_of"])
        self.assertEqual(before["sales_by_agent"]["Ana"], {"won": 2, "lost": 1, "won_value": 199.75})
        self.assertEqual(after["sales_by_agent"]["Ana"], {"won": 1, "lost": 2, "won_value": 74.25})


if __name__ == "__main__":
    unittest.main()
