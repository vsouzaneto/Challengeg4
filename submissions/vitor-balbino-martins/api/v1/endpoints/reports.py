from fastapi import APIRouter, HTTPException
from schemas.report import ReportRequest, ReportResponse
from services.report_service import SupportReportService

router = APIRouter()


@router.post("/support", response_model=ReportResponse)
async def support_report(request: ReportRequest):
    try:
        return SupportReportService.generate(request.dataset, request.chunk_size, request.hourly_cost)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Relatório indisponível: {exc}") from exc
