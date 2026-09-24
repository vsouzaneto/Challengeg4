"""Job ``build_features``: raw -> bronze -> silver -> gold for one ``--as-of``.

Idempotent: bronze/silver are rewritten (they do not depend on ``as_of``) and the three gold
tables are rewritten only in their ``as_of=<date>`` partition. Prints a summary and writes
``_manifest.json`` (params, git sha, raw checksums, counts, duration) into each partition.

Run: ``uv run python -m lead_scorer.jobs build-features --as-of 2017-12-31``
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from pyspark.sql import SparkSession

from lead_scorer.config import BRONZE_DIR, GOLD_DIR, RAW_DIR, SILVER_DIR, SNAPSHOT_DATE
from lead_scorer.data import gold
from lead_scorer.data.checks import check_silver
from lead_scorer.data.load import load_bronze, write_bronze
from lead_scorer.data.silver import build_silver, write_silver
from lead_scorer.spark import get_spark


@dataclass(frozen=True)
class BuildSummary:
    as_of: date
    bronze_counts: dict[str, int]
    silver_counts: dict[str, int]
    gold_counts: dict[str, int]
    manifest: dict[str, Any]

    def lines(self) -> list[str]:
        out = [
            f"[build_features] as_of={self.as_of.isoformat()} snapshot={SNAPSHOT_DATE.isoformat()}"
        ]
        out.append("  bronze: " + ", ".join(f"{k}={v}" for k, v in self.bronze_counts.items()))
        keys = (
            "opportunities",
            "open",
            "engaging",
            "prospecting",
            "won",
            "lost",
            "account_unknown_open",
        )
        out.append("  silver: " + ", ".join(f"{k}={self.silver_counts[k]}" for k in keys))
        out.append("  gold:   " + ", ".join(f"{k}={v}" for k, v in self.gold_counts.items()))
        out.append(
            f"  git_sha={self.manifest['git_sha']} duration={self.manifest['duration_seconds']}s "
            f"manifest={gold.MANIFEST_NAME}"
        )
        return out


def run(
    as_of: date = SNAPSHOT_DATE,
    *,
    spark: SparkSession | None = None,
    raw_dir: Path = RAW_DIR,
    bronze_dir: Path = BRONZE_DIR,
    silver_dir: Path = SILVER_DIR,
    gold_dir: Path = GOLD_DIR,
    snapshot: date = SNAPSHOT_DATE,
) -> BuildSummary:
    """Execute the full data pipeline for ``as_of`` and return the counts written."""
    if as_of > snapshot:
        raise ValueError(
            f"as_of {as_of} is after the data snapshot {snapshot}; nothing is known there"
        )
    started = time.perf_counter()  # duration only; never used as a data timestamp
    session = spark or get_spark("lead-scorer-build-features")

    bronze = load_bronze(session, raw_dir)
    bronze_counts = write_bronze(bronze, bronze_dir)

    silver = build_silver(bronze)
    silver_counts = check_silver(silver, bronze.opportunities)
    silver_counts.update(write_silver(silver, silver_dir))

    build = gold.build_gold(silver.opportunities, as_of, snapshot)
    gold_counts = gold.write_gold(build, gold_dir)
    manifest = gold.write_manifest(
        build,
        raw_checksums=bronze.checksums,
        silver_counts=silver_counts,
        duration_seconds=time.perf_counter() - started,
        spark_version=session.version,
        gold_dir=gold_dir,
    )
    return BuildSummary(
        as_of=as_of,
        bronze_counts=bronze_counts,
        silver_counts=silver_counts,
        gold_counts=gold_counts,
        manifest=manifest,
    )


if __name__ == "__main__":  # pragma: no cover - thin wrapper around the typer CLI
    from lead_scorer.jobs.cli import app

    app(["build-features"] + __import__("sys").argv[1:])
