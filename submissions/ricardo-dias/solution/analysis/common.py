"""Caminhos e carregamento compartilhados pelos scripts de análise."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

# Console do Windows usa cp1252 por padrão; os relatórios têm acentos e setas.
sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
# CSVs brutos ficam fora do repo; sobrescreva com DATA_DIR se estiverem em outro lugar.
DATA_DIR = Path(os.environ.get("DATA_DIR", HERE.parents[4] / "data" / "raw"))
APP_DATA = HERE.parent / "app" / "data"
SEED = 42

D1_FILE = "customer_support_tickets.csv"
D2_FILE = "all_tickets_processed_improved_v3.csv"


def load_d1() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / D1_FILE)


def load_d2() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / D2_FILE)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _default(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return None if np.isnan(o) else float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(f"não serializável: {type(o)}")


def write_json(name: str, payload, *, generated: bool = True, compact: bool = False) -> Path:
    """Grava em app/data. `generatedAt` fica fora do diff determinístico só quando pedido."""
    APP_DATA.mkdir(parents=True, exist_ok=True)
    path = APP_DATA / name
    if generated and isinstance(payload, dict):
        payload = {"generatedAt": now_iso(), **payload}
    dump = dict(separators=(",", ":")) if compact else dict(indent=2)
    path.write_text(json.dumps(payload, ensure_ascii=False, default=_default, **dump), encoding="utf-8")
    print(f"→ {path.relative_to(HERE.parents[1])}")
    return path


def r(x: float, n: int = 4) -> float:
    return float(round(float(x), n))
