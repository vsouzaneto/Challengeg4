"""Build actual multilingual encoder embeddings, exact search and semantic geometry."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("HF_HOME", str(ROOT / ".cache" / "huggingface"))
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
os.environ.setdefault("NUMBA_NUM_THREADS", "4")

import faiss
import hdbscan
import joblib
import numpy as np
import torch
import umap
from huggingface_hub import model_info, snapshot_download
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer

from prepare_data import ARTIFACTS, SEED, load_catalog, write_json

ENCODER = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def embed(model: SentenceTransformer, records: list[dict], out: Path, revision: str) -> np.ndarray:
    batches = out / "embedding_batches"
    batches.mkdir(parents=True, exist_ok=True)
    identity = hashlib.sha256(json.dumps([(r["ticket_id"], r["text"]) for r in records], ensure_ascii=False).encode()).hexdigest()
    expected = {"corpus_sha256": identity, "encoder_revision": revision, "batch_records": 512, "normalize_embeddings": True}
    resume_path = batches / "manifest.json"
    if resume_path.exists() and json.loads(resume_path.read_text()) != expected:
        raise ValueError(f"Cache incompatível em {batches}; selecione nova artifact_version, sem sobrescrever embeddings de outra fonte.")
    write_json(resume_path, expected)
    parts = []
    for start in range(0, len(records), 512):
        path = batches / f"{start:06d}.npy"
        count = min(512, len(records) - start)
        if path.exists():
            batch = np.load(path, allow_pickle=False)
            if batch.shape != (count, model.get_sentence_embedding_dimension()):
                raise ValueError(f"Batch incompleto em {path}")
        else:
            batch = model.encode([r["text"] for r in records[start:start+512]], batch_size=64,
                                 normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False).astype("float32")
            np.save(path, batch, allow_pickle=False)
        if not np.isfinite(batch).all():
            raise ValueError("Embedding com valores não finitos")
        parts.append(batch)
        if start % 2048 == 0 or start + 512 >= len(records):
            print(json.dumps({"dataset": out.name, "embedded": start + count, "total": len(records)}), flush=True)
    return np.ascontiguousarray(np.concatenate(parts), dtype="float32")


def build_dataset(dataset_id: str, model: SentenceTransformer, revision: str, model_path: str, catalog: list[dict]) -> None:
    started = time.perf_counter()
    records = [r for r in catalog if r["dataset_id"] == dataset_id]
    out = ARTIFACTS / dataset_id
    out.mkdir(parents=True, exist_ok=True)
    ids = [r["ticket_id"] for r in records]
    embeddings = embed(model, records, out, revision)
    np.save(out / "embeddings.npy", embeddings, allow_pickle=False)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, str(out / "index.faiss"))
    write_json(out / "map_ids.json", ids)
    print(json.dumps({"dataset": dataset_id, "step": "clustering"}), flush=True)
    # PCA keeps clustering separate from the two-dimensional display projection.
    reducer = PCA(n_components=32, random_state=SEED)
    reduced = reducer.fit_transform(embeddings)
    clusterer = hdbscan.HDBSCAN(min_cluster_size=35 if dataset_id == "ds1" else 80, min_samples=8,
                               metric="euclidean", prediction_data=True, core_dist_n_jobs=4)
    labels = clusterer.fit_predict(reduced)
    np.save(out / "clusters.npy", labels.astype("int32"), allow_pickle=False)
    np.save(out / "cluster_probabilities.npy", clusterer.probabilities_.astype("float32"), allow_pickle=False)
    joblib.dump({"pca": reducer, "clusterer": clusterer}, out / "clusterer.joblib")
    print(json.dumps({"dataset": dataset_id, "step": "umap", "clusters": len(set(labels) - {-1})}), flush=True)
    projector = umap.UMAP(n_components=2, n_neighbors=20, min_dist=.2, metric="cosine", random_state=SEED,
                          transform_seed=SEED, n_epochs=120, low_memory=True, n_jobs=1)
    coordinates = projector.fit_transform(embeddings).astype("float32")
    if not np.isfinite(coordinates).all():
        raise ValueError("Projeção com valores não finitos")
    np.save(out / "coordinates.npy", coordinates, allow_pickle=False)
    joblib.dump(projector, out / "projector.joblib")
    word_model = TfidfVectorizer(max_features=12000, min_df=3, stop_words="english", token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z]{2,}\b")
    words = word_model.fit_transform([r["text"] for r in records])
    vocabulary = word_model.get_feature_names_out()
    cluster_summaries = []
    for label in sorted(set(labels)):
        members = np.flatnonzero(labels == label)
        center = embeddings[members].mean(axis=0)
        center /= max(np.linalg.norm(center), 1e-12)
        ranked = members[np.argsort(-(embeddings[members] @ center))]
        mean_words = np.asarray(words[members].mean(axis=0)).ravel()
        terms = vocabulary[np.argsort(-mean_words)[:5]].tolist()
        categories = Counter(records[i]["category"] for i in members)
        scores = [records[i]["csat"] for i in members if records[i]["csat"] is not None]
        cluster_summaries.append({
            "cluster_id": int(label), "space_id": f"{dataset_id}-semantic-v1", "size": len(members),
            "label": "Sem cluster estável" if label == -1 else " · ".join(terms[:3]),
            "terms": terms, "dominant_category": categories.most_common(1)[0][0], "categories": dict(categories),
            "centroid": coordinates[members].mean(axis=0).tolist(), "cohesion": float((embeddings[members] @ center).mean()),
            "representative_ids": [ids[i] for i in ranked[:5]], "is_noise": int(label) == -1,
            "csat_mean": float(np.mean(scores)) if scores else None, "csat_count": len(scores),
        })
    scores, neighbors = index.search(embeddings, 7)
    # Exclude same row. These are corpus neighbors; replay also excludes its own historical source.
    neighbor_map = {ids[i]: [{"ticket_id": ids[int(j)], "similarity": float(score)} for j, score in zip(js, ss) if j >= 0 and int(j) != i][:6] for i, (js, ss) in enumerate(zip(neighbors, scores))}
    write_json(out / "neighbors.json", neighbor_map)
    metadata = {
        "space_id": f"{dataset_id}-semantic-v1", "dataset_id": dataset_id, "artifact_version": "v1",
        "encoder_name": ENCODER, "encoder_revision": revision,
        "dimension": embeddings.shape[1], "count": len(records), "normalized": True,
        "similarity": "cosine via normalized embeddings and FAISS IndexFlatIP",
        "projection": {"method": "UMAP", "file": "projector.joblib", "n_neighbors": 20, "min_dist": .2, "n_epochs": 120, "seed": SEED,
                       "limitation": "Distância no plano 2D não equivale à similaridade semântica."},
        "clustering": {"method": "PCA 32 + HDBSCAN", "min_cluster_size": clusterer.min_cluster_size, "min_samples": 8,
                       "noise_count": int((labels == -1).sum()), "clusters_count": len(set(labels) - {-1}),
                       "pca_explained_variance": float(reducer.explained_variance_ratio_.sum()), "assignment": "HDBSCAN approximate_predict in PCA space"},
        "clusters": cluster_summaries, "build_seconds": time.perf_counter() - started,
        "limitations": ["Clusters são agrupamentos exploratórios, não incidentes confirmados.", "Hierarquia disponível: clusters e tickets; subclusters não foram inventados.", "Encoder multilíngue; relevância e precisão de duplicatas exigem avaliação humana."],
    }
    for name in ["embeddings.npy", "index.faiss", "coordinates.npy", "clusters.npy", "map_ids.json"]:
        metadata.setdefault("checksums", {})[name] = hashlib.sha256((out / name).read_bytes()).hexdigest()
    write_json(out / "semantic.json", metadata)
    print(json.dumps({"dataset": dataset_id, "ready": True, "clusters": metadata["clustering"]["clusters_count"], "seconds": metadata["build_seconds"]}), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["ds1", "ds2", "all"], default="all")
    args = parser.parse_args()
    torch.set_num_threads(4)
    manifest_path = ARTIFACTS / "encoder.json"
    if manifest_path.exists():
        encoder = json.loads(manifest_path.read_text())
        revision = encoder["revision"]
    else:
        revision = model_info(ENCODER).sha
    path = snapshot_download(ENCODER, revision=revision,
                             allow_patterns=["*.json", "*.safetensors", "*.txt", "*.model", "1_Pooling/*", "2_Dense/*"],
                             ignore_patterns=["onnx/*", "openvino/*", "*.h5"])
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model = SentenceTransformer(path, device=device, local_files_only=True)
    write_json(manifest_path, {"name": ENCODER, "revision": revision, "path": path, "device_used": device,
                              "max_sequence_length": model.max_seq_length, "dimension": model.get_sentence_embedding_dimension(),
                              "versions": {package: importlib.metadata.version(package) for package in ["sentence-transformers", "torch", "faiss-cpu", "umap-learn", "hdbscan"]}})
    catalog = load_catalog()
    for dataset_id in (["ds1", "ds2"] if args.dataset == "all" else [args.dataset]):
        build_dataset(dataset_id, model, revision, path, catalog)
    manifest = json.loads((ARTIFACTS / "manifest.json").read_text())
    manifest["semantic_spaces"] = {dataset: f"{dataset}/semantic.json" for dataset in ["ds1", "ds2"] if (ARTIFACTS / dataset / "semantic.json").exists()}
    manifest["encoder"] = json.loads(manifest_path.read_text())
    write_json(ARTIFACTS / "manifest.json", manifest)


if __name__ == "__main__":
    main()
