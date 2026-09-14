#!/usr/bin/env python3
"""Public CLI for the reproducible RavenStack data build."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


SUBMISSION_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SUBMISSION_ROOT / "solution" / "src"))

from ravenstack import BuildConfig, build  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build RavenStack raw/stage/gold analytics.")
    parser.add_argument(
        "--source-dir",
        type=Path,
        help="Optional directory containing the five original Kaggle CSV files.",
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Replace an invalid/missing local raw copy from pinned Kaggle v1.",
    )
    parser.add_argument(
        "--no-export",
        action="store_true",
        help="Build DuckDB without refreshing artifacts/data CSV and JSON exports.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = BuildConfig.defaults(
        source_dir=args.source_dir,
        force_download=args.force_download,
        export_csv=not args.no_export,
    )
    result = build(config)
    print(f"Build concluído: {result.database_path}")
    print(
        f"Raw={result.raw_rows} | elegíveis={result.eligible_rows} | "
        f"quarentena={result.quarantined_rows} | corte={result.data_cutoff}"
    )
    if not args.no_export:
        print(f"Gold revisável: {result.export_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

