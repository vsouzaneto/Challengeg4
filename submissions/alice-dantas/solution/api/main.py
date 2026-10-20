"""API HTTP fina sobre o núcleo (ADR-003): só traduz o payload de `views` para JSON.

Rodar (em solution/): `.venv/bin/uvicorn api.main:app --port 8000`.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from leadscorer import data, evidence, intelligence, policy, views
from leadscorer.errors import DataError, LeadScorerError, NotFoundError, PolicyError

from .schemas import (ErrorBody, Evidence, Intelligence, IntelligenceDeals, Meta, Rules, SellerList, SellerPipeline,
                      TeamPipeline)

WEB_ORIGIN = "http://localhost:3000"
STATUS = ((DataError, 503), (PolicyError, 422), (NotFoundError, 404))

# Erros que cada rota pode devolver, todos com o mesmo corpo {"detail", "code", "params"}.
DATA_ERROR = {503: {"model": ErrorBody, "description": "CSVs ausentes ou inválidos, ou sem venda ganha até o as_of"}}
AS_OF_ERROR = {422: {"model": ErrorBody, "description": "as_of inválido"}}
NOT_FOUND = {404: {"model": ErrorBody, "description": "Vendedor não encontrado"}}
EVIDENCE_ERROR = {503: {"model": ErrorBody, "description": "Resultado do backtest ausente, inválido ou de outra regra"}}
PARAMETER_ERROR = {422: {"model": ErrorBody, "description": "as_of, outcome ou group inválido"}}


# Os filtros chegam como texto e o núcleo decide: valor inexistente dá recorte vazio, nunca erro.
def intelligence_filters(product: Optional[str] = None, seller: Optional[str] = None, manager: Optional[str] = None,
                         office: Optional[str] = None, sector: Optional[str] = None, account: Optional[str] = None,
                         size: Optional[str] = None) -> intelligence.Filters:
    return intelligence.Filters(product=product, seller=seller, manager=manager, office=office, sector=sector,
                                account=account, size=size)


def create_app(raw_dir: Path = policy.RAW_DIR, evidence_path: Path = policy.EVIDENCE_PATH) -> FastAPI:
    app = FastAPI(title="Lead Scorer", version="0.1.0")
    app.add_middleware(CORSMiddleware, allow_origins=[WEB_ORIGIN], allow_methods=["GET"])
    cache: Dict[str, data.Dataset] = {}

    def dataset() -> data.Dataset:
        # Carga preguiçosa: a API sobe sem os CSVs e responde 503 até eles existirem.
        if "dataset" not in cache:
            cache["dataset"] = data.load(raw_dir)
        return cache["dataset"]

    @app.exception_handler(LeadScorerError)
    async def user_error(_: Request, error: LeadScorerError) -> JSONResponse:
        status = next((code for kind, code in STATUS if isinstance(error, kind)), 500)
        return JSONResponse(status_code=status,
                            content={"detail": str(error), "code": error.code, "params": error.params})

    # As frases da explicação citam só alguns campos: `exclude_unset` mantém de fora os ausentes.
    @app.get("/api/meta", response_model=Meta, responses={**DATA_ERROR, **AS_OF_ERROR})
    def get_meta(as_of: Optional[str] = None) -> Dict[str, Any]:
        current = dataset()
        return views.meta(current, views.context(current, as_of))

    @app.get("/api/sellers", response_model=SellerList, responses=DATA_ERROR)
    def get_sellers() -> Dict[str, Any]:
        return {"sellers": views.sellers(dataset())}

    @app.get("/api/sellers/{seller}/pipeline", response_model=SellerPipeline, response_model_exclude_unset=True,
             responses={**DATA_ERROR, **AS_OF_ERROR, **NOT_FOUND})
    def get_seller_pipeline(seller: str, as_of: Optional[str] = None) -> Dict[str, Any]:
        return views.seller_pipeline(dataset(), seller, as_of)

    @app.get("/api/pipeline", response_model=TeamPipeline, response_model_exclude_unset=True,
             responses={**DATA_ERROR, **AS_OF_ERROR})
    def get_pipeline(manager: Optional[str] = None, office: Optional[str] = None,
                     as_of: Optional[str] = None) -> Dict[str, Any]:
        return views.team_pipeline(dataset(), manager, office, as_of)

    @app.get("/api/rules", response_model=Rules, responses={**DATA_ERROR, **AS_OF_ERROR})
    def get_rules(as_of: Optional[str] = None) -> Dict[str, Any]:
        return views.rules(dataset(), as_of)

    @app.get("/api/intelligence", response_model=Intelligence, responses={**DATA_ERROR, **AS_OF_ERROR})
    def get_intelligence(filters: intelligence.Filters = Depends(intelligence_filters),
                         as_of: Optional[str] = None) -> Dict[str, Any]:
        return intelligence.payload(dataset(), filters, as_of)

    @app.get("/api/intelligence/deals", response_model=IntelligenceDeals, responses={**DATA_ERROR, **PARAMETER_ERROR})
    def get_intelligence_deals(filters: intelligence.Filters = Depends(intelligence_filters),
                               outcome: Optional[str] = None, group: Optional[str] = None,
                               as_of: Optional[str] = None) -> Dict[str, Any]:
        return intelligence.deals(dataset(), filters, outcome, group, as_of)

    # A evidência vem do resultado gravado do backtest: não depende dos CSVs no ar.
    @app.get("/api/evidence", response_model=Evidence, responses=EVIDENCE_ERROR)
    def get_evidence() -> Dict[str, Any]:
        return evidence.load(evidence_path)

    return app


app = create_app()
