"""Prepare the immutable CSV sources without copying customer identity fields."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sqlite3
import statistics
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = Path(os.environ.get("SUPPORT_ARTIFACTS_DIR", str(ROOT / "artifacts" / "v1"))).expanduser().resolve()
SEED = 42
FILES = {"ds1": "customer_support_tickets.csv", "ds2": "all_tickets_processed_improved_v3.csv"}
CATALOG_DB = ARTIFACTS / "catalog.sqlite3"
CATALOG_FIELDS = ("ticket_id", "dataset_id", "source", "text", "subject", "category", "channel", "priority", "status", "product", "csat", "resolution")


def canonical(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text).split())


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


def catalog_fingerprint(records: list[dict]) -> str:
    content = json.dumps(records, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(content.encode()).hexdigest()


def write_catalog(records: list[dict]) -> dict:
    """Cria/atualiza o catálogo sanitizado sem apagar uma versão incompatível."""
    CATALOG_DB.parent.mkdir(parents=True, exist_ok=True)
    digest = catalog_fingerprint(records)
    values = [tuple([index, *[record[field] for field in CATALOG_FIELDS]]) for index, record in enumerate(records)]
    with sqlite3.connect(CATALOG_DB) as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS catalog_tickets (
                row_order INTEGER NOT NULL UNIQUE,
                ticket_id TEXT PRIMARY KEY,
                dataset_id TEXT NOT NULL,
                source TEXT NOT NULL,
                text TEXT NOT NULL,
                subject TEXT,
                category TEXT,
                channel TEXT,
                priority TEXT,
                status TEXT,
                product TEXT,
                csat INTEGER,
                resolution TEXT
            );
            CREATE TABLE IF NOT EXISTS catalog_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_catalog_dataset ON catalog_tickets(dataset_id);
        """)
        existing = db.execute("SELECT value FROM catalog_metadata WHERE key='catalog_sha256'").fetchone()
        if existing and existing[0] != digest:
            raise ValueError("Catálogo SQLite pertence a outra fonte; use uma nova versão de artifacts sem apagar a existente.")
        db.executemany("""
            INSERT INTO catalog_tickets (row_order, ticket_id, dataset_id, source, text, subject, category, channel, priority, status, product, csat, resolution)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(ticket_id) DO UPDATE SET
                row_order=excluded.row_order, dataset_id=excluded.dataset_id, source=excluded.source,
                text=excluded.text, subject=excluded.subject, category=excluded.category,
                channel=excluded.channel, priority=excluded.priority, status=excluded.status,
                product=excluded.product, csat=excluded.csat, resolution=excluded.resolution
        """, values)
        count = db.execute("SELECT COUNT(*) FROM catalog_tickets").fetchone()[0]
        if count != len(records):
            raise ValueError("Catálogo SQLite tem registros de outra versão; use uma nova versão de artifacts sem apagar a existente.")
        db.executemany("""
            INSERT INTO catalog_metadata(key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """, (("catalog_sha256", digest), ("records", str(len(records))), ("schema_version", "1")))
    return {"file": CATALOG_DB.name, "records": len(records), "sha256": digest, "source": "sqlite"}


def load_catalog(path: Path = CATALOG_DB) -> list[dict]:
    """Lê o catálogo canônico em SQLite em uma ordem estável para treino e índice."""
    if not path.exists():
        raise FileNotFoundError(f"Catálogo SQLite ausente: {path}. Execute scripts/prepare_data.py.")
    with sqlite3.connect(path) as db:
        db.row_factory = sqlite3.Row
        rows = [dict(row) for row in db.execute("SELECT " + ", ".join(CATALOG_FIELDS) + " FROM catalog_tickets ORDER BY row_order")]
        metadata = dict(db.execute("SELECT key, value FROM catalog_metadata"))
    if not rows or metadata.get("records") != str(len(rows)) or metadata.get("catalog_sha256") != catalog_fingerprint(rows):
        raise ValueError("Catálogo SQLite incompleto ou incompatível; reconstrua em uma nova versão de artifacts.")
    return rows


def write_predictions(predictions: dict[str, dict]) -> None:
    """Persiste a inferência histórica junto do catálogo, sem limpar versões anteriores."""
    if not CATALOG_DB.exists():
        raise FileNotFoundError(f"Catálogo SQLite ausente: {CATALOG_DB}. Execute scripts/prepare_data.py.")
    values = [(ticket_id, row["predicted_category"], row["confidence"], row["model_version"], row["inference_mode"])
              for ticket_id, row in predictions.items()]
    with sqlite3.connect(CATALOG_DB) as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS catalog_predictions (
                ticket_id TEXT PRIMARY KEY REFERENCES catalog_tickets(ticket_id),
                predicted_category TEXT NOT NULL,
                confidence REAL NOT NULL,
                model_version TEXT NOT NULL,
                inference_mode TEXT NOT NULL
            );
        """)
        db.executemany("""
            INSERT INTO catalog_predictions(ticket_id, predicted_category, confidence, model_version, inference_mode)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(ticket_id) DO UPDATE SET
                predicted_category=excluded.predicted_category, confidence=excluded.confidence,
                model_version=excluded.model_version, inference_mode=excluded.inference_mode
        """, values)
        count = db.execute("SELECT COUNT(*) FROM catalog_predictions").fetchone()[0]
        if count != len(values):
            raise ValueError("Predições SQLite têm registros de outra versão; use uma nova versão de artifacts sem apagar a existente.")
        db.executemany("""
            INSERT INTO catalog_metadata(key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """, (("prediction_records", str(len(values))), ("prediction_model_version", values[0][3] if values else "")))


def sanitize(text: str, known_names: re.Pattern | None = None) -> str:
    text = canonical(text)
    if known_names:
        text = known_names.sub("[nome removido]", text)
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[email removido]", text)
    text = re.sub(r"https?://\S+", "[link removido]", text, flags=re.I)
    text = re.sub(r"(?<!\w)(?:\+?\d[\d ().-]{7,}\d)(?!\w)", "[identificador removido]", text)
    return text


def read_source(dataset_id: str):
    path = ROOT / FILES[dataset_id]
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        rows, columns = list(reader), reader.fieldnames
    if not rows or any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError(f"Fonte inválida: {dataset_id}")
    return rows, {
        "dataset_id": dataset_id, "file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "rows": len(rows), "columns": columns,
        "nulls": {col: sum(not row[col].strip() for row in rows) for col in columns},
    }


def diagnosis(records: list[dict]) -> dict:
    scores = [r["csat"] for r in records if r["csat"] is not None]
    return {
        "dataset_id": "ds1", "source": "historical", "total": len(records),
        "counts": {key: dict(Counter(r[key] for r in records)) for key in ["channel", "priority", "category", "status", "product"]},
        "csat": {"count": len(scores), "coverage": len(scores) / len(records) if records else 0,
                 "mean": statistics.mean(scores) if scores else None,
                 "median": statistics.median(scores) if scores else None,
                 "positive_count": sum(s >= 4 for s in scores),
                 "positive_rate": sum(s >= 4 for s in scores) / len(scores) if scores else None,
                 "distribution": dict(Counter(scores))},
        "temporal": {"frt_available": False, "ttr_available": False,
                     "reason": "A fonte não contém abertura do ticket; campos temporais são timestamps com inconsistências."},
    }


def main() -> None:
    ds1, meta1 = read_source("ds1")
    ds2, meta2 = read_source("ds2")
    names = sorted({r["Customer Name"] for r in ds1}, key=len, reverse=True)
    # Match complete known names; do not mistake individual first names for entities.
    name_pattern = re.compile(r"(?<!\w)(?:" + "|".join(re.escape(n) for n in names if n) + r")(?!\w)", re.I)
    catalog = []
    for row in ds1:
        catalog.append({
            "ticket_id": f"ds1:{row['Ticket ID']}", "dataset_id": "ds1", "source": "historical",
            "text": sanitize(row["Ticket Description"], name_pattern), "subject": sanitize(row["Ticket Subject"], name_pattern),
            "category": row["Ticket Type"], "channel": row["Ticket Channel"], "priority": row["Ticket Priority"],
            "status": row["Ticket Status"], "product": row["Product Purchased"],
            "csat": int(float(row["Customer Satisfaction Rating"])) if row["Customer Satisfaction Rating"] else None,
            "resolution": sanitize(row["Resolution"], name_pattern) or None,
        })
    for row in ds2:
        ticket_id = "ds2:" + hashlib.sha256(canonical(row["Document"]).encode()).hexdigest()
        catalog.append({
            "ticket_id": ticket_id, "dataset_id": "ds2", "source": "historical",
            "text": sanitize(row["Document"]), "subject": None,
            "category": row["Topic_group"], "channel": None, "priority": None, "status": None,
            "product": None, "csat": None, "resolution": None,
        })
    if len({r["ticket_id"] for r in catalog}) != len(catalog):
        raise ValueError("Colisão de identidade na fonte: revisar antes de indexar")
    parse = lambda value: datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    pairs = [r for r in ds1 if r["First Response Time"] and r["Time to Resolution"]]
    invalid_pairs = sum(parse(r["Time to Resolution"]) < parse(r["First Response Time"]) for r in pairs)
    quality = {
        "sources": [meta1, meta2], "timestamp_pairs": len(pairs), "invalid_timestamp_order": invalid_pairs,
        "frt_available": False, "ttr_available": False, "effort_available": False,
        "description_placeholders": sum(bool(re.search(r"\{[^{}]+\}", r["Ticket Description"])) for r in ds1),
        "ds1_exact_text_unique": len({r["Ticket Description"] for r in ds1}),
        "ds1_canonical_text_unique": len({canonical(r["Ticket Description"]) for r in ds1}),
        "pii_policy": "Nome completo conhecido, emails, URLs e identificadores numéricos longos mascarados. Campos pessoais não copiados.",
        "pii_limitations": "Redação baseada em padrões não garante detectar nomes desconhecidos ou toda informação sensível em texto livre; uso local e revisão antes de compartilhamento.",
    }
    summary = diagnosis([r for r in catalog if r["dataset_id"] == "ds1"])
    summary["temporal"].update({"pairs": len(pairs), "invalid_pairs": invalid_pairs})
    manifest_path = ARTIFACTS / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    manifest.update({"artifact_version": "v1", "created_at": datetime.now(timezone.utc).isoformat(),
                     "sources": [meta1, meta2], "seed": SEED,
                     "id_normalization": "Unicode NFC, trim, whitespace collapsed; case preserved; sha256 UTF-8 for ds2",
                     "data_preparation_version": "prepare-v1"})
    manifest["catalog"] = write_catalog(catalog)
    for name, value in [("quality.json", quality), ("diagnosis.json", summary), ("manifest.json", manifest)]:
        write_json(ARTIFACTS / name, value)
    print(json.dumps({"catalog_records": len(catalog), "catalog_database": str(CATALOG_DB), "invalid_timestamp_order": invalid_pairs, "artifacts": str(ARTIFACTS)}))


if __name__ == "__main__":
    main()
