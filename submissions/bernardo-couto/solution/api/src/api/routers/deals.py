"""Scored deals: filterable list and per-deal detail. Pure read over the loaded snapshot."""

from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Path, Query, Response

from api.errors import ApiError
from api.repository import (
    DEFAULT_SORT,
    SORTABLE_FIELDS,
    Queue,
    filter_deals,
    parse_sort,
    sort_deals,
)
from api.routers._common import (
    ERR_404_DEAL,
    ERR_422,
    ERR_503,
    LIST_RESPONSES,
    AsOfQuery,
    load_snapshot,
    ok_with_headers,
)
from api.schemas import DealsPage, ScoredDeal
from api.settings import ZOMBIE_DAYS

router = APIRouter(tags=["deals"])


@router.get(
    "/deals",
    response_model=DealsPage,
    operation_id="list_deals",
    summary="Lista deals pontuados com filtros, ordenação e paginação",
    description=(
        "Retorna os deals abertos da partição `as_of` (padrão: a mais recente), ordenados por "
        "`priority_score` decrescente. Filtros combinam por **E**. `total` conta os deals que "
        "satisfazem os filtros antes da paginação.\n\n"
        "Exemplos:\n\n"
        "* Top 10 de um vendedor: `?sales_agent=Darcel%20Schlecht&limit=10`\n"
        "* Time de um gerente sem conta cadastrada: "
        "`?manager=Melvin%20Marxen&account_known=false`\n"
        "* Deals mais antigos em Engaging primeiro: "
        "`?deal_stage=Engaging&sort=-days_in_engaging`\n"
        "* Fila **Trabalhar** (vivos + Prospecting): `?queue=work`; fila **Confirmar ou "
        f"encerrar** (parados > {ZOMBIE_DAYS} dias): `?queue=confirm&sort=-expected_value`\n"
        "* Primeira onda de parados (139-180 dias): "
        "`?queue=confirm&min_days_in_engaging=139&max_days_in_engaging=180`\n\n"
        f"Campos ordenáveis: `{'`, `'.join(sorted(SORTABLE_FIELDS))}`. Prefixo `-` inverte."
    ),
    responses=LIST_RESPONSES,
)
def list_deals(
    response: Response,
    sales_agent: Annotated[
        str | None, Query(description="Nome exato do vendedor.", examples=["Darcel Schlecht"])
    ] = None,
    manager: Annotated[
        str | None, Query(description="Nome exato do gerente.", examples=["Melvin Marxen"])
    ] = None,
    regional_office: Annotated[
        str | None,
        Query(description="Escritório regional.", examples=["Central", "East", "West"]),
    ] = None,
    deal_stage: Annotated[
        Literal["Prospecting", "Engaging"] | None,
        Query(description="Estágio do deal aberto."),
    ] = None,
    tier: Annotated[
        Literal["A", "B", "C", "D"] | None, Query(description="Faixa de prioridade.")
    ] = None,
    min_score: Annotated[
        float | None,
        Query(ge=0, le=100, description="Só deals com `priority_score >= min_score`."),
    ] = None,
    account_known: Annotated[
        bool | None,
        Query(
            description=(
                "`true`: só deals com conta; `false`: só sem conta (~68% dos abertos). "
                "Omitido: todos."
            )
        ),
    ] = None,
    queue: Annotated[
        Queue | None,
        Query(
            description=(
                f"`work`: deals vivos (`days_in_engaging` <= {ZOMBIE_DAYS}) e Prospecting (sem "
                f"data); `confirm`: parados há mais de {ZOMBIE_DAYS} dias, para confirmar ou "
                "encerrar no CRM. Omitido: ambas as filas."
            )
        ),
    ] = None,
    min_days_in_engaging: Annotated[
        int | None,
        Query(ge=0, description="Só deals com `days_in_engaging >= valor` (exclui Prospecting)."),
    ] = None,
    max_days_in_engaging: Annotated[
        int | None,
        Query(ge=0, description="Só deals com `days_in_engaging <= valor` (exclui Prospecting)."),
    ] = None,
    as_of: AsOfQuery = None,
    sort: Annotated[
        str,
        Query(
            description="Campos separados por vírgula; `-` para decrescente.",
            examples=["-priority_score", "-expected_value,sales_agent"],
        ),
    ] = DEFAULT_SORT,
    limit: Annotated[int, Query(ge=1, le=500, description="Tamanho da página.")] = 50,
    offset: Annotated[int, Query(ge=0, description="Itens a pular.")] = 0,
) -> DealsPage:
    try:
        keys = parse_sort(sort)
    except ValueError as exc:
        raise ApiError(422, "INVALID_SORT", str(exc), "Veja a lista de campos em /docs.") from exc
    snap = load_snapshot(as_of, response)
    matched = filter_deals(
        snap.deals,
        sales_agent=sales_agent,
        manager=manager,
        regional_office=regional_office,
        deal_stage=deal_stage,
        tier=tier,
        min_score=min_score,
        account_known=account_known,
        queue=queue,
        min_days_in_engaging=min_days_in_engaging,
        max_days_in_engaging=max_days_in_engaging,
    )
    ordered = sort_deals(matched, keys)
    return DealsPage(
        items=ordered[offset : offset + limit],
        total=len(matched),
        limit=limit,
        offset=offset,
        sort=",".join(("-" if desc else "") + name for name, desc in keys),
        as_of=snap.as_of,
        model_version=snap.model_version,
    )


@router.get(
    "/deals/{opportunity_id}",
    response_model=ScoredDeal,
    operation_id="get_deal",
    summary="Detalhe de um deal: score, explicações e próxima ação",
    description=(
        "Um deal com `p_win`, `expected_value`, `urgency`, `confidence`, as `reasons` em "
        "português ordenadas por |peso| e a `next_action` sugerida. É o payload da tela de "
        "detalhe: o vendedor deve entender *por que* o score em menos de um minuto."
    ),
    responses={
        **ok_with_headers("Deal encontrado."),
        404: ERR_404_DEAL,
        422: ERR_422,
        503: ERR_503,
    },
)
def get_deal(
    response: Response,
    opportunity_id: Annotated[
        str, Path(min_length=1, max_length=32, description="ID da oportunidade no CRM.")
    ],
    as_of: AsOfQuery = None,
) -> ScoredDeal:
    snap = load_snapshot(as_of, response)
    return snap.get(opportunity_id)
