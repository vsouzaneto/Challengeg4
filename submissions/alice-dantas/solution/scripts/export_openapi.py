"""Grava o contrato da API em web/contract/openapi.json.

O front gera tipos e validação a partir deste arquivo, sem precisar da API no ar.
`tests/test_contract.py` falha se ele ficar diferente do schema gerado pela API.

Rodar (em solution/): `.venv/bin/python scripts/export_openapi.py`
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

SOLUTION_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOLUTION_DIR))

from api.main import create_app  # noqa: E402

CONTRACT_PATH = SOLUTION_DIR / "web" / "contract" / "openapi.json"


def schema() -> Dict[str, Any]:
    return create_app().openapi()


def render(document: Dict[str, Any]) -> str:
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    CONTRACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONTRACT_PATH.write_text(render(schema()), encoding="utf-8")
    print(f"Gravado em {CONTRACT_PATH.relative_to(SOLUTION_DIR)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
