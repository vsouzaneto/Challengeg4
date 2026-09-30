from core.config import settings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres.vectorstores import PGVector
import torch


class RagRepository:
    def _store(self):
        
        device = settings.RAG_DEVICE.lower()
        if device == "cuda":
            try:
                if not torch.cuda.is_available(): device = "cpu"
            except ImportError: device = "cpu"
        embeddings = HuggingFaceEmbeddings(model_name=settings.RAG_MODEL_NAME, model_kwargs={"device": device}, encode_kwargs={"normalize_embeddings": True})
        connection = settings.RAG_SYNC_DATABASE_URL or settings.DATABASE_URL.replace("+asyncpg", "")
        return PGVector(embeddings=embeddings, collection_name=settings.RAG_COLLECTION_NAME, connection=connection, use_jsonb=True)

    def add_documents(self, documents): return self._store().add_documents(documents)
    def similarity_search_with_score(self, query, k): return self._store().similarity_search_with_score(query, k=k)
