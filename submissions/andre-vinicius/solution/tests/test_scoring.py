import copy
import json
import threading
import unittest
from datetime import date
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen

from app import build_payload, handler_factory
from scoring import load_data, prioritize, rank_open


ROOT = Path(__file__).resolve().parents[1]


class ScoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_data(ROOT / "data")

    def test_real_data_joins_and_alias(self):
        self.assertEqual(len(self.rows), 8800)
        self.assertTrue(any(r["product"] == "GTXPro" and r["product_key"] == "GTX Pro" and r["catalog_price"] > 0 for r in self.rows))
        self.assertTrue(any(not r["account"] for r in self.rows))

    def test_open_deals_only_and_deterministic_order(self):
        as_of, ranked = rank_open(self.rows)
        self.assertEqual(as_of, date(2017, 12, 31))
        self.assertEqual(len(ranked), 2089)
        self.assertEqual(len({r["id"] for r in ranked}), len(ranked))
        self.assertEqual({r["stage"] for r in ranked}, {"Prospecting", "Engaging"})
        self.assertEqual([r["queue"] for r in ranked], sorted((r["queue"] for r in ranked), key={"Avançar": 0, "Revisar": 1, "Qualificar": 2}.get))
        self.assertEqual(ranked, rank_open(self.rows)[1])

    def test_closed_outcome_does_not_affect_open_priority(self):
        row = next(r for r in self.rows if r["deal_stage"] == "Engaging")
        before = prioritize(row, date(2017, 12, 31))
        changed = copy.deepcopy(row)
        changed.update(close_value="999999999", close_date="2030-01-01")
        self.assertEqual(before, prioritize(changed, date(2017, 12, 31)))

    def test_outcome_dates_do_not_change_snapshot_or_ranking(self):
        before = rank_open(self.rows)
        changed = copy.deepcopy(self.rows)
        changed[0]["close_date"] = "2030-01-01"
        changed[0]["close_value"] = "999999999"
        self.assertEqual(before, rank_open(changed))

    def test_missing_engagement_date_and_stable_tie(self):
        sample = copy.deepcopy(next(r for r in self.rows if r["deal_stage"] == "Prospecting"))
        sample.update(opportunity_id="B", engage_date="", close_date="", close_value="")
        other = copy.deepcopy(sample)
        other["opportunity_id"] = "A"
        as_of, ranked = rank_open([sample, other])
        self.assertEqual(as_of, date(2017, 12, 31))
        self.assertEqual([r["id"] for r in ranked], ["A", "B"])
        self.assertEqual(ranked[0]["days_engaged"], None)
        self.assertIn("sem data", " ".join(ranked[0]["reasons"]).lower())

    def test_missing_account_still_has_action_and_explanation(self):
        row = next(r for r in self.rows if r["deal_stage"] == "Prospecting" and not r["account"])
        result = prioritize(row, date(2017, 12, 31))
        self.assertEqual(result["queue"], "Qualificar")
        self.assertIn("Conta ausente", " ".join(result["reasons"]))
        self.assertTrue(result["next_action"])

    def test_payload_counts_match_lists(self):
        payload = build_payload(ROOT / "data")
        self.assertEqual(sum(payload["counts"].values()), len(payload["deals"]))
        self.assertEqual(payload["as_of"], "2017-12-31")

    def test_http_serves_application_and_real_ranked_data(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler_factory(build_payload(ROOT / "data")))
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            base = f"http://127.0.0.1:{server.server_port}"
            with urlopen(base + "/") as response:
                html = response.read().decode("utf-8")
                self.assertIn("Decida o próximo contato.", html)
                self.assertIn('data-view="table"', html)
                self.assertIn("/documentation.html", html)
            with urlopen(base + "/method.html") as response:
                method = response.read().decode("utf-8")
                self.assertIn("Como o índice é calculado", method)
                self.assertIn("Desfecho, valor e data de fechamento não pontuam", method)
            with urlopen(base + "/documentation.html") as response:
                self.assertIn("Especificação funcional", response.read().decode("utf-8"))
            with urlopen(base + "/reader.html?doc=technical-spec") as response:
                self.assertIn("reader.js", response.read().decode("utf-8"))
            with urlopen(base + "/source/test-plan.md") as response:
                self.assertIn("plano de testes", response.read().decode("utf-8").lower())
            with urlopen(base + "/source/case-development.md") as response:
                self.assertIn("Como o Foco foi desenvolvido com o Demiurgo", response.read().decode("utf-8"))
            with urlopen(base + "/evidence/gerentes-desktop.png") as response:
                self.assertTrue(response.read().startswith(b"\x89PNG\r\n\x1a\n"))
            with urlopen(base + "/api/deals") as response:
                self.assertTrue(response.headers["Content-Type"].startswith("application/json"))
                data = json.load(response)
            self.assertEqual(len(data["deals"]), 2089)
            self.assertTrue(data["deals"][0]["reasons"])
            with urlopen(base + "/filter.js") as response:
                self.assertIn("filterDeals", response.read().decode("utf-8"))
            with urlopen(base + "/panels.html") as response:
                html = response.read().decode("utf-8")
                self.assertIn("Painéis do negócio", html)
                self.assertIn('data-panel="vendedor"', html)
                self.assertIn('data-panel="preco"', html)
            with urlopen(base + "/annotations.js") as response:
                self.assertIn("saveAnnotation", response.read().decode("utf-8"))
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
