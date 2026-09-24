"""Silver layer: cleaned, typed and conformed tables.

``opportunities`` is the analytical table: one row per deal (still 8.800), enriched with the
product catalogue, the account dimension and the sales team via **left joins**, each with a
boolean flag (``product_matched``, ``account_known``, ``agent_matched``). Rows are never dropped:
a deal without account is a deal we score with less confidence, not a deal we forget.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from lead_scorer.config import SILVER_DIR
from lead_scorer.data import clean
from lead_scorer.data.load import Bronze
from lead_scorer.data.schemas import ACCOUNTS, INGESTED_FROM, PRODUCTS, SALES_TEAMS


class RowLossError(AssertionError):
    """Raised when a join changes the number of opportunity rows."""


@dataclass(frozen=True)
class Silver:
    accounts: DataFrame
    products: DataFrame
    sales_teams: DataFrame
    opportunities: DataFrame

    def as_dict(self) -> dict[str, DataFrame]:
        return {
            ACCOUNTS: self.accounts,
            PRODUCTS: self.products,
            SALES_TEAMS: self.sales_teams,
            "opportunities": self.opportunities,
        }


#: account attributes carried into ``opportunities`` (all null when ``account_known`` is false).
ACCOUNT_ATTRIBUTES: tuple[str, ...] = (
    "sector",
    "year_established",
    "revenue",
    "employees",
    "office_location",
    "subsidiary_of",
    "is_subsidiary",
)


def _assert_no_row_loss(before: int, after: int, step: str) -> None:
    if before != after:
        raise RowLossError(f"{step}: expected {before} opportunity rows, got {after}")


def enrich_opportunities(
    opportunities: DataFrame, products: DataFrame, accounts: DataFrame, sales_teams: DataFrame
) -> DataFrame:
    """Left-join the dimensions onto the cleaned deals with match flags; assert no row loss."""
    n_before = opportunities.count()

    prod = products.select("product", "series", "sales_price").withColumn(
        "product_matched", F.lit(True)
    )
    acc = accounts.select("account", *ACCOUNT_ATTRIBUTES).withColumn("account_known", F.lit(True))
    team = sales_teams.select("sales_agent", "manager", "regional_office").withColumn(
        "agent_matched", F.lit(True)
    )

    df = (
        opportunities.join(prod, on="product", how="left")
        .join(acc, on="account", how="left")
        .join(team, on="sales_agent", how="left")
    )
    for flag in ("product_matched", "account_known", "agent_matched"):
        df = df.withColumn(flag, F.coalesce(F.col(flag), F.lit(False)))

    # Put the natural columns first, lineage last.
    leading = [
        "opportunity_id",
        "sales_agent",
        "product",
        "account",
        "deal_stage",
        "engage_date",
        "close_date",  # leakage-ok: silver keeps the raw outcome; gold separates it
        "close_value",  # leakage-ok: silver keeps the raw outcome; gold separates it
    ]
    rest = [c for c in df.columns if c not in leading and c != INGESTED_FROM]
    df = df.select(*leading, *rest, INGESTED_FROM)

    _assert_no_row_loss(n_before, df.count(), "silver.enrich_opportunities")
    return df


def build_silver(bronze: Bronze) -> Silver:
    """Apply ``clean.py`` to every table and build the enriched ``opportunities``."""
    accounts = clean.clean_accounts(bronze.accounts)
    products = clean.clean_products(bronze.products)
    sales_teams = clean.clean_sales_teams(bronze.sales_teams)
    opportunities = clean.clean_opportunities(bronze.opportunities)
    enriched = enrich_opportunities(opportunities, products, accounts, sales_teams)
    return Silver(
        accounts=accounts, products=products, sales_teams=sales_teams, opportunities=enriched
    )


def write_silver(silver: Silver, silver_dir: Path = SILVER_DIR) -> dict[str, int]:
    """Persist silver as parquet (``data/silver/<table>/``), overwrite; return row counts."""
    counts: dict[str, int] = {}
    for table, df in silver.as_dict().items():
        df.coalesce(1).write.mode("overwrite").parquet(str(silver_dir / table))
        counts[table] = df.count()
    return counts
