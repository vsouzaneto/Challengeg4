"""API read-only opcional sobre o bundle (localhost). Não expor na Internet sem auth."""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException

ROOT = Path(__file__).resolve().parent
BUNDLE_PATH = ROOT / "outputs" / "dashboard_bundle.json"
if not BUNDLE_PATH.exists():
    BUNDLE_PATH = ROOT / "command-center" / "public" / "data" / "bundle.json"

app = FastAPI(title="RavenStack Intelligence API", version="1.0")
_bundle: dict | None = None


def _load() -> dict:
    global _bundle
    if _bundle is None:
        _bundle = json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))
    return _bundle


@app.get("/health")
def health() -> dict:
    return {"ok": True, "bundle": BUNDLE_PATH.name}


@app.get("/kpis")
def kpis() -> dict:
    b = _load()
    return b.get("kpis_globais", {})


@app.get("/account/{account_id}")
def account(account_id: str) -> dict:
    b = _load()
    inv = b.get("investigacoes", {}).get(account_id)
    conta = next((c for c in b.get("contas", []) if c.get("conta_id") == account_id), None)
    if not conta and not inv:
        raise HTTPException(status_code=404, detail="conta não encontrada")
    return {"conta": conta, "investigacao": inv}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8766)
