"""Seller feedback loop: what happened after the recommendation. Persisted for the pipeline."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Response, status

from api.feedback_store import append_record, build_record, read_records
from api.repository import repository
from api.routers._common import ERR_404_DEAL, ERR_422, ERR_503, AsOfQuery, load_snapshot
from api.schemas import FeedbackCreate, FeedbackRecord
from api.settings import settings

log = logging.getLogger("api.feedback")
router = APIRouter(tags=["feedback"])


@router.post(
    "/feedback",
    response_model=FeedbackRecord,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_feedback",
    summary="Registra a ação do vendedor sobre um deal",
    description=(
        "Grava em `data/feedback/actions.parquet` (append atômico) o que o vendedor fez depois "
        "de ver a recomendação. O deal precisa existir na partição `as_of` (padrão: a mais "
        "recente); o registro guarda o `priority_score` e a `model_version` exibidos naquele "
        "momento para permitir avaliar o scorer contra o comportamento real depois.\n\n"
        "`recorded_at` é o único carimbo de relógio real do sistema: é auditoria, nunca feature."
    ),
    responses={
        201: {"description": "Ação registrada."},
        404: ERR_404_DEAL,
        422: ERR_422,
        503: ERR_503,
    },
)
def create_feedback(
    payload: FeedbackCreate, response: Response, as_of: AsOfQuery = None
) -> FeedbackRecord:
    snap = load_snapshot(as_of, response)
    deal = snap.get(payload.opportunity_id)
    record = build_record(payload, deal)
    rows = append_record(settings.feedback_file, record)
    log.info(
        "feedback_saved id=%s opportunity_id=%s action=%s rows=%d",
        record.id,
        record.opportunity_id,
        record.action.value,
        rows,
    )
    return record


@router.get(
    "/feedback",
    response_model=list[FeedbackRecord],
    operation_id="list_feedback",
    summary="Ações registradas",
    description=(
        "Lista o conteúdo de `actions.parquet`, mais recente primeiro. Filtro opcional por "
        "`opportunity_id`. Vazio (200) quando ninguém registrou nada ainda."
    ),
    responses={422: ERR_422},
)
def list_feedback(opportunity_id: str | None = None) -> list[FeedbackRecord]:
    records = read_records(settings.feedback_file)
    if opportunity_id is not None:
        records = [r for r in records if r.opportunity_id == opportunity_id]
    return sorted(records, key=lambda r: r.recorded_at, reverse=True)


__all__ = ["repository", "router"]
