"""API payload models.

``ScoredDeal`` and ``Reason`` are imported, not redefined: the single source of truth is the
``lead-scorer-contracts`` package shared with the pipeline (ADR 0007). Only API-specific
envelopes live here.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any, Literal

from lead_scorer_contracts import (
    EXAMPLE_SCORED_DEAL,
    SCHEMA_VERSION,
    Confidence,
    Reason,
    ReasonCode,
    ScoredDeal,
    Tier,
)
from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "EXAMPLE_SCORED_DEAL",
    "SCHEMA_VERSION",
    "AgentSummary",
    "Confidence",
    "DealsPage",
    "ErrorBody",
    "ErrorResponse",
    "FeedbackAction",
    "FeedbackCreate",
    "FeedbackRecord",
    "HealthResponse",
    "ManagerSummary",
    "MetaResponse",
    "ModelMetricsResponse",
    "PipelineGroup",
    "PipelineSummary",
    "Reason",
    "ReasonCode",
    "RegionSummary",
    "ScoredDeal",
    "Tier",
    "TierDistribution",
]

GroupBy = Literal["sales_agent", "manager", "regional_office"]


class HealthResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"status": "ok", "version": "1.0.0"}]}
    )
    status: str = Field(description="`ok` quando o processo responde.", examples=["ok"])
    version: str = Field(description="Versão da API.", examples=["1.0.0"])


class MetaResponse(BaseModel):
    """What the UI needs before it renders anything: which snapshots exist and which model."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "schema_version": "1.0.0",
                    "as_of_available": ["2017-12-31"],
                    "default_as_of": "2017-12-31",
                    "model_version": "2017-12-31-lr-v1",
                    "artifacts_present": True,
                    "open_deals": 2089,
                    "snapshot_date": "2017-12-31",
                }
            ]
        }
    )
    schema_version: str = Field(description="Versão do contrato `ScoredDeal`.")
    as_of_available: list[date] = Field(
        description="Partições `as_of=` encontradas em gold/scores, em ordem crescente."
    )
    default_as_of: date | None = Field(
        description="Partição mais recente (snapshot padrão da UI). Nulo se não há artefatos."
    )
    model_version: str | None = Field(
        description="Versão apontada por `models/latest`. Nulo se o pipeline ainda não rodou."
    )
    artifacts_present: bool = Field(
        description="Falso quando não há scores: a UI mostra como gerar em vez de uma tabela vazia."
    )
    open_deals: int | None = Field(
        default=None,
        description="Quantidade de deals abertos na partição padrão. Nulo sem artefatos.",
    )
    snapshot_date: date = Field(
        default=date(2017, 12, 31),
        description="Data do snapshot do CRM: toda idade/tempo é ancorada aqui, nunca em hoje.",
    )


class ErrorBody(BaseModel):
    code: str = Field(
        description="Código estável, em SCREAMING_SNAKE_CASE.",
        examples=["ARTIFACTS_MISSING", "DEAL_NOT_FOUND", "VALIDATION_ERROR"],
    )
    message: str = Field(
        description="Mensagem em pt-BR para exibir ao usuário.",
        examples=["Nenhum score encontrado em data/gold/scores."],
    )
    hint: str | None = Field(
        default=None,
        description="Como resolver: comando a rodar, parâmetro a corrigir ou rota a consultar.",
        examples=["Rode `make pipeline` ou `docker compose --profile pipeline run --rm pipeline`."],
    )
    details: list[Any] | None = Field(
        default=None,
        description="Detalhes estruturados (erros de validação campo a campo, linhas inválidas).",
    )


class ErrorResponse(BaseModel):
    """Standard error envelope: ``{"error": {"code", "message", "hint"}}``."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "error": {
                        "code": "ARTIFACTS_MISSING",
                        "message": "Nenhum score encontrado em data/gold/scores.",
                        "hint": "Rode `make pipeline` em solution/ (JDK 17/21).",
                    }
                }
            ]
        }
    )
    error: ErrorBody


class DealsPage(BaseModel):
    """Paginated list of scored deals plus the snapshot it came from."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "items": [EXAMPLE_SCORED_DEAL],
                    "total": 2089,
                    "limit": 50,
                    "offset": 0,
                    "sort": "-priority_score",
                    "as_of": "2017-12-31",
                    "model_version": "2017-12-31-lr-v1",
                }
            ]
        }
    )
    items: list[ScoredDeal] = Field(description="Deals da página, já filtrados e ordenados.")
    total: int = Field(
        ge=0, description="Total de deals que satisfazem os filtros (sem paginação)."
    )
    limit: int = Field(ge=1, description="Tamanho da página aplicado.")
    offset: int = Field(ge=0, description="Deslocamento aplicado.")
    sort: str = Field(description="Ordenação aplicada, no formato `-campo,campo`.")
    as_of: date = Field(description="Partição servida.")
    model_version: str = Field(description="Versão do modelo que gerou os scores desta partição.")


class TierDistribution(BaseModel):
    """Count of open deals per tier."""

    model_config = ConfigDict(json_schema_extra={"examples": [{"A": 5, "B": 12, "C": 20, "D": 9}]})
    A: int = Field(default=0, ge=0)  # noqa: N815 - tier labels are the domain vocabulary
    B: int = Field(default=0, ge=0)  # noqa: N815
    C: int = Field(default=0, ge=0)  # noqa: N815
    D: int = Field(default=0, ge=0)  # noqa: N815


class AgentSummary(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "sales_agent": "Darcel Schlecht",
                    "manager": "Melvin Marxen",
                    "regional_office": "Central",
                    "open_deals": 46,
                    "expected_value": 91250.5,
                    "tier_distribution": {"A": 12, "B": 14, "C": 12, "D": 8},
                }
            ]
        }
    )
    sales_agent: str = Field(description="Nome do vendedor (valor a usar em `?sales_agent=`).")
    manager: str = Field(description="Gerente do vendedor.")
    regional_office: str = Field(description="Escritório regional.")
    open_deals: int = Field(ge=0, description="Deals abertos no snapshot.")
    expected_value: float = Field(ge=0, description="Soma de `expected_value` dos deals abertos.")
    tier_distribution: TierDistribution


class ManagerSummary(BaseModel):
    manager: str = Field(description="Nome do gerente (valor a usar em `?manager=`).")
    regional_office: str = Field(description="Escritório regional do time.")
    sales_agents: list[str] = Field(description="Vendedores do time, em ordem alfabética.")
    open_deals: int = Field(ge=0)
    expected_value: float = Field(ge=0)


class RegionSummary(BaseModel):
    regional_office: str = Field(description="Escritório regional (`?regional_office=`).")
    managers: list[str] = Field(description="Gerentes do escritório, em ordem alfabética.")
    agents: int = Field(ge=0, description="Quantidade de vendedores com deal aberto.")
    open_deals: int = Field(ge=0)
    expected_value: float = Field(ge=0)


class PipelineGroup(BaseModel):
    """Manager-level view of one slice of the pipeline (an agent, a manager or a region)."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "key": "Melvin Marxen",
                    "open_deals": 320,
                    "engaging": 245,
                    "prospecting": 75,
                    "expected_value": 512340.0,
                    "zombie_count": 18,
                    "zombie_value": 22110.0,
                    "nominal_zombie_value": 109300.0,
                    "cooling_count": 24,
                    "cooling_value": 30150.0,
                    "account_coverage": 0.31,
                    "tier_distribution": {"A": 80, "B": 80, "C": 80, "D": 80},
                    "avg_priority_score": 51.3,
                }
            ]
        }
    )
    key: str = Field(description="Valor da dimensão agrupada (vendedor, gerente ou região).")
    open_deals: int = Field(ge=0, description="Deals abertos.")
    engaging: int = Field(ge=0, description="Deals em Engaging.")
    prospecting: int = Field(
        ge=0, description="Deals em Prospecting (sem data, urgência desconhecida)."
    )
    expected_value: float = Field(ge=0, description="Soma de `expected_value`.")
    zombie_count: int = Field(
        ge=0, description="Deals com `days_in_engaging` > 138 (ciclo máximo observado)."
    )
    zombie_value: float = Field(ge=0, description="`expected_value` preso nesses zumbis.")
    nominal_zombie_value: float | None = Field(
        description=(
            "Soma de `sales_price` (valor nominal, fora do forecast) dos zumbis. Nulo quando a "
            "partição não traz `sales_price`; 0 quando não há zumbis."
        )
    )
    cooling_count: int = Field(
        ge=0, description="Deals esfriando: `days_in_engaging` entre 101 e 138 (inclusive)."
    )
    cooling_value: float = Field(ge=0, description="`expected_value` dos deals esfriando.")
    account_coverage: float = Field(
        ge=0, le=1, description="Fração de deals com conta conhecida (~0,32 no snapshot)."
    )
    tier_distribution: TierDistribution
    avg_priority_score: float = Field(ge=0, le=100, description="Média de `priority_score`.")


class PipelineSummary(BaseModel):
    group_by: GroupBy = Field(description="Dimensão usada nos grupos.")
    as_of: date
    model_version: str
    zombie_threshold_days: int = Field(description="Limiar de zumbi aplicado (138).")
    cooling_min_days: int = Field(description="Início da faixa 'esfriando' (101).")
    total: PipelineGroup = Field(description="Agregado do recorte inteiro (key = `*`).")
    groups: list[PipelineGroup] = Field(description="Um item por valor da dimensão.")


class ModelMetricsResponse(BaseModel):
    """Backtest metrics and model card location as written by the ``train`` job."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "model_version": "2017-12-31-lr-v1",
                    "metrics": {
                        "backtest": {
                            "2017-09-30": {"precision_at_10": 0.78, "brier": 0.21},
                        },
                        "baselines": {"random": {"precision_at_10": 0.63}},
                    },
                    "feature_list": ["product_base_rate", "days_in_engaging"],
                    "model_card_path": "models/2017-12-31-lr-v1/model_card.md",
                    "model_card_markdown": "# Model card\n...",
                }
            ]
        }
    )
    model_version: str = Field(description="Versão apontada por `models/latest`.")
    metrics: dict[str, Any] = Field(
        description="Conteúdo de `metrics.json` (backtest vs. baselines, calibração). Livre."
    )
    feature_list: list[str] | None = Field(
        default=None, description="Conteúdo de `feature_list.json`, se presente."
    )
    model_card_path: str = Field(description="Caminho do `model_card.md`, relativo a solution/.")
    model_card_markdown: str | None = Field(
        default=None, description="Texto do model card (pt-BR) para renderizar na UI."
    )


class FeedbackAction(StrEnum):
    """What the seller did after seeing the recommendation."""

    CONTACTED = "contacted"
    MEETING_SCHEDULED = "meeting_scheduled"
    PROPOSAL_SENT = "proposal_sent"
    DISCARD = "discard"
    ACCOUNT_FIXED = "account_fixed"
    NOTE = "note"
    CLOSED_IN_CRM = "closed_in_crm"


class FeedbackCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "opportunity_id": "Z063OYW0",
                    "action": "contacted",
                    "note": "Falei com o comprador; reunião na quinta.",
                    "actor": "Darcel Schlecht",
                }
            ]
        }
    )
    opportunity_id: str = Field(min_length=1, max_length=32, description="Deal alvo da ação.")
    action: FeedbackAction = Field(
        description=(
            "`contacted`, `meeting_scheduled`, `proposal_sent`, `discard` (ocultar da minha "
            "fila), `account_fixed` (conta preenchida no CRM), `closed_in_crm` (vendedor "
            "encerrou o deal no CRM) ou `note`."
        )
    )
    note: str | None = Field(
        default=None, max_length=500, description="Observação livre, até 500 caracteres."
    )
    actor: str = Field(
        min_length=1, max_length=120, description="Quem registrou (nome do vendedor/gerente)."
    )


class FeedbackRecord(FeedbackCreate):
    """Persisted row of ``data/feedback/actions.parquet``."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "8f1c2a9e4b7d4e1f9c3a5b6d7e8f9a0b",
                    "opportunity_id": "Z063OYW0",
                    "action": "contacted",
                    "note": "Falei com o comprador; reunião na quinta.",
                    "actor": "Darcel Schlecht",
                    "recorded_at": "2026-09-23T13:45:12.123456Z",
                    "as_of": "2017-12-31",
                    "model_version": "2017-12-31-lr-v1",
                    "priority_score": 82.4,
                }
            ]
        }
    )
    id: str = Field(description="UUID4 hexadecimal do registro.")
    recorded_at: datetime = Field(
        description="Carimbo de auditoria (UTC). Única hora real do sistema; nunca entra no score."
    )
    as_of: date = Field(description="Partição em que o deal foi visto ao registrar a ação.")
    model_version: str = Field(description="Versão do modelo exibida ao usuário naquele momento.")
    priority_score: float = Field(ge=0, le=100, description="Score mostrado no momento da ação.")
