from fastapi import APIRouter, HTTPException

from schemas.clustering import ClusteringRequest, ClusteringResponse
from services.clustering_service import TicketClusteringService

router = APIRouter()


@router.post("", response_model=ClusteringResponse)
async def cluster_tickets(request: ClusteringRequest):
    try:
        return TicketClusteringService.cluster(request.dataset, request.clusters, request.batch_size, request.representatives)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Clustering indisponível: {exc}") from exc
