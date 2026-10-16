"""Monta o quadro Kanban servido à interface web.

As colunas são as três frentes da fila (``priority.LANES``). O histórico de
negócios concluídos aparece no detalhe e no dashboard apenas como contexto.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from decimal import Decimal

from .data import CLOSED_STAGES, Dataset
from .priority import CycleReference, PriorityItem, build_queue, build_reference


def lanes(reference: CycleReference) -> list[dict]:
    limit = reference.max_cycle_days
    return [
        {"id": "negociar", "title": "Negociar",
         "rule": f"Em negociação há até {limit} dias",
         "hint": "Maior valor primeiro; no empate, o mais recente."},
        {"id": "qualificar", "title": "Qualificar",
         "rule": "Em prospecção, negociação ainda não iniciada",
         "hint": "Maior valor primeiro."},
        {"id": "encerrar", "title": "Confirmar ou encerrar",
         "rule": f"Em negociação há mais de {limit} dias",
         "hint": "Nenhuma venda demorou tanto para fechar."},
    ]


def _money(value: Decimal) -> float:
    return float(value)


def _history(dataset: Dataset) -> dict[str, dict]:
    """Ganhos, perdas e receita já concluídos por conta, vendedor e vendedor+produto."""
    groups: dict[str, dict[str, Counter]] = {
        "account": defaultdict(Counter), "agent": defaultdict(Counter),
        "agentProduct": defaultdict(Counter),
    }
    for deal in dataset.opportunities:
        if deal.deal_stage not in CLOSED_STAGES:
            continue
        outcome = "won" if deal.deal_stage == "Won" else "lost"
        keys = {"agent": deal.sales_agent, "agentProduct": f"{deal.sales_agent}|{deal.product}"}
        if deal.account is not None:
            keys["account"] = deal.account
        for group, key in keys.items():
            groups[group][key][outcome] += 1
            if outcome == "won":
                groups[group][key]["revenue"] += int(deal.close_value)
    return {group: {key: {"won": c["won"], "lost": c["lost"], "revenue": c["revenue"]}
                    for key, c in entries.items()}
            for group, entries in groups.items()}


def _closed_cycles(dataset: Dataset, reference: CycleReference) -> dict[str, list[int]]:
    """Quantos negócios concluídos fecharam com N dias em Engaging (índice = dias)."""
    counts = {"won": [0] * (reference.max_cycle_days + 1), "lost": [0] * (reference.max_cycle_days + 1)}
    for deal in dataset.opportunities:
        if deal.deal_stage in CLOSED_STAGES and deal.close_date <= reference.as_of:
            days = (deal.close_date - deal.engage_date).days
            counts["won" if deal.deal_stage == "Won" else "lost"][days] += 1
    return counts


def _card(item: PriorityItem) -> dict:
    deal = item.opportunity
    return {
        "id": deal.opportunity_id,
        "lane": item.lane,
        "phase": item.phase,
        "stage": deal.deal_stage,
        "product": deal.product,
        "price": _money(item.catalog_price),
        "account": deal.account,
        "engageDate": deal.engage_date.isoformat() if deal.engage_date else None,
        "days": item.days_in_engaging,
        "daysBeyond": item.days_beyond_cycle,
        "nextAction": item.next_action,
        "actions": list(item.actions),
        "reasons": [{"label": r.label, "value": r.value, "detail": r.detail} for r in item.reasons],
        "agent": deal.sales_agent,
        "manager": item.manager,
        "region": item.regional_office,
    }


def build_board(dataset: Dataset) -> dict:
    """Payload serializável em JSON com toda a carteira aberta ordenada."""
    reference = build_reference(dataset)
    queue = build_queue(dataset, reference=reference)
    return {
        "snapshot": reference.as_of.isoformat(),
        "reference": {
            "closed": reference.closed, "won": reference.won,
            "maxCycle": reference.max_cycle_days,
            "medianWon": reference.median_won_days, "medianLost": reference.median_lost_days,
        },
        "lanes": lanes(reference),
        "closedCycles": _closed_cycles(dataset, reference),
        "items": [_card(item) for item in queue],
        "products": {p.name: {"series": p.series, "price": _money(p.sales_price)}
                     for p in dataset.products.values()},
        "accounts": {a.name: {
            "sector": a.sector, "established": a.year_established,
            "revenue": _money(a.revenue_musd), "employees": a.employees,
            "location": a.office_location, "subsidiaryOf": a.subsidiary_of,
        } for a in dataset.accounts.values()},
        "team": [{"agent": s.name, "manager": s.manager, "region": s.regional_office}
                 for s in sorted(dataset.sales_agents.values(), key=lambda s: s.name)],
        "history": _history(dataset),
    }
