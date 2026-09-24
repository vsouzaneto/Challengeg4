"""Typed API errors and the single error envelope ``{"error": {"code", "message", "hint"}}``."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

PIPELINE_HINT = (
    "Rode `make pipeline` em solution/ (JDK 17/21) ou "
    "`docker compose --profile pipeline run --rm pipeline` para gerar data/gold/scores."
)


class ApiError(Exception):
    """Raised by routers/repository; rendered by :func:`install_error_handlers`."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        hint: str | None = None,
        details: list[Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.hint = hint
        self.details = details

    def to_payload(self) -> dict[str, Any]:
        body: dict[str, Any] = {"code": self.code, "message": self.message, "hint": self.hint}
        if self.details is not None:
            body["details"] = self.details
        return {"error": body}


class ArtifactsMissingError(ApiError):
    def __init__(self, message: str = "Nenhum score encontrado em data/gold/scores.") -> None:
        super().__init__(503, "ARTIFACTS_MISSING", message, PIPELINE_HINT)


class ArtifactsInvalidError(ApiError):
    def __init__(self, message: str, details: list[Any] | None = None) -> None:
        super().__init__(
            503,
            "ARTIFACTS_INVALID",
            message,
            "O parquet não satisfaz o contrato ScoredDeal. Regere com a mesma versão do pacote "
            "lead-scorer-contracts usada pela API.",
            details,
        )


class AsOfNotFoundError(ApiError):
    def __init__(self, as_of: str, available: list[str]) -> None:
        super().__init__(
            404,
            "AS_OF_NOT_FOUND",
            f"Não há partição as_of={as_of}.",
            f"Partições disponíveis: {', '.join(available) or 'nenhuma'}. Veja GET /api/v1/meta.",
        )


class DealNotFoundError(ApiError):
    def __init__(self, opportunity_id: str, as_of: str) -> None:
        super().__init__(
            404,
            "DEAL_NOT_FOUND",
            f"Deal {opportunity_id!r} não está aberto em as_of={as_of}.",
            "Confira o opportunity_id ou troque o parâmetro `as_of`.",
        )


class ModelArtifactsMissingError(ApiError):
    def __init__(self, missing: str) -> None:
        super().__init__(
            503,
            "MODEL_ARTIFACTS_MISSING",
            f"Artefato do modelo ausente: {missing}.",
            "Rode `make pipeline` (job `train`) para gerar models/<versão>/ e o ponteiro "
            "models/latest.",
        )


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def _api_error(_: Request, exc: ApiError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=exc.to_payload())

    @app.exception_handler(RequestValidationError)
    async def _validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        err = ApiError(
            422,
            "VALIDATION_ERROR",
            "Parâmetros ou corpo da requisição inválidos.",
            "Veja `details` e o schema em /docs.",
            details=[_clean(e) for e in exc.errors()],
        )
        return JSONResponse(status_code=422, content=err.to_payload())

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}.get(exc.status_code, "HTTP_ERROR")
        err = ApiError(exc.status_code, code, str(exc.detail), None)
        return JSONResponse(status_code=exc.status_code, content=err.to_payload())


def _clean(error: dict[str, Any]) -> dict[str, Any]:
    """Drop non-serialisable ``ctx`` objects from pydantic error dicts."""
    return {k: v for k, v in error.items() if k in {"type", "loc", "msg", "input"}}
