"""Re-export of the shared contract so pipeline code imports ``lead_scorer.contracts``.

The source of truth lives in ``solution/shared/lead_scorer_contracts`` (see ADR 0007).
"""

from lead_scorer_contracts import (
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
