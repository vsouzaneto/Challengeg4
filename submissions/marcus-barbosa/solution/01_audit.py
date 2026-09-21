"""Etapa 0 do método: relatório de saúde dos dados antes de qualquer fator de scoring.

Uso:
    python 01_audit.py            # lê data/raw/*.csv e escreve ../docs/data_health_report.md
"""
from __future__ import annotations

import json
from pathlib import Path

from leadscorer.audit import write_report
from leadscorer.data import load_tables

HERE = Path(__file__).resolve().parent
RAW = HERE / "data" / "raw"
DOCS = HERE.parent / "docs"


def main() -> int:
    tables = load_tables(RAW)
    DOCS.mkdir(exist_ok=True)
    metrics = write_report(tables, DOCS / "data_health_report.md")
    (DOCS / "data_health_metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"relatório: {DOCS / 'data_health_report.md'}")
    for k in ("rows_sales_pipeline", "reference_date", "rows_without_account", "open_rows_without_account",
              "orphan_product_rows", "cycle_negative", "win_rate_global"):
        print(f"  {k}: {metrics.get(k)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
