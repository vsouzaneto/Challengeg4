"""Manager view: zombies, value at risk and account coverage per agent / manager / region."""

from __future__ import annotations

from collections import defaultdict
from typing import Annotated

from fastapi import APIRouter, Query, Response

from api.repository import filter_deals
from api.routers._common import LIST_RESPONSES, AsOfQuery, load_snapshot
from api.routers.dimensions import tier_distribution
from api.schemas import GroupBy, PipelineGroup, PipelineSummary, ScoredDeal
from api.settings import COOLING_MIN_DAYS, ZOMBIE_DAYS

router = APIRouter(tags=["pipeline"])


def summarise(key: str, deals: list[ScoredDeal]) -> PipelineGroup:
    zombies = [d for d in deals if (d.days_in_engaging or 0) > ZOMBIE_DAYS]
    cooling = [
        d
        for d in deals
        if d.days_in_engaging is not None and COOLING_MIN_DAYS <= d.days_in_engaging <= ZOMBIE_DAYS
    ]
    priced_zombies = [d.sales_price for d in zombies if d.sales_price is not None]
    nominal_zombie_value: float | None
    if not zombies:
        nominal_zombie_value = 0.0
    elif priced_zombies:
        nominal_zombie_value = round(sum(priced_zombies), 2)
    else:
        nominal_zombie_value = None  # partition written before sales_price existed
    known = sum(1 for d in deals if d.account is not None)
    n = len(deals)
    return PipelineGroup(
        key=key,
        open_deals=n,
        engaging=sum(1 for d in deals if d.deal_stage == "Engaging"),
        prospecting=sum(1 for d in deals if d.deal_stage == "Prospecting"),
        expected_value=round(sum(d.expected_value for d in deals), 2),
        zombie_count=len(zombies),
        zombie_value=round(sum(d.expected_value for d in zombies), 2),
        nominal_zombie_value=nominal_zombie_value,
        cooling_count=len(cooling),
        cooling_value=round(sum(d.expected_value for d in cooling), 2),
        account_coverage=round(known / n, 4) if n else 0.0,
        tier_distribution=tier_distribution(deals),
        avg_priority_score=round(sum(d.priority_score for d in deals) / n, 2) if n else 0.0,
    )


@router.get(
    "/pipeline/summary",
    response_model=PipelineSummary,
    operation_id="get_pipeline_summary",
    summary="Resumo do pipeline para o gerente",
    description=(
        "Agrega os deals abertos por vendedor, gerente ou região: quantidade, valor esperado, "
        f"**zumbis** (`days_in_engaging` > {ZOMBIE_DAYS}, o ciclo máximo observado nos Won) com o "
        "valor preso neles (esperado e nominal, quando `sales_price` existe na partição), deals "
        f"**esfriando** ({COOLING_MIN_DAYS}-{ZOMBIE_DAYS} dias), cobertura de conta (fração "
        "com `account` preenchida) e distribuição "
        "por tier. Os filtros restringem o recorte antes de agrupar: um gerente passa "
        "`?manager=...&group_by=sales_agent` para ver seu time vendedor a vendedor."
    ),
    responses=LIST_RESPONSES,
)
def get_pipeline_summary(
    response: Response,
    group_by: Annotated[GroupBy, Query(description="Dimensão dos grupos.")] = "manager",
    sales_agent: Annotated[str | None, Query(description="Restringe a um vendedor.")] = None,
    manager: Annotated[str | None, Query(description="Restringe a um gerente.")] = None,
    regional_office: Annotated[str | None, Query(description="Restringe a uma região.")] = None,
    as_of: AsOfQuery = None,
) -> PipelineSummary:
    snap = load_snapshot(as_of, response)
    deals = filter_deals(
        snap.deals, sales_agent=sales_agent, manager=manager, regional_office=regional_office
    )
    groups: dict[str, list[ScoredDeal]] = defaultdict(list)
    for d in deals:
        groups[getattr(d, group_by)].append(d)
    items = sorted(
        (summarise(k, v) for k, v in groups.items()),
        key=lambda g: (-g.expected_value, g.key),
    )
    return PipelineSummary(
        group_by=group_by,
        as_of=snap.as_of,
        model_version=snap.model_version,
        zombie_threshold_days=ZOMBIE_DAYS,
        cooling_min_days=COOLING_MIN_DAYS,
        total=summarise("*", deals),
        groups=items,
    )
