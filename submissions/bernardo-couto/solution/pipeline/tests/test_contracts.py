from datetime import date

import pytest
from pydantic import ValidationError

from lead_scorer.contracts import EXAMPLE_SCORED_DEAL, Reason, ScoredDeal


def test_example_row_validates() -> None:
    deal = ScoredDeal.model_validate(EXAMPLE_SCORED_DEAL)
    assert deal.tier == "A"
    assert deal.as_of == date(2017, 12, 31)


@pytest.mark.parametrize(
    ("field", "value"),
    [("priority_score", 101), ("priority_score", -1), ("p_win", 1.5), ("urgency", -0.01)],
)
def test_score_bounds(field: str, value: float) -> None:
    with pytest.raises(ValidationError):
        ScoredDeal.model_validate({**EXAMPLE_SCORED_DEAL, field: value})


def test_prospecting_without_account_or_days() -> None:
    row = {
        **EXAMPLE_SCORED_DEAL,
        "deal_stage": "Prospecting",
        "account": None,
        "days_in_engaging": None,
    }
    deal = ScoredDeal.model_validate(row)
    assert deal.account is None and deal.days_in_engaging is None


def test_reasons_required() -> None:
    with pytest.raises(ValidationError):
        ScoredDeal.model_validate({**EXAMPLE_SCORED_DEAL, "reasons": []})


def test_reason_is_frozen() -> None:
    reason = Reason(code="HIGH_TICKET", direction="+", weight=0.1, text_pt="Ticket alto.")
    with pytest.raises(ValidationError):
        reason.weight = 0.2
