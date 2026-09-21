"""Etapa 3 do método: backtest por snapshot do score e das categorias.

Uso:
    python 03_backtest.py
Escreve ../docs/backtest.md e ../docs/backtest.json.
"""
from __future__ import annotations

import json
from pathlib import Path

from leadscorer.backtest import run_backtest, to_markdown
from leadscorer.data import enrich, load_tables

HERE = Path(__file__).resolve().parent
RAW = HERE / "data" / "raw"
DOCS = HERE.parent / "docs"


def main() -> int:
    e = enrich(load_tables(RAW))
    results = run_backtest(e)
    DOCS.mkdir(exist_ok=True)
    (DOCS / "backtest.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    md = to_markdown(results)
    (DOCS / "backtest.md").write_text(md, encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
