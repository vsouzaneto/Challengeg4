from fastapi import APIRouter, BackgroundTasks, HTTPException
from schemas.rag import RagIndexResponse, RagQuery, RagSearchResult
from services.rag_service import RagService

router = APIRouter()

@router.post("/index", response_model=RagIndexResponse, status_code=202)
async def start_indexing(background_tasks: BackgroundTasks):
    if RagService.status()["status"] == "running": return {"status": "running", "message": "Indexação já está em andamento."}
    background_tasks.add_task(RagService.index_assets)
    return {"status": "queued", "message": "Indexação dos CSVs enfileirada."}

@router.get("/index/status")
async def indexing_status(): return RagService.status()

@router.post("/search", response_model=list[RagSearchResult])
async def search(query: RagQuery):
    try: results = RagService.search(query.query, query.k)
    except Exception as exc: raise HTTPException(status_code=503, detail=f"RAG indisponível: {exc}") from exc
    return [{"content": doc.page_content, "metadata": doc.metadata, "score": score} for doc, score in results]
