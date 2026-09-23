"""Caminhos e utilidades compartilhadas pelo pipeline."""
import json
import os
import sys
from pathlib import Path

import numpy as np

# O console do Windows usa cp1252 por padrão e quebra com acentos/símbolos nos prints.
sys.stdout.reconfigure(encoding="utf-8")

SUBMISSION = Path(__file__).resolve().parents[2]
REPO_ROOT = SUBMISSION.parents[1]
DATASETS = Path(os.environ.get("DATASETS_DIR", REPO_ROOT / "datasets"))
APP_DATA = SUBMISSION / "solution" / "app" / "data"

TICKETS_CSV = DATASETS / "customer_support_tickets.csv"  # Dataset 1 (métricas operacionais)
IT_TICKETS_CSV = DATASETS / "all_tickets_processed_improved_v3.csv"  # Dataset 2 (texto classificado)

SEED = 42


def _to_builtin(obj):
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return None if np.isnan(obj) else round(float(obj), 6)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    raise TypeError(f"não serializável: {type(obj)}")


def save_json(name: str, obj) -> Path:
    """Grava um JSON consumido pelo web app em solution/app/data/."""
    APP_DATA.mkdir(parents=True, exist_ok=True)
    path = APP_DATA / name
    path.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":"), default=_to_builtin), encoding="utf-8")
    print(f"-> {path.relative_to(SUBMISSION)} ({path.stat().st_size / 1024:.0f} KB)")
    return path


def load_env():
    """Lê o .env da raiz do repositório (GEMINI_API_KEY etc.) sem sobrescrever variáveis já definidas."""
    env = REPO_ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
