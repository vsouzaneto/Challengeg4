"""Quadro Kanban: frentes, ordem e contexto histórico."""

from datetime import date, timedelta
from decimal import Decimal
from unittest import TestCase
import json

from leadscore.board import build_board
from leadscore.data import Dataset, Opportunity, Product, SalesAgent
from leadscore.priority import SNAPSHOT_DATE, build_queue


def deal(identifier, *, stage, days=None, account="Conta A", value=None, closed=None):
    engaged = SNAPSHOT_DATE - timedelta(days=days) if days is not None else None
    if closed is not None:
        engaged = closed - timedelta(days=days)
    return Opportunity(identifier, "Ana", "Caro", "Caro", account, stage, engaged, closed, value)


class BoardTests(TestCase):
    def setUp(self):
        self.dataset = Dataset(
            "fixture", {},
            {"Caro": Product("Caro", "S", Decimal("10000"))},
            {"Ana": SalesAgent("Ana", "Manager 1", "Leste")},
            (
                deal("PROS", stage="Prospecting", account=None),
                deal("NEW", stage="Engaging", days=10),
                deal("OLD", stage="Engaging", days=300),
                deal("WON", stage="Won", days=90, closed=date(2017, 6, 1), value=Decimal("9000")),
                deal("LOST", stage="Lost", days=20, closed=date(2017, 6, 1), value=Decimal("0")),
            ),
            {},
        )

    def test_board_keeps_queue_order_and_only_open_deals(self):
        board = build_board(self.dataset)
        self.assertEqual([card["id"] for card in board["items"]],
                         [item.opportunity.opportunity_id for item in build_queue(self.dataset)])
        self.assertEqual({card["id"]: card["lane"] for card in board["items"]},
                         {"NEW": "negociar", "PROS": "qualificar", "OLD": "encerrar"})
        self.assertEqual([lane["id"] for lane in board["lanes"]], ["negociar", "qualificar", "encerrar"])
        self.assertIn("90 dias", board["lanes"][0]["rule"])
        json.dumps(board)  # payload precisa ser serializável

    def test_history_is_context_from_closed_deals(self):
        board = build_board(self.dataset)
        self.assertEqual(board["history"]["account"]["Conta A"], {"won": 1, "lost": 1, "revenue": 9000})
        self.assertEqual(board["history"]["agentProduct"]["Ana|Caro"], {"won": 1, "lost": 1, "revenue": 9000})
        self.assertEqual(board["history"]["agent"]["Ana"], {"won": 1, "lost": 1, "revenue": 9000})
        self.assertEqual(board["reference"]["maxCycle"], 90)
        cycles = board["closedCycles"]
        self.assertEqual((len(cycles["won"]), cycles["won"][90], cycles["lost"][20]), (91, 1, 1))
