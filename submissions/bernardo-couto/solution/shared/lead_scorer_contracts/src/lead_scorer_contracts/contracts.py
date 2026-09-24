"""Pydantic v2 models for the ``gold/scores`` parquet and the ``/api/v1/deals`` payloads.

Field order and names follow the ``scoring-methodology`` skill verbatim. Descriptions and
examples are in pt-BR because they surface in Swagger for a Brazilian sales audience.
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = "1.2.0"

Tier = Literal["A", "B", "C", "D"]
Confidence = Literal["alta", "media", "baixa"]
Direction = Literal["+", "-", "i"]


class ReasonCode(StrEnum):
    """Closed set of reason codes. Every rule in the pipeline emits exactly one of these."""

    PRODUCT_BASE_RATE = "PRODUCT_BASE_RATE"
    AGENT_TRACK_RECORD = "AGENT_TRACK_RECORD"
    AGENT_PRODUCT_FIT = "AGENT_PRODUCT_FIT"
    SECTOR_FIT = "SECTOR_FIT"
    ACCOUNT_SIZE = "ACCOUNT_SIZE"
    ACCOUNT_HISTORY = "ACCOUNT_HISTORY"
    ACCOUNT_UNKNOWN = "ACCOUNT_UNKNOWN"
    SURVIVAL_POSITIVE = "SURVIVAL_POSITIVE"
    ZOMBIE_RISK = "ZOMBIE_RISK"
    HIGH_TICKET = "HIGH_TICKET"
    LOW_TICKET = "LOW_TICKET"
    PROSPECTING_NO_TIMELINE = "PROSPECTING_NO_TIMELINE"
    AGENT_OVERLOAD = "AGENT_OVERLOAD"
    URGENCY_WINDOW = "URGENCY_WINDOW"
    MODEL_CONTRIBUTION = "MODEL_CONTRIBUTION"


class Reason(BaseModel):
    """One explanation line, in the seller's voice, with the number that justifies it."""

    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "code": "ZOMBIE_RISK",
                    "direction": "-",
                    "weight": -16.5,
                    "text_pt": (
                        "142 dias em Engaging: acima do ciclo máximo observado (138). "
                        "Confirme se o deal ainda existe."
                    ),
                }
            ]
        },
    )

    code: ReasonCode = Field(
        description="Código estável da regra ou contribuição que gerou esta explicação.",
        examples=["PRODUCT_BASE_RATE", "ZOMBIE_RISK"],
    )
    direction: Direction = Field(
        description="Direção do efeito no score: '+' aumenta, '-' reduz, 'i' informativo.",
        examples=["+", "-", "i"],
    )
    weight: float = Field(
        description=(
            "Contribuição em pontos de priority_score (escala 0-100); reason codes "
            "informativos têm peso 0. As reasons são ordenadas por |peso| decrescente."
        ),
        examples=[9.0, -16.5, 0.0],
    )
    text_pt: str = Field(
        min_length=1,
        max_length=400,
        description="Frase curta em pt-BR na voz do vendedor, com o número que a justifica.",
        examples=["78 dias em Engaging: acima da mediana de fechamento deste produto (57)."],
    )


class ScoreBreakdown(BaseModel):
    """Decomposição aditiva do ``priority_score`` em pontos (0-100).

    ``p_win_points + value_points + urgency_points == priority_score`` (tolerância 0,01).
    Pesos padrão: 25 (probabilidade), 35 (valor esperado, escala log) e 40 (urgência).
    """

    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "examples": [{"p_win_points": 17.1, "value_points": 29.6, "urgency_points": 39.2}]
        },
    )

    p_win_points: float = Field(
        description=(
            "Pontos da probabilidade: 25 x clip((p_win - 0,30) / 0,50, 0, 1). Em deals parados "
            "(> 138 dias) já inclui a redução pela metade do p_win e o teto de 49."
        ),
        examples=[17.1],
    )
    value_points: float = Field(
        ge=0,
        description="Pontos do valor: 35 x log1p(preço x razão histórica) / log1p(26.768).",
        examples=[29.6],
    )
    urgency_points: float = Field(
        ge=0,
        description="Pontos da urgência: 40 x urgency (hazard de Won em 14 dias dado a idade).",
        examples=[39.2],
    )


EXAMPLE_SCORED_DEAL: dict[str, Any] = {
    "opportunity_id": "Z063OYW0",
    "sales_agent": "Darcel Schlecht",
    "manager": "Melvin Marxen",
    "regional_office": "Central",
    "product": "GTX Pro",
    "account": "Konex",
    "deal_stage": "Engaging",
    "days_in_engaging": 78,
    "priority_score": 82.4,
    "tier": "A",
    "p_win": 0.71,
    "expected_value": 3412.5,
    "sales_price": 4821.0,
    "urgency": 0.8,
    "confidence": "alta",
    "score_breakdown": {"p_win_points": 20.5, "value_points": 29.9, "urgency_points": 32.0},
    "reasons": [
        {
            "code": "AGENT_PRODUCT_FIT",
            "direction": "+",
            "weight": 9.0,
            "text_pt": "Você fecha 74% dos GTX Pro (média do time: 63%).",
        },
        {
            "code": "SURVIVAL_POSITIVE",
            "direction": "+",
            "weight": 0.6,
            "text_pt": ("78 dias em Engaging: deals que passam de 60 dias fecham em 68%."),
        },
    ],
    "next_action": "Ligar esta semana e propor data de fechamento.",
    "as_of": "2017-12-31",
    "model_version": "2017-12-31-lr-v1",
}


class ScoredDeal(BaseModel):
    """One open deal at ``as_of`` with its priority score and explanation.

    This is the row schema of ``gold/scores/as_of=YYYY-MM-DD`` and the item schema of the
    API. The API never recomputes anything: it only reads and filters these rows.
    """

    model_config = ConfigDict(frozen=True, json_schema_extra={"examples": [EXAMPLE_SCORED_DEAL]})

    opportunity_id: str = Field(
        min_length=1,
        description="Identificador único da oportunidade no CRM.",
        examples=["Z063OYW0"],
    )
    sales_agent: str = Field(description="Vendedor responsável.", examples=["Darcel Schlecht"])
    manager: str = Field(description="Gerente do vendedor.", examples=["Melvin Marxen"])
    regional_office: str = Field(
        description="Escritório regional do vendedor.", examples=["Central", "East", "West"]
    )
    product: str = Field(
        description="Produto (nome conformado ao catálogo).", examples=["GTX Pro", "MG Special"]
    )
    account: str | None = Field(
        default=None,
        description="Conta (cliente). Ausente em ~68% dos deals abertos; nunca descarta o deal.",
        examples=["Konex", None],
    )
    deal_stage: Literal["Prospecting", "Engaging"] = Field(
        description="Estágio atual do deal aberto.", examples=["Engaging"]
    )
    days_in_engaging: int | None = Field(
        default=None,
        ge=0,
        description="Dias desde engage_date até as_of. Nulo em Prospecting (sem data).",
        examples=[78, None],
    )
    priority_score: float = Field(
        ge=0,
        le=100,
        description="Score de prioridade 0-100 = f(p_win, expected_value, urgency).",
        examples=[82.4],
    )
    tier: Tier = Field(description="Faixa A-D por quantis do priority_score.", examples=["A"])
    p_win: float = Field(
        ge=0, le=1, description="Probabilidade estimada de fechar (calibrada).", examples=[0.71]
    )
    expected_value: float = Field(
        ge=0,
        description=(
            "Valor esperado = sales_price x razão histórica de fechamento do produto x p_win."
        ),
        examples=[3412.5],
    )
    sales_price: float | None = Field(
        default=None,
        ge=0,
        description=(
            "Preço de tabela do produto (valor nominal, sem probabilidade). Nulo em partições "
            "geradas antes do schema 1.1.0."
        ),
        examples=[4821.0, None],
    )
    urgency: float = Field(
        ge=0,
        le=1,
        description="Urgência 0-1: quanto a ação do vendedor esta semana muda o desfecho.",
        examples=[0.8],
    )
    confidence: Confidence = Field(
        description="Confiança na estimativa: cai sem conta conhecida ou com histórico pequeno.",
        examples=["alta", "media", "baixa"],
    )
    score_breakdown: ScoreBreakdown | None = Field(
        default=None,
        description=(
            "Decomposição do priority_score em pontos (probabilidade + valor + urgência). "
            "Nulo em partições geradas antes do schema 1.2.0."
        ),
    )
    reasons: list[Reason] = Field(
        min_length=1,
        description="Explicações ordenadas por |peso|, misturando regras e modelo.",
    )
    next_action: str = Field(
        min_length=1,
        description="Próximo passo sugerido, em uma frase.",
        examples=["Ligar esta semana e propor data de fechamento."],
    )
    as_of: date = Field(
        description="Data de referência do score (snapshot ou corte de backtest).",
        examples=["2017-12-31"],
    )
    model_version: str = Field(
        min_length=1,
        description="Versão do modelo/regras que gerou o score (pasta em models/).",
        examples=["2017-12-31-lr-v1"],
    )
