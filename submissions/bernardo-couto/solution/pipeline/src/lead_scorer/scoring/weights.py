"""Named constants of the rules layer (docs/specs/scoring-spec.md section 2).

Every number the score depends on lives here, so the backtest can vary it and the model card
can print it. Defaults are the data-scientist's recommended configuration.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Weights:
    """Rules-layer configuration. ``w_p + w_v + w_u`` must sum to 100 (score is 0-100)."""

    prior_a: float = 20.0  # pseudo-count of the Bayesian prior (same alpha as gold)
    zombie_days: int = 138  # max observed cycle (Won and Lost)
    zombie_p_factor: float = 0.5  # convention, not an estimate: no deal ever closed after 138 d
    zombie_urgency: float = 0.2
    zombie_score_cap: float = 49.0
    prospecting_urgency: float = 0.5  # "unknown", not zero
    w_p: float = 25.0
    w_v: float = 35.0
    w_u: float = 40.0  # >= 40 keeps Spearman(score, price) < 0.9
    p_scale_lo: float = 0.30
    p_scale_hi: float = 0.80
    max_list_price: float = 26_768.0  # GTK 500, normalises the value axis
    high_ticket_price: float = 4_000.0
    low_ticket_price: float = 600.0
    min_group_n: int = 30  # below this the group's evidence is "small"
    overload_quantile: float = 0.75
    tier_a: float = 75.0
    tier_b: float = 55.0
    tier_c: float = 35.0
    late_cycle_days: int = 120  # above this SURVIVAL_POSITIVE adds the countdown to 138
    late_action_days: int = 100  # above this next_action becomes "close or give up this week"
    blend_model_weight: float = 0.0  # layer 2 (LR) in shadow mode

    def __post_init__(self) -> None:
        if abs(self.w_p + self.w_v + self.w_u - 100.0) > 1e-9:
            raise ValueError("w_p + w_v + w_u must sum to 100")
        if not 0.0 <= self.blend_model_weight <= 1.0:
            raise ValueError("blend_model_weight must be in [0, 1]")

    @property
    def points_per_p_win(self) -> float:
        """Score points per unit of ``p_win`` inside the scale window (25 / 0.5 = 50)."""
        return self.w_p / (self.p_scale_hi - self.p_scale_lo)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


DEFAULT_WEIGHTS = Weights()

__all__ = ["DEFAULT_WEIGHTS", "Weights"]
