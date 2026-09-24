from fastapi import APIRouter

from api import __version__
from api.schemas import HealthResponse

router = APIRouter(tags=["operacao"])


@router.get(
    "/health",
    response_model=HealthResponse,
    operation_id="get_health",
    summary="Verifica se a API está de pé",
    description="Usado pelo `HEALTHCHECK` do Docker e pelo frontend ao abrir. Não toca em disco.",
)
def get_health() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__)
