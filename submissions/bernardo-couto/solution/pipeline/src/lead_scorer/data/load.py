"""Bronze layer: checksum-verified, schema-explicit ingestion of the raw CSVs.

Bronze changes nothing in the data. It only (1) proves the raw files are the ones we audited
(``verify_checksums`` against ``SHA256SUMS``), (2) applies the declared ``StructType`` with
``FAILFAST`` and (3) stamps each row with ``_ingested_from`` = SHA256 of its source file.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from lead_scorer.config import BRONZE_DIR, RAW_DIR
from lead_scorer.data.schemas import (
    ACCOUNTS,
    INGESTED_FROM,
    OPPORTUNITIES,
    PRODUCTS,
    RAW_SCHEMAS,
    SALES_TEAMS,
    TABLES,
)

CHECKSUM_FILE = "SHA256SUMS"


class ChecksumMismatchError(RuntimeError):
    """Raised when a raw file differs from the audited copy (or is missing)."""


def sha256_of(path: Path) -> str:
    """Return the hex SHA256 digest of ``path`` (streamed, so it works for large files)."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_checksum_file(raw_dir: Path = RAW_DIR) -> dict[str, str]:
    """Parse ``SHA256SUMS`` (``<hex>  <file>`` per line) into ``{file: hex}``."""
    expected: dict[str, str] = {}
    for line in (raw_dir / CHECKSUM_FILE).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        digest, _, name = line.partition("  ")
        expected[name.strip().lstrip("*")] = digest.strip().lower()
    return expected


def verify_checksums(raw_dir: Path = RAW_DIR) -> dict[str, str]:
    """Verify every file listed in ``SHA256SUMS``; return ``{file: sha256}`` or raise.

    Called at the start of every job: raw is immutable and this is how we prove it.
    """
    expected = read_checksum_file(raw_dir)
    if not expected:
        raise ChecksumMismatchError(f"{raw_dir / CHECKSUM_FILE} is empty")
    problems: list[str] = []
    actual: dict[str, str] = {}
    for name, digest in sorted(expected.items()):
        path = raw_dir / name
        if not path.exists():
            problems.append(f"{name}: missing")
            continue
        actual[name] = sha256_of(path)
        if actual[name] != digest:
            problems.append(f"{name}: expected {digest[:12]}..., got {actual[name][:12]}...")
    if problems:
        raise ChecksumMismatchError(
            "raw data does not match SHA256SUMS (raw is immutable; never edit CSVs): "
            + "; ".join(problems)
        )
    return actual


def raw_csv_path(table: str, raw_dir: Path = RAW_DIR) -> Path:
    return raw_dir / f"{table}.csv"


def read_bronze_table(
    spark: SparkSession, table: str, raw_dir: Path = RAW_DIR, checksum: str | None = None
) -> DataFrame:
    """Read one raw CSV with its explicit schema, FAILFAST, plus ``_ingested_from``."""
    if table not in RAW_SCHEMAS:
        raise KeyError(f"unknown raw table {table!r}; expected one of {TABLES}")
    path = raw_csv_path(table, raw_dir)
    digest = checksum or sha256_of(path)
    df = spark.read.csv(
        str(path),
        schema=RAW_SCHEMAS[table],
        header=True,
        mode="FAILFAST",
        enforceSchema=True,
        nullValue="",
        emptyValue="",
    )
    return df.withColumn(INGESTED_FROM, F.lit(digest))


@dataclass(frozen=True)
class Bronze:
    """The four raw tables, typed and stamped, exactly as in the CSVs."""

    opportunities: DataFrame
    accounts: DataFrame
    products: DataFrame
    sales_teams: DataFrame
    checksums: dict[str, str]

    def as_dict(self) -> dict[str, DataFrame]:
        return {
            OPPORTUNITIES: self.opportunities,
            ACCOUNTS: self.accounts,
            PRODUCTS: self.products,
            SALES_TEAMS: self.sales_teams,
        }


def load_bronze(spark: SparkSession, raw_dir: Path = RAW_DIR) -> Bronze:
    """Verify checksums then read the four tables (fails fast on any drift)."""
    checksums = verify_checksums(raw_dir)

    def _read(table: str) -> DataFrame:
        return read_bronze_table(spark, table, raw_dir, checksums.get(f"{table}.csv"))

    return Bronze(
        opportunities=_read(OPPORTUNITIES),
        accounts=_read(ACCOUNTS),
        products=_read(PRODUCTS),
        sales_teams=_read(SALES_TEAMS),
        checksums=checksums,
    )


def write_bronze(bronze: Bronze, bronze_dir: Path = BRONZE_DIR) -> dict[str, int]:
    """Persist bronze as parquet (``data/bronze/<table>/``), overwrite; return row counts."""
    counts: dict[str, int] = {}
    for table, df in bronze.as_dict().items():
        df.coalesce(1).write.mode("overwrite").parquet(str(bronze_dir / table))
        counts[table] = df.count()
    return counts
