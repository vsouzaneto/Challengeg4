"""Data-quality expectations. Every failure raises ``DataQualityError`` and aborts the job.

Reference counts come from the audited snapshot (skill ``crm-dataset``) and are re-asserted on
every run: if the raw files change, the pipeline refuses to produce a gold layer silently.
"""

from __future__ import annotations

from collections.abc import Iterable

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from lead_scorer.data.clean import CLOSED_STAGES, DEAL_STAGES, OPEN_STAGES
from lead_scorer.data.silver import Silver


class DataQualityError(AssertionError):
    """A contract on a silver/gold table was violated."""


#: Audited counts of the 2017-12-31 snapshot.
REFERENCE_COUNTS: dict[str, int] = {
    "opportunities": 8_800,
    "open": 2_089,
    "engaging": 1_589,
    "prospecting": 500,
    "won": 4_238,
    "lost": 2_473,
    "accounts": 85,
    "products": 7,
    "sales_teams": 35,
}


# --- primitive expectations -----------------------------------------------------------------------


def expect_count(df: DataFrame, expected: int, name: str) -> int:
    actual = df.count()
    if actual != expected:
        raise DataQualityError(f"{name}: expected {expected} rows, got {actual}")
    return actual


def expect_unique(df: DataFrame, column: str, name: str) -> None:
    total = df.count()
    distinct = df.select(column).distinct().count()
    if total != distinct:
        raise DataQualityError(f"{name}.{column}: {total - distinct} duplicate values")


def expect_not_null(df: DataFrame, columns: Iterable[str], name: str) -> None:
    for column in columns:
        nulls = df.filter(F.col(column).isNull()).count()
        if nulls:
            raise DataQualityError(f"{name}.{column}: {nulls} null values")


def expect_in_set(df: DataFrame, column: str, allowed: Iterable[str], name: str) -> None:
    bad = df.filter(~F.col(column).isin(list(allowed)) | F.col(column).isNull()).count()
    if bad:
        raise DataQualityError(f"{name}.{column}: {bad} values outside {sorted(allowed)}")


def expect_all_true(df: DataFrame, column: str, name: str) -> None:
    bad = df.filter(~F.col(column)).count()
    if bad:
        raise DataQualityError(f"{name}.{column}: {bad} rows are false")


def expect_dates_parsed(df: DataFrame, raw: DataFrame, column: str, name: str) -> None:
    """Every non-null raw string must have parsed into a non-null date (same row count)."""
    raw_non_null = raw.filter(F.col(column).isNotNull()).count()
    parsed_non_null = df.filter(F.col(column).isNotNull()).count()
    if raw_non_null != parsed_non_null:
        raise DataQualityError(
            f"{name}.{column}: {raw_non_null - parsed_non_null} values failed to parse as dates"
        )


def expect_no_columns(df: DataFrame, forbidden: Iterable[str], name: str) -> None:
    present = sorted(set(df.columns) & set(forbidden))
    if present:
        raise DataQualityError(f"{name}: forbidden columns present {present}")


# --- table contracts ------------------------------------------------------------------------------


def check_silver(silver: Silver, raw_opportunities: DataFrame) -> dict[str, int]:
    """Run the silver contract; return the counts it verified (for the manifest)."""
    opps = silver.opportunities
    name = "silver.opportunities"

    counts = {"opportunities": expect_count(opps, REFERENCE_COUNTS["opportunities"], name)}
    expect_unique(opps, "opportunity_id", name)
    expect_not_null(opps, ["opportunity_id", "sales_agent", "product", "deal_stage"], name)
    expect_in_set(opps, "deal_stage", DEAL_STAGES, name)

    for key, stages in {
        "open": OPEN_STAGES,
        "engaging": ("Engaging",),
        "prospecting": ("Prospecting",),
        "won": ("Won",),
        "lost": ("Lost",),
    }.items():
        counts[key] = expect_count(
            opps.filter(F.col("deal_stage").isin(list(stages))),
            REFERENCE_COUNTS[key],
            f"{name}[{key}]",
        )

    # Dates: every raw string parsed; closed deals have both dates; open deals have no close.
    expect_dates_parsed(opps, raw_opportunities, "engage_date", name)
    expect_dates_parsed(opps, raw_opportunities, "close_date", name)  # leakage-ok: DQ on silver
    closed = opps.filter(F.col("deal_stage").isin(list(CLOSED_STAGES)))
    expect_not_null(
        closed, ["engage_date", "close_date", "close_value"], f"{name}[closed]"
    )  # leakage-ok: DQ on silver
    open_with_close = opps.filter(
        F.col("deal_stage").isin(list(OPEN_STAGES))
        & F.col("close_date").isNotNull()  # leakage-ok: DQ on silver
    ).count()
    if open_with_close:
        raise DataQualityError(f"{name}: {open_with_close} open deals carry a close date")
    bad_order = closed.filter(
        F.col("close_date") < F.col("engage_date")
    ).count()  # leakage-ok: DQ on silver
    if bad_order:
        raise DataQualityError(f"{name}: {bad_order} closed deals close before they engage")

    # FK coverage: every agent and product must resolve; every non-null account must resolve.
    expect_all_true(opps, "agent_matched", name)
    expect_all_true(opps, "product_matched", name)
    expect_all_true(opps.filter(F.col("account").isNotNull()), "account_known", name)
    counts["account_unknown_open"] = opps.filter(
        F.col("deal_stage").isin(list(OPEN_STAGES)) & ~F.col("account_known")
    ).count()

    # Dimensions: unique keys, reference sizes.
    for table, df, key in (
        ("accounts", silver.accounts, "account"),
        ("products", silver.products, "product"),
        ("sales_teams", silver.sales_teams, "sales_agent"),
    ):
        counts[table] = expect_count(df, REFERENCE_COUNTS[table], f"silver.{table}")
        expect_unique(df, key, f"silver.{table}")
        expect_not_null(df, [key], f"silver.{table}")
    return counts
