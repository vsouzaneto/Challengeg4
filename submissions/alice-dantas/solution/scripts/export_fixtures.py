"""Grava respostas da API, com dados sintéticos, em web/tests/fixtures/.

O front testa tipos, textos e tela contra estas respostas sem precisar da API no ar
nem dos CSVs reais. Os dados vêm das fixtures dos testes do núcleo
(`tests/conftest.py`) e cobrem todos os códigos do contrato.
`tests/test_contract.py` falha se elas ficarem diferentes do que a API devolve.

Rodar (em solution/): `.venv/bin/python scripts/export_fixtures.py`
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict
from urllib.parse import quote

SOLUTION_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOLUTION_DIR))
sys.path.insert(0, str(SOLUTION_DIR / "tests"))

from fastapi.testclient import TestClient  # noqa: E402

from api.main import create_app  # noqa: E402
from conftest import EDGE_TABLES, INTEL_TABLES, write_evidence, write_raw  # noqa: E402
from leadscorer import policy  # noqa: E402

FIXTURES_DIR = SOLUTION_DIR / "web" / "tests" / "fixtures"
MISSING_DATA_DIR = SOLUTION_DIR / "tests" / "missing-data"  # não existe: gera o 503


def pipeline(seller: str) -> str:
    return f"/api/sellers/{quote(seller)}/pipeline"


def body(client: TestClient, url: str, status: int = 200) -> Any:
    response = client.get(url)
    assert response.status_code == status, (url, response.status_code, response.text)
    return response.json()


def fixtures() -> Dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmp:
        evidence = write_evidence(Path(tmp) / "processed" / "backtest_results.json")
        base = TestClient(create_app(write_raw(Path(tmp) / "base"), evidence))
        edges = TestClient(create_app(write_raw(Path(tmp) / "edges", **EDGE_TABLES)))
        intel = TestClient(create_app(write_raw(Path(tmp) / "intel", **INTEL_TABLES)))
        return {
            "sellers": body(base, "/api/sellers"),
            "meta": body(base, "/api/meta"),
            "pipeline-ana-alfa": body(base, pipeline("Ana Alfa")),
            "pipeline-bruno-beta": body(base, pipeline("Bruno Beta")),
            "pipeline-carla-gama": body(base, pipeline("Carla Gama")),
            "pipeline-edges-ana-alfa": body(edges, pipeline("Ana Alfa")),
            "pipeline-edges-bruno-beta": body(edges, pipeline("Bruno Beta")),
            # Focar vazio: um começa por Acompanhar, o outro por Revisar.
            "pipeline-edges-davi-delta": body(edges, pipeline("Davi Delta")),
            "pipeline-edges-eva-epsilon": body(edges, pipeline("Eva Epsilon")),
            "team-all": body(base, "/api/pipeline"),
            "team-empty": body(base, "/api/pipeline?manager=Ninguem"),
            "team-east": body(base, "/api/pipeline?office=East"),
            "rules": body(base, "/api/rules"),
            "evidence": body(base, "/api/evidence"),
            # Inteligência: a base rica dispara todo diagnóstico e descoberta; as outras, os recortes.
            "intelligence-rich": body(intel, "/api/intelligence"),
            "intelligence-all": body(base, "/api/intelligence"),
            "intelligence-east": body(base, "/api/intelligence?office=East"),
            "intelligence-sector": body(intel, "/api/intelligence?sector=retail"),
            "intelligence-empty": body(intel, "/api/intelligence?account=Ninguem"),
            "intelligence-deals-won": body(intel, "/api/intelligence/deals?outcome=won&seller=Ana%20Alfa"),
            "intelligence-deals-open": body(intel, "/api/intelligence/deals?outcome=open"),
            # A lista de termos proibidos é uma só: a tela a lê daqui (início de palavra).
            "vocabulary": {"forbidden_terms": list(policy.FORBIDDEN_TERMS), "match": "word_start"},
            "errors": {
                "404": body(base, pipeline("Fulano"), 404),
                "422": body(base, "/api/meta?as_of=31/12/2017", 422),
                "503": body(TestClient(create_app(MISSING_DATA_DIR)), "/api/sellers", 503),
            },
        }


def render(document: Any) -> str:
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    for name, document in fixtures().items():
        (FIXTURES_DIR / f"{name}.json").write_text(render(document), encoding="utf-8")
    print(f"Gravado em {FIXTURES_DIR.relative_to(SOLUTION_DIR)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
