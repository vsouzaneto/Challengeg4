from fastapi import APIRouter, HTTPException

from services.cross_dataset_service import CrossDatasetService

router = APIRouter()


@router.post("/satisfaction")
async def satisfaction_analysis():
    try:
        return CrossDatasetService.analyze_satisfaction()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Cruzamento indisponível: {exc}") from exc
