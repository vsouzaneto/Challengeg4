"""Single-source contract for scored deals.

The pipeline writes rows that satisfy ``ScoredDeal``; the API validates the parquet
against it at boot and exposes it through OpenAPI. Any change here is a contract change:
bump ``SCHEMA_VERSION`` and regenerate the committed artifacts and TS types.
"""

from lead_scorer_contracts.contracts import (
    EXAMPLE_SCORED_DEAL,
    SCHEMA_VERSION,
    Confidence,
    Direction,
    Reason,
    ReasonCode,
    ScoreBreakdown,
    ScoredDeal,
    Tier,
)

__all__ = [
    "EXAMPLE_SCORED_DEAL",
    "SCHEMA_VERSION",
    "Confidence",
    "Direction",
    "Reason",
    "ReasonCode",
    "ScoreBreakdown",
    "ScoredDeal",
    "Tier",
]
