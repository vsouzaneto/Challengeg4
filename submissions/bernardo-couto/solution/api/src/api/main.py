"""FastAPI application factory. Routers are mounted under ``/api/v1``."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import __version__
from api.errors import ApiError, install_error_handlers
from api.repository import repository
from api.routers import deals, dimensions, feedback, health, meta, model, pipeline
from api.settings import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("api")

DESCRIPTION = """
API do **Lead Scorer**: prioriza os deals abertos do CRM para o vendedor saber em quais focar.

**Como o score é calculado (resumo):**

1. `p_win` — probabilidade de fechar, por regras transparentes (taxa-base por produto, histórico
   do vendedor, sobrevivência em Engaging) combinadas a um modelo Spark ML treinado no histórico.
2. `expected_value` — preço de tabela × razão histórica de fechamento do produto × `p_win`.
3. `urgency` — quanto agir esta semana muda o desfecho (janela de decisão do ciclo).
4. `priority_score` (0–100) e `tier` (A–D) combinam os três com pesos nomeados.
5. Cada deal traz `reasons` em português, com o número que justifica cada linha.

A API **só lê** o parquet gerado pelo pipeline (`data/gold/scores/as_of=…`); nenhum score é
recalculado aqui. Snapshot dos dados: **2017-12-31** — nenhuma rota usa a data de hoje.

**Convenções**

* Prefixo `/api/v1`; toda resposta com dados de score traz os headers `X-As-Of` e
  `X-Model-Version`.
* Erros sempre no envelope `{"error": {"code", "message", "hint"}}`; `503` significa
  "pipeline ainda não rodou" e o `hint` diz o comando.
* Paginação `limit`/`offset` + `total`; ordenação `sort=-campo,campo`.

Documentação completa no serviço `docs` (`http://localhost:8001`).
"""

OPENAPI_TAGS = [
    {"name": "operacao", "description": "Saúde do serviço."},
    {
        "name": "meta",
        "description": "Descoberta de snapshots (`as_of`), versão do modelo e contagens.",
    },
    {
        "name": "deals",
        "description": "Deals pontuados: lista filtrável, detalhe e explicação (reason codes).",
    },
    {
        "name": "dimensoes",
        "description": "Vendedores, gerentes e regiões com contagens, para preencher filtros.",
    },
    {
        "name": "pipeline",
        "description": "Visão do gerente: zumbis, valor em risco, cobertura de conta por recorte.",
    },
    {
        "name": "modelo",
        "description": "Métricas do backtest temporal vs. baselines e model card.",
    },
    {
        "name": "feedback",
        "description": "Ações registradas pelo vendedor sobre um deal (loop de aprendizado).",
    },
]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Fail fast on an invalid parquet; keep serving (with 503s) when there is none yet."""
    if settings.validate_on_boot:
        try:
            snap = repository.warm_up()
        except ApiError as exc:
            log.error("boot_validation_failed code=%s message=%s", exc.code, exc.message)
            raise RuntimeError(f"{exc.code}: {exc.message} {exc.hint or ''}".strip()) from exc
        if snap is not None:
            log.info(
                "boot_ok as_of=%s deals=%d model_version=%s",
                snap.as_of.isoformat(),
                len(snap.deals),
                snap.model_version,
            )
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Lead Scorer API",
        version=__version__,
        summary="Priorização explicável de deals abertos para o time de vendas.",
        description=DESCRIPTION,
        openapi_tags=OPENAPI_TAGS,
        contact={"name": "Bernardo Couto"},
        license_info={"name": "MIT"},
        servers=[
            {"url": "http://localhost:8000", "description": "Local / Docker Compose"},
        ],
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
        expose_headers=["X-As-Of", "X-Model-Version"],
    )
    install_error_handlers(app)
    for router in (
        health.router,
        meta.router,
        deals.router,
        dimensions.router,
        pipeline.router,
        model.router,
        feedback.router,
    ):
        app.include_router(router, prefix=settings.api_prefix)
    return app


app = create_app()
