"""Reproduz a auditoria G1: python audit_data.py [--archive CAMINHO]."""

from __future__ import annotations

import argparse
from pathlib import Path

from leadscore.data import ARCHIVE_NAME, download_archive, load_dataset, report_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Audita as quatro tabelas públicas do CRM")
    parser.add_argument("--archive", type=Path, help="ZIP local; usa o cache/download padrão se omitido")
    parser.add_argument("--output", type=Path, help="Opcional: salva o relatório JSON neste caminho")
    args = parser.parse_args()

    archive = args.archive or Path(__file__).resolve().parent / "data" / ARCHIVE_NAME
    if args.archive is None:
        download_archive(archive)
    dataset = load_dataset(archive)
    report = report_json(dataset)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    print(report, end="")


if __name__ == "__main__":
    main()
