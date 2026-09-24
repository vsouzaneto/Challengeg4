"""Filter dimensions with counts: agents, managers, regions. Feeds the UI selects."""

from __future__ import annotations

from collections import defaultdict

from fastapi import APIRouter, Response

from api.routers._common import LIST_RESPONSES, AsOfQuery, load_snapshot
from api.schemas import AgentSummary, ManagerSummary, RegionSummary, ScoredDeal, TierDistribution

router = APIRouter(tags=["dimensoes"])


def tier_distribution(deals: list[ScoredDeal]) -> TierDistribution:
    counts: dict[str, int] = defaultdict(int)
    for d in deals:
        counts[d.tier] += 1
    return TierDistribution(**counts)


def _total_ev(deals: list[ScoredDeal]) -> float:
    return float(round(sum(d.expected_value for d in deals), 2))


@router.get(
    "/agents",
    response_model=list[AgentSummary],
    operation_id="list_agents",
    summary="Vendedores com deal aberto",
    description=(
        "Um item por vendedor, com gerente, região, quantidade de deals abertos, valor esperado "
        "somado e distribuição por tier. Ordenado por valor esperado decrescente."
    ),
    responses=LIST_RESPONSES,
)
def list_agents(response: Response, as_of: AsOfQuery = None) -> list[AgentSummary]:
    snap = load_snapshot(as_of, response)
    groups: dict[str, list[ScoredDeal]] = defaultdict(list)
    for d in snap.deals:
        groups[d.sales_agent].append(d)
    items = [
        AgentSummary(
            sales_agent=agent,
            manager=deals[0].manager,
            regional_office=deals[0].regional_office,
            open_deals=len(deals),
            expected_value=_total_ev(deals),
            tier_distribution=tier_distribution(deals),
        )
        for agent, deals in groups.items()
    ]
    return sorted(items, key=lambda a: (-a.expected_value, a.sales_agent))


@router.get(
    "/managers",
    response_model=list[ManagerSummary],
    operation_id="list_managers",
    summary="Gerentes e seus times",
    description="Um item por gerente com região, vendedores e totais do time.",
    responses=LIST_RESPONSES,
)
def list_managers(response: Response, as_of: AsOfQuery = None) -> list[ManagerSummary]:
    snap = load_snapshot(as_of, response)
    groups: dict[str, list[ScoredDeal]] = defaultdict(list)
    for d in snap.deals:
        groups[d.manager].append(d)
    items = [
        ManagerSummary(
            manager=manager,
            regional_office=deals[0].regional_office,
            sales_agents=sorted({d.sales_agent for d in deals}),
            open_deals=len(deals),
            expected_value=_total_ev(deals),
        )
        for manager, deals in groups.items()
    ]
    return sorted(items, key=lambda m: (-m.expected_value, m.manager))


@router.get(
    "/regions",
    response_model=list[RegionSummary],
    operation_id="list_regions",
    summary="Escritórios regionais",
    description="Um item por escritório regional com gerentes, vendedores e totais.",
    responses=LIST_RESPONSES,
)
def list_regions(response: Response, as_of: AsOfQuery = None) -> list[RegionSummary]:
    snap = load_snapshot(as_of, response)
    groups: dict[str, list[ScoredDeal]] = defaultdict(list)
    for d in snap.deals:
        groups[d.regional_office].append(d)
    items = [
        RegionSummary(
            regional_office=region,
            managers=sorted({d.manager for d in deals}),
            agents=len({d.sales_agent for d in deals}),
            open_deals=len(deals),
            expected_value=_total_ev(deals),
        )
        for region, deals in groups.items()
    ]
    return sorted(items, key=lambda r: (-r.expected_value, r.regional_office))
