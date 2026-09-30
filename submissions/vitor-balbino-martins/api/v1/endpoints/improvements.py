from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from services.improvement_service import ImprovementService

router = APIRouter()

class ImprovementRequest(BaseModel):
    dataset: str = "customer_support_tickets.csv"
    chunk_size: int = Field(default=250, ge=10, le=500)
    hourly_cost: float | None = Field(default=None, ge=0)

@router.post("")
async def improvements(request: ImprovementRequest):
    try: return ImprovementService.generate(request.dataset, request.chunk_size, request.hourly_cost)
    except Exception as exc: raise HTTPException(status_code=503, detail=f"Consolidação indisponível: {exc}") from exc
