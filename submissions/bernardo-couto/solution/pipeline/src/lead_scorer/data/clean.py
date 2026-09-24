"""Single source of data corrections (bronze -> silver cleaning rules).

Every fix to the raw data lives here, as data (mapping tables) plus small pure functions:
- product names: the pipeline writes ``GTXPro`` while the catalogue has ``GTX Pro``;
- sectors: ``technolgy`` is a typo of ``technology`` (12 accounts);
- whitespace trimming on every string column;
- ISO date parsing into ``DateType``;
- ``deal_stage`` domain.

Nothing else in the codebase is allowed to hard-code these corrections (a hook enforces it).
"""

from __future__ import annotations

from collections.abc import Iterable

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StringType

# --- mapping tables -----------------------------------------------------------------------------

#: pipeline spelling -> catalogue spelling (``products.csv`` is the reference).
PRODUCT_NAME_MAP: dict[str, str] = {
    "GTXPro": "GTX Pro",
}

#: raw sector -> canonical sector.
SECTOR_MAP: dict[str, str] = {
    "technolgy": "technology",
}

#: closed-world domain of ``deal_stage``.
DEAL_STAGES: tuple[str, ...] = ("Prospecting", "Engaging", "Won", "Lost")
OPEN_STAGES: tuple[str, ...] = ("Prospecting", "Engaging")
CLOSED_STAGES: tuple[str, ...] = ("Won", "Lost")

DATE_FORMAT = "yyyy-MM-dd"


# --- column-level helpers -------------------------------------------------------------------------


def _apply_map(col: Column, mapping: dict[str, str]) -> Column:
    """Replace exact matches using ``mapping``; other values pass through unchanged."""
    expr = col
    for raw, fixed in mapping.items():
        expr = F.when(col == F.lit(raw), F.lit(fixed)).otherwise(expr)
    return expr


def normalize_product(col: Column) -> Column:
    """Trim and map product spellings to the catalogue (``GTXPro`` -> ``GTX Pro``)."""
    return _apply_map(F.trim(col), PRODUCT_NAME_MAP)


def normalize_sector(col: Column) -> Column:
    """Trim, lower-case and fix known typos (``technolgy`` -> ``technology``)."""
    return _apply_map(F.lower(F.trim(col)), SECTOR_MAP)


def parse_date(col: Column) -> Column:
    """Parse an ISO ``yyyy-MM-dd`` string into ``DateType`` (null stays null)."""
    return F.to_date(F.trim(col), DATE_FORMAT)


def trim_strings(df: DataFrame, columns: Iterable[str] | None = None) -> DataFrame:
    """Trim every ``StringType`` column (or the given subset); empty strings become null."""
    targets = (
        list(columns)
        if columns is not None
        else [f.name for f in df.schema.fields if isinstance(f.dataType, StringType)]
    )
    for name in targets:
        trimmed = F.trim(F.col(name))
        df = df.withColumn(name, F.when(trimmed == "", F.lit(None)).otherwise(trimmed))
    return df


# --- table-level cleaning -------------------------------------------------------------------------


def clean_opportunities(df: DataFrame) -> DataFrame:
    """Trim, normalise ``product`` and type the dates; keeps every row and every column."""
    df = trim_strings(df, ["opportunity_id", "sales_agent", "product", "account", "deal_stage"])
    return (
        df.withColumn("product", normalize_product(F.col("product")))
        .withColumn("engage_date", parse_date(F.col("engage_date")))
        .withColumn("close_date", parse_date(F.col("close_date")))  # leakage-ok: silver typing only
    )


def clean_accounts(df: DataFrame) -> DataFrame:
    """Trim and normalise ``sector``; adds ``is_subsidiary``."""
    df = trim_strings(df, ["account", "sector", "office_location", "subsidiary_of"])
    return df.withColumn("sector", normalize_sector(F.col("sector"))).withColumn(
        "is_subsidiary", F.col("subsidiary_of").isNotNull()
    )


def clean_products(df: DataFrame) -> DataFrame:
    """Trim and normalise the catalogue side too (idempotent if already canonical)."""
    df = trim_strings(df, ["product", "series"])
    return df.withColumn("product", normalize_product(F.col("product")))


def clean_sales_teams(df: DataFrame) -> DataFrame:
    return trim_strings(df, ["sales_agent", "manager", "regional_office"])
