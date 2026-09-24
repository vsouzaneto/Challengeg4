"""Explicit schemas for the four raw CRM tables (bronze contract).

Bronze never infers types: every CSV is read with the ``StructType`` declared here and
``mode="FAILFAST"`` so a malformed value aborts the job instead of silently becoming null.
Dates stay as strings in bronze; parsing is a *cleaning* step (``clean.py``), which keeps the raw
layer a byte-faithful mirror of the CSVs.
"""

from __future__ import annotations

from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

# Table names (raw CSV stem == bronze/silver table name).
OPPORTUNITIES = "sales_pipeline"
ACCOUNTS = "accounts"
PRODUCTS = "products"
SALES_TEAMS = "sales_teams"

TABLES: tuple[str, ...] = (OPPORTUNITIES, ACCOUNTS, PRODUCTS, SALES_TEAMS)

OPPORTUNITIES_SCHEMA = StructType(
    [
        StructField("opportunity_id", StringType(), nullable=False),
        StructField("sales_agent", StringType(), nullable=True),
        StructField("product", StringType(), nullable=True),
        StructField("account", StringType(), nullable=True),
        StructField("deal_stage", StringType(), nullable=True),
        StructField("engage_date", StringType(), nullable=True),
        StructField("close_date", StringType(), nullable=True),  # leakage-ok: raw outcome column
        StructField("close_value", DoubleType(), nullable=True),  # leakage-ok: raw outcome column
    ]
)

ACCOUNTS_SCHEMA = StructType(
    [
        StructField("account", StringType(), nullable=False),
        StructField("sector", StringType(), nullable=True),
        StructField("year_established", IntegerType(), nullable=True),
        StructField("revenue", DoubleType(), nullable=True),  # USD millions
        StructField("employees", IntegerType(), nullable=True),
        StructField("office_location", StringType(), nullable=True),
        StructField("subsidiary_of", StringType(), nullable=True),
    ]
)

PRODUCTS_SCHEMA = StructType(
    [
        StructField("product", StringType(), nullable=False),
        StructField("series", StringType(), nullable=True),
        StructField("sales_price", DoubleType(), nullable=True),
    ]
)

SALES_TEAMS_SCHEMA = StructType(
    [
        StructField("sales_agent", StringType(), nullable=False),
        StructField("manager", StringType(), nullable=True),
        StructField("regional_office", StringType(), nullable=True),
    ]
)

RAW_SCHEMAS: dict[str, StructType] = {
    OPPORTUNITIES: OPPORTUNITIES_SCHEMA,
    ACCOUNTS: ACCOUNTS_SCHEMA,
    PRODUCTS: PRODUCTS_SCHEMA,
    SALES_TEAMS: SALES_TEAMS_SCHEMA,
}

# Name of the lineage column added by bronze: SHA256 of the source CSV.
INGESTED_FROM = "_ingested_from"
