from fastapi import APIRouter
from api.v1.endpoints.health import router as health_router
from api.v1.endpoints.rag import router as rag_router
from api.v1.endpoints.reports import router as reports_router
from api.v1.endpoints.clustering import router as clustering_router
from api.v1.endpoints.satisfaction import router as satisfaction_router
from api.v1.endpoints.dashboard import router as dashboard_router
from api.v1.endpoints.improvements import router as improvements_router

router = APIRouter()
router.include_router(health_router, prefix="/health", tags=["health"])
router.include_router(rag_router, prefix="/rag", tags=["rag"])
router.include_router(reports_router, prefix="/reports", tags=["reports"])
router.include_router(clustering_router, prefix="/clustering", tags=["clustering"])
router.include_router(satisfaction_router, prefix="/reports", tags=["reports"])
router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
router.include_router(improvements_router, prefix="/reports/improvements", tags=["improvements"])
