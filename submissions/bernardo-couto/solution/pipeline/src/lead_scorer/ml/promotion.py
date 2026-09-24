"""Promotion rule of layer 2 (docs/specs/scoring-spec.md section 5).

The model leaves shadow mode only if, in **every** backtest cut, ``AUC-PR(model) >= AUC-PR(base
rate) + MARGIN`` **and** ``Brier(model) <= Brier(base rate)`` after calibration. Otherwise the
blend weight stays 0 and the scores are rules-only.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

AUC_PR_MARGIN = 0.02
PROMOTED_BLEND_WEIGHT = 0.5


@dataclass(frozen=True)
class CutCriterion:
    cut: str
    auc_pr_model: float
    auc_pr_base: float
    brier_model: float
    brier_base: float
    auc_pr_ok: bool
    brier_ok: bool

    @property
    def passed(self) -> bool:
        return self.auc_pr_ok and self.brier_ok


@dataclass(frozen=True)
class PromotionDecision:
    promoted: bool
    blend_model_weight: float
    criteria: list[CutCriterion] = field(default_factory=list)
    rule: str = (
        f"promote only if, in every cut, AUC-PR(model) >= AUC-PR(base rate) + {AUC_PR_MARGIN} "
        "and Brier(model) <= Brier(base rate) after calibration"
    )

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for crit, item in zip(self.criteria, data["criteria"], strict=True):
            item["passed"] = crit.passed
        return data


def decide(
    backtest: dict[str, dict[str, Any]],
    shadow: dict[str, dict[str, Any]] | None,
    margin: float = AUC_PR_MARGIN,
) -> PromotionDecision:
    """``backtest[cut]`` has the base-rate ``auc_pr``/``brier``; ``shadow[cut]`` the model's."""
    if not shadow or not backtest:
        return PromotionDecision(promoted=False, blend_model_weight=0.0)
    criteria: list[CutCriterion] = []
    for cut in sorted(backtest):
        base, model = backtest[cut], shadow.get(cut)
        if model is None:
            return PromotionDecision(promoted=False, blend_model_weight=0.0)
        crit = CutCriterion(
            cut=cut,
            auc_pr_model=float(model["auc_pr"]),
            auc_pr_base=float(base["auc_pr"]),
            brier_model=float(model["brier"]),
            brier_base=float(base["brier"]),
            auc_pr_ok=float(model["auc_pr"]) >= float(base["auc_pr"]) + margin,
            brier_ok=float(model["brier"]) <= float(base["brier"]),
        )
        criteria.append(crit)
    promoted = bool(criteria) and all(c.passed for c in criteria)
    return PromotionDecision(
        promoted=promoted,
        blend_model_weight=PROMOTED_BLEND_WEIGHT if promoted else 0.0,
        criteria=criteria,
    )


__all__ = ["AUC_PR_MARGIN", "CutCriterion", "PromotionDecision", "decide"]
