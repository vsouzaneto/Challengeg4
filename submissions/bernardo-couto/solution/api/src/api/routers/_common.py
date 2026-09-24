"""Shared query parameters, response headers and OpenAPI ``responses`` blocks."""

from __future__ import annotations

from datetime import date
from typing import Annotated, Any

from fastapi import Query, Response

from api.repository import Snapshot, repository
from api.schemas import ErrorResponse

AsOfQuery = Annotated[
    date | None,
    Query(
        description=(
            "Partição a servir (`YYYY-MM-DD`). Padrão: a mais recente listada em `GET /meta`. "
            "Cortes de backtest (ex.: `2017-09-30`) mostram o que o vendedor teria visto."
        ),
        examples=["2017-12-31"],
    ),
]


def load_snapshot(as_of: date | None, response: Response) -> Snapshot:
    """Resolve the partition and stamp the contract headers on the response."""
    snap = repository.snapshot(as_of)
    response.headers["X-As-Of"] = snap.as_of.isoformat()
    response.headers["X-Model-Version"] = snap.model_version
    return snap


def _err(description: str, code: str, message: str, hint: str) -> dict[str, Any]:
    return {
        "description": description,
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {"error": {"code": code, "message": message, "hint": hint}}
            }
        },
    }


ERR_503 = _err(
    "Artefatos do pipeline ausentes ou inválidos.",
    "ARTIFACTS_MISSING",
    "Nenhum score encontrado em data/gold/scores.",
    "Rode `make pipeline` em solution/ ou `docker compose --profile pipeline run --rm pipeline`.",
)
ERR_404_AS_OF = _err(
    "Partição `as_of` inexistente.",
    "AS_OF_NOT_FOUND",
    "Não há partição as_of=2016-01-01.",
    "Partições disponíveis: 2017-12-31. Veja GET /api/v1/meta.",
)
ERR_404_DEAL = _err(
    "Deal não encontrado na partição (ou `as_of` inexistente).",
    "DEAL_NOT_FOUND",
    "Deal 'XXXX' não está aberto em as_of=2017-12-31.",
    "Confira o opportunity_id ou troque o parâmetro `as_of`.",
)
ERR_422 = _err(
    "Parâmetro ou corpo inválido.",
    "VALIDATION_ERROR",
    "Parâmetros ou corpo da requisição inválidos.",
    "Veja `details` e o schema em /docs.",
)

HEADERS_DOC: dict[str, Any] = {
    "X-As-Of": {"description": "Partição servida (YYYY-MM-DD).", "schema": {"type": "string"}},
    "X-Model-Version": {
        "description": "Versão do modelo que gerou os scores.",
        "schema": {"type": "string"},
    },
}


def ok_with_headers(description: str) -> dict[int | str, dict[str, Any]]:
    return {200: {"description": description, "headers": HEADERS_DOC}}


LIST_RESPONSES: dict[int | str, dict[str, Any]] = {
    **ok_with_headers("Sucesso."),
    404: ERR_404_AS_OF,
    422: ERR_422,
    503: ERR_503,
}
