import csv
from collections import Counter, defaultdict
from pathlib import Path

from core.config import settings


class TicketClusteringService:
    @staticmethod
    def _load(dataset):
        path = Path(__file__).resolve().parents[1] / settings.RAG_ASSETS_DIR / dataset
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            return list(csv.DictReader(file))

    @staticmethod
    def _text(row):
        fields = ("Ticket Subject", "Ticket Description", "Resolution", "Ticket Type", "Product Purchased")
        return " ".join(f"{field}: {row.get(field, '')}" for field in fields if row.get(field))

    @classmethod
    def cluster(cls, dataset, n_clusters, batch_size, representatives):
        rows = cls._load(dataset)
        if len(rows) < n_clusters:
            raise ValueError("A quantidade de clusters não pode exceder o número de registros")
        from langchain_huggingface import HuggingFaceEmbeddings
        from sklearn.cluster import MiniBatchKMeans
        import numpy as np

        device = settings.RAG_DEVICE.lower()
        if device == "cuda":
            try:
                import torch
                if not torch.cuda.is_available(): device = "cpu"
            except ImportError: device = "cpu"
        embeddings = HuggingFaceEmbeddings(model_name=settings.RAG_MODEL_NAME, model_kwargs={"device": device}, encode_kwargs={"normalize_embeddings": True})
        texts = [cls._text(row) for row in rows]
        vectors = embeddings.embed_documents(texts)
        model = MiniBatchKMeans(n_clusters=n_clusters, batch_size=batch_size, random_state=42, n_init="auto")
        labels = model.fit_predict(np.asarray(vectors))
        groups = defaultdict(list)
        for index, label in enumerate(labels): groups[int(label)].append(index)
        result = []
        for label, indexes in sorted(groups.items()):
            center = model.cluster_centers_[label]
            ranked = sorted(indexes, key=lambda i: float(np.linalg.norm(np.asarray(vectors[i]) - center)))
            sample = []
            for i in ranked[:representatives]:
                row = rows[i]
                sample.append({"ticket_id": row.get("Ticket ID"), "subject": row.get("Ticket Subject"), "source_index": i + 2})
            result.append({
                "cluster": label, "size": len(indexes),
                "channels": dict(Counter(rows[i].get("Ticket Channel") or "unknown" for i in indexes)),
                "priorities": dict(Counter(rows[i].get("Ticket Priority") or "unknown" for i in indexes)),
                "ticket_types": dict(Counter(rows[i].get("Ticket Type") or "unknown" for i in indexes)),
                "representatives": sample,
            })
        return {"dataset": dataset, "total_records": len(rows), "clusters": n_clusters, "model": settings.RAG_MODEL_NAME, "groups": result}
