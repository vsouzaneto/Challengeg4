"""Valida conformidade G4 Challenge 001 antes do PR."""
from __future__ import annotations

import json
import sys

from analytics.paths import COMMAND_CENTER_DIST, DASH_PUBLIC, OUT, REPORTS, SUBMISSION, SOLUTION

REQUIRED_OUTPUTS = [
    "account_master.csv",
    "integration_qa.csv",
    "contas_analitico.csv",
    "fila_cs_top50.csv",
    "dashboard_bundle.json",
    "recommendations_impact.csv",
    "data_quality_summary.json",
]

REQUIRED_REPORTS = [
    "executive_summary.md",
    "ceo_one_pager.md",
    "playbook_cs_revolving.md",
    "causality_register.md",
    "data_quality_ceo.md",
    "model_and_limits.md",
]

REQUIRED_DOCS = [
    "METODOLOGIA.md",
    "ENTREGA-E-PR.md",
    "PR-BODY.md",
]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def main() -> None:
    for name in REQUIRED_OUTPUTS:
        if not (OUT / name).exists():
            fail(f"output ausente: {name}")
    if not (DASH_PUBLIC / "bundle.json").exists():
        fail("command-center/public/data/bundle.json ausente")
    if not (COMMAND_CENTER_DIST / "index.html").exists():
        fail("build React ausente — cd command-center && npm run build")

    qa = __import__("pandas").read_csv(OUT / "integration_qa.csv")
    if not qa["pass"].all():
        fail("integration QA falhou")

    for name in REQUIRED_REPORTS:
        if not (REPORTS / name).exists():
            fail(f"relatório: {name}")

    docs = SUBMISSION / "docs"
    for name in REQUIRED_DOCS:
        if not (docs / name).exists():
            fail(f"doc: {name}")

    readme = (SUBMISSION / "README.md").read_text(encoding="utf-8")
    if "Felipe de Lima Santiago" not in readme:
        fail("README sem identificação")

    proc = SUBMISSION / "process-log" / "PROCESS-LOG.md"
    if not proc.exists():
        fail("process log")

    spec = SUBMISSION / "docs" / "SPEC-001.md"
    if not spec.exists():
        fail("doc: SPEC-001.md")

    bundle = json.loads((OUT / "dashboard_bundle.json").read_text(encoding="utf-8"))
    for key in ("qualidade_dados", "recomendacao_destaque", "investigacoes"):
        if key not in bundle:
            fail(f"bundle sem {key}")

    print("=== VERIFICAÇÃO CE: APROVADA ===")


if __name__ == "__main__":
    main()
