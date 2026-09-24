"""Discovery endpoint: which ``as_of`` partitions and which model are available."""

from __future__ import annotations

import logging

from fastapi import APIRouter

from api.errors import ApiError
from api.repository import list_as_of_partitions, read_model_version, repository
from api.schemas import SCHEMA_VERSION, MetaResponse
from api.settings import settings

__all__ = ["list_as_of_partitions", "read_model_version", "router"]

log = logging.getLogger("api.meta")
router = APIRouter(tags=["meta"])


@router.get(
    "/meta",
    response_model=MetaResponse,
    operation_id="get_meta",
    summary="Snapshots e modelo disponíveis",
    description=(
        "Lista as partições `as_of=` presentes em `data/gold/scores`, a versão em "
        "`models/latest` e a contagem de deals abertos da partição padrão. Quando "
        "`artifacts_present` é falso, a UI orienta a rodar o pipeline em vez de falhar. "
        "Nunca retorna 503: é o endpoint que a UI usa para decidir o que mostrar."
    ),
)
def get_meta() -> MetaResponse:
    partitions = list_as_of_partitions(settings.scores_dir)
    open_deals: int | None = None
    if partitions:
        try:
            open_deals = len(repository.snapshot(partitions[-1]).deals)
        except ApiError as exc:  # invalid parquet: /meta still answers, /deals will 503
            log.warning("meta_snapshot_unavailable code=%s message=%s", exc.code, exc.message)
    return MetaResponse(
        schema_version=SCHEMA_VERSION,
        as_of_available=partitions,
        default_as_of=partitions[-1] if partitions else None,
        model_version=read_model_version(settings.latest_model_pointer),
        artifacts_present=bool(partitions),
        open_deals=open_deals,
    )
