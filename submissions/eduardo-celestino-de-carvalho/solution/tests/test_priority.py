"""Comportamentos comerciais críticos da fila de foco."""

from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal
from unittest import TestCase

from leadscore.data import Dataset, Opportunity, Product, SalesAgent
from leadscore.priority import (SNAPSHOT_DATE, build_queue, build_reference, filter_queue,
                                score_opportunity)


def open_deal(identifier, *, product="Caro", stage="Engaging", days=None, account="Conta A", agent="Ana"):
    engaged = SNAPSHOT_DATE - timedelta(days=days) if days is not None else None
    return Opportunity(identifier, agent, product, product, account, stage, engaged, None, None)


def closed_deal(identifier, *, cycle, won, closed=date(2017, 6, 30)):
    return Opportunity(identifier, "Ana", "Barato", "Barato", "Conta A", "Won" if won else "Lost",
                       closed - timedelta(days=cycle), closed, Decimal("100" if won else "0"))


class PriorityTests(TestCase):
    def setUp(self):
        # Histórico: ciclo máximo de 100 dias; perdas rápidas, ganhos mais lentos.
        history = (closed_deal("W1", cycle=60, won=True), closed_deal("W2", cycle=100, won=True),
                   closed_deal("L1", cycle=10, won=False))
        self.open = (
            open_deal("NEW_CHEAP", product="Barato", days=10),
            open_deal("NEW_RICH", days=20),
            open_deal("OLD_RICH", days=80),
            open_deal("STALE_RICH", days=250),
            open_deal("PROS", stage="Prospecting", account=None),
        )
        self.dataset = Dataset(
            "fixture", {},
            {name: Product(name, "S", Decimal(price)) for name, price in (
                ("Barato", "100"), ("Caro", "10000"))},
            {"Ana": SalesAgent("Ana", "Manager 1", "Leste"),
             "Beto": SalesAgent("Beto", "Manager 2", "Oeste")},
            history + self.open, {},
        )
        self.reference = build_reference(self.dataset)

    def by_id(self):
        return {item.opportunity.opportunity_id: item for item in build_queue(self.dataset)}

    def test_reference_uses_only_deals_closed_until_snapshot(self):
        self.assertEqual(self.reference.max_cycle_days, 100)
        self.assertEqual((self.reference.closed, self.reference.won), (3, 2))
        self.assertEqual(self.reference.median_lost_days, 10)
        # Antes do primeiro fechamento não há referência: nada posterior ao corte entra.
        with self.assertRaisesRegex(ValueError, "Sem negócios concluídos"):
            build_reference(self.dataset, date(2017, 6, 29))

    def test_deal_beyond_historical_cycle_goes_to_cleanup(self):
        stale = self.by_id()["STALE_RICH"]
        self.assertEqual(stale.lane, "encerrar")
        self.assertEqual(stale.days_beyond_cycle, 150)
        self.assertIn("atualizar a etapa", stale.next_action)

    def test_focus_ranks_by_value_and_prefers_recent_on_ties(self):
        queue = build_queue(self.dataset)
        focus = [item.opportunity.opportunity_id for item in queue if item.lane == "negociar"]
        self.assertEqual(focus, ["NEW_RICH", "OLD_RICH", "NEW_CHEAP"])
        lanes = [item.lane for item in queue]
        self.assertEqual(lanes, sorted(lanes, key=["negociar", "qualificar", "encerrar"].index))

    def test_stale_expensive_deal_never_outranks_focus(self):
        queue = build_queue(self.dataset)
        ids = [item.opportunity.opportunity_id for item in queue]
        self.assertLess(ids.index("NEW_CHEAP"), ids.index("STALE_RICH"))

    def test_phases_follow_days_in_engaging(self):
        items = self.by_id()
        self.assertEqual(items["NEW_CHEAP"].phase, "Início")
        self.assertEqual(items["NEW_RICH"].phase, "Em andamento")
        self.assertEqual(items["OLD_RICH"].phase, "Em andamento")
        late = score_opportunity(self.dataset, open_deal("LATE", days=95), self.reference)
        self.assertEqual(late.phase, "Perto do limite")

    def test_prospecting_without_date_or_account_gets_qualification(self):
        item = self.by_id()["PROS"]
        self.assertEqual(item.lane, "qualificar")
        self.assertIsNone(item.days_in_engaging)
        self.assertIn("Identificar e registrar a conta relacionada", item.actions)
        self.assertTrue(item.account_missing)

    def test_missing_account_adds_task_without_changing_order(self):
        with_account = score_opportunity(self.dataset, self.open[1], self.reference)
        without = score_opportunity(self.dataset, replace(self.open[1], account=None), self.reference)
        self.assertEqual((with_account.lane, with_account.phase), (without.lane, without.phase))
        self.assertEqual(len(without.actions), len(with_account.actions) + 1)

    def test_outcome_cannot_enter_priority(self):
        with self.assertRaisesRegex(ValueError, "apenas Prospecting ou Engaging"):
            score_opportunity(self.dataset, replace(self.open[0], deal_stage="Won"), self.reference)
        with self.assertRaisesRegex(ValueError, "desfecho"):
            score_opportunity(self.dataset, replace(self.open[0], close_value=Decimal("100")),
                              self.reference)

    def test_filters_keep_order(self):
        extra = open_deal("BETO", days=5, agent="Beto")
        dataset = replace(self.dataset, opportunities=self.dataset.opportunities + (extra,))
        queue = build_queue(dataset)
        self.assertEqual([i.opportunity.opportunity_id for i in filter_queue(queue, regional_office="Oeste")],
                         ["BETO"])
        cleanup = filter_queue(queue, lanes=frozenset({"encerrar"}))
        self.assertEqual([i.opportunity.opportunity_id for i in cleanup], ["STALE_RICH"])
        self.assertEqual(filter_queue(queue, search="pros")[0].lane, "qualificar")
