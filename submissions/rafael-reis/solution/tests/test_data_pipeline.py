"""Run with .venv/bin/python tests/test_data_pipeline.py after artifact generation."""
import json
import hashlib
import re
import sys
from pathlib import Path

import numpy as np
import faiss
import joblib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from prepare_data import ARTIFACTS, CATALOG_DB, canonical, load_catalog, sanitize


def main():
    assert canonical("  cafe\u0301\n x ") == "café x"
    assert "example.com" not in sanitize("email sample@example.com https://example.com")
    assert CATALOG_DB.exists()
    catalog = load_catalog()
    assert len(catalog) == 56306 and len({r["ticket_id"] for r in catalog}) == 56306
    assert not any("Customer Name" in r or "Customer Email" in r for r in catalog)
    assert not any(re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", r["text"]) for r in catalog)
    import sqlite3
    with sqlite3.connect(CATALOG_DB) as db:
        prediction_count = db.execute("SELECT COUNT(*) FROM catalog_predictions").fetchone()[0]
    assert prediction_count == 47837
    quality = json.loads((ARTIFACTS / "quality.json").read_text())
    for source in quality["sources"]:
        assert hashlib.sha256((ROOT / source["file"]).read_bytes()).hexdigest() == source["sha256"]
    assert quality["timestamp_pairs"] == 2769 and quality["invalid_timestamp_order"] == 1365
    assert quality["ttr_available"] is False and quality["frt_available"] is False
    diagnosis = json.loads((ARTIFACTS / "diagnosis.json").read_text())
    assert diagnosis["csat"]["count"] == 2769 and diagnosis["csat"]["positive_count"] == 1087
    metrics = json.loads((ARTIFACTS / "model_metrics.json").read_text())
    assert 0 <= metrics["accuracy"] <= 1 and len(metrics["classes"]) == 8
    classifier = joblib.load(ARTIFACTS / "classifier.joblib")
    probabilities = classifier["pipeline"].predict_proba(["I changed my password and cannot access my account."])
    assert probabilities.shape == (1, 8) and np.isfinite(probabilities).all()
    assert np.allclose(probabilities.sum(axis=1), 1) and classifier["model_version"] == metrics["model_version"]
    split = json.loads((ARTIFACTS / "split_ids.json").read_text())
    subsets = [set(split[key]) for key in ["train", "validation", "test"]]
    assert sum(map(len, subsets)) == 47837 and not (subsets[0] & subsets[1] or subsets[0] & subsets[2] or subsets[1] & subsets[2])
    lookup = {r["ticket_id"]: canonical(r["text"]).casefold() for r in catalog}
    group_sets = [{lookup[ticket] for ticket in subset} for subset in subsets]
    assert not (group_sets[0] & group_sets[1] or group_sets[0] & group_sets[2] or group_sets[1] & group_sets[2])
    for dataset, count in [("ds1", 8469), ("ds2", 47837)]:
        path = ARTIFACTS / dataset
        semantic = json.loads((path / "semantic.json").read_text())
        for name, digest in semantic["checksums"].items():
            assert hashlib.sha256((path / name).read_bytes()).hexdigest() == digest
        embeddings = np.load(path / "embeddings.npy", allow_pickle=False)
        assert embeddings.shape == (count, 384)
        assert np.allclose(np.linalg.norm(embeddings, axis=1), 1, atol=1e-4)
        coords = np.load(path / "coordinates.npy", allow_pickle=False)
        assert coords.shape == (count, 2) and np.isfinite(coords).all()
        assert len(np.load(path / "clusters.npy", allow_pickle=False)) == count
        index = faiss.read_index(str(path / "index.faiss"))
        assert index.ntotal == count and index.d == 384
        similarities, _ = index.search(embeddings[[0, count // 2, count - 1]], 1)
        assert np.allclose(similarities, 1, atol=1e-4)
        assert sum(cluster["size"] for cluster in semantic["clusters"]) == count
        assert len(set(json.loads((path / "map_ids.json").read_text()))) == count
        neighbors = json.loads((path / "neighbors.json").read_text())
        assert all(all(n["ticket_id"] != ticket for n in nearest) for ticket, nearest in neighbors.items())
    print("OK: source/artifact hashes, privacy patterns, metrics, classifier, split leakage, embeddings, FAISS, geometry and neighbors")


if __name__ == "__main__":
    main()
