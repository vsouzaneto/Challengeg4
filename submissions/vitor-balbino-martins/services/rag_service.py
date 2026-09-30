import csv
import logging
from pathlib import Path
from threading import Lock
from core.config import settings
from repositories.rag_repository import RagRepository
from langchain_core.documents import Document


logger = logging.getLogger(__name__)

class RagService:
    _status = {"status": "idle", "processed": 0, "total": 0, "error": None}
    _lock = Lock()

    @classmethod
    def status(cls): return dict(cls._status)

    @classmethod
    def index_assets(cls):
        with cls._lock:
            if cls._status["status"] == "running": return
            cls._status = {"status": "running", "processed": 0, "total": 0, "error": None}
        try:
            assets = Path(__file__).resolve().parents[1] / settings.RAG_ASSETS_DIR
            documents = []
            for path in sorted(assets.glob("*.csv")):
                with path.open("r", encoding="utf-8-sig", newline="") as file:
                    for row in csv.DictReader(file):
                        content = "\n".join(f"{key}: {value}" for key, value in row.items() if value)
                        documents.append(Document(page_content=content, metadata={"source": path.name, "ticket_id": row.get("Ticket ID")}))
            cls._status["total"] = len(documents)
            RagRepository().add_documents(documents)
            cls._status.update(status="completed", processed=len(documents))
        except Exception as exc:
            logger.exception("RAG indexing failed")
            cls._status.update(status="failed", error=str(exc))

    @staticmethod
    def search(query, k): return RagRepository().similarity_search_with_score(query, k)
