"""Closed feature list of layer 2 (docs/specs/scoring-spec.md section 1).

Features are derived **only** from ``gold/opportunity_features``. Anything about the account is
forbidden as a predictor (``account_known`` encodes "already closed": 100% of closed deals have
an account vs 32% of the still-open ones), as are outcome columns and calendar leakage.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from lead_scorer.scoring.weights import DEFAULT_WEIGHTS

CATEGORICAL_FEATURES: tuple[str, ...] = ("product",)
NUMERIC_FEATURES: tuple[str, ...] = (
    "product_rate",
    "log_days",
    "is_zombie",
    "log_price",
    "open_load",
    "survival_rate",
)
FEATURES: tuple[str, ...] = CATEGORICAL_FEATURES + NUMERIC_FEATURES

#: Never in the model vector (tested). Prefix matches are listed in FORBIDDEN_PREFIXES.
FORBIDDEN: frozenset[str] = frozenset(
    {
        "account",
        "account_known",
        "sector",
        "revenue",
        "employees",
        "subsidiary_of",
        "is_subsidiary",
        "office_location",
        "year_established",
        "account_age_years",
        "win_rate_account",
        "n_account",
        "engage_month",
        "engage_date",
        "label",
        "label_won",
        "close_value",  # leakage-ok: deny-list entry
        "close_date",  # leakage-ok: deny-list entry
        "cycle_days",
        "realized_value",
        "days_to_close_from_as_of",
    }
)
FORBIDDEN_PREFIXES: tuple[str, ...] = ("account_", "engage_month", "close_", "outcome_", "label")

LABEL_COL = "label"
ID_COL = "opportunity_id"


def is_forbidden(column: str) -> bool:
    return column in FORBIDDEN or column.startswith(FORBIDDEN_PREFIXES)


def add_ml_features(features: DataFrame) -> DataFrame:
    """Derive the model features from an ``opportunity_features`` frame (keeps other columns).

    ``log_days`` and ``survival_rate`` are null for Prospecting deals (no ``engage_date``); the
    Spark ML ``Imputer`` fills them with the training median.
    """
    days = F.col("days_in_engaging")
    return (
        features.withColumn(
            "product_rate", F.coalesce(F.col("win_rate_product"), F.col("global_win_rate"))
        )
        .withColumn("log_days", F.log1p(days.cast("double")))
        .withColumn(
            "is_zombie",
            (days.isNotNull() & (days > F.lit(DEFAULT_WEIGHTS.zombie_days))).cast("double"),
        )
        .withColumn("log_price", F.log1p(F.col("sales_price").cast("double")))
        .withColumn("open_load", F.col("open_deals_agent").cast("double"))
        .withColumn("survival_rate", F.col("win_rate_survival").cast("double"))
    )


def assert_feature_contract() -> None:
    bad = [f for f in FEATURES if is_forbidden(f)]
    if bad:
        raise AssertionError(f"forbidden features in FEATURES: {bad}")


assert_feature_contract()

__all__ = [
    "CATEGORICAL_FEATURES",
    "FEATURES",
    "FORBIDDEN",
    "FORBIDDEN_PREFIXES",
    "ID_COL",
    "LABEL_COL",
    "NUMERIC_FEATURES",
    "add_ml_features",
    "is_forbidden",
]
