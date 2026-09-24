from datetime import date

import pytest
from pydantic import ValidationError

from lead_scorer_contracts import EXAMPLE_SCORED_DEAL, SCHEMA_VERSION, Reason, ScoredDeal


def test_example_validates() -> None:
    deal = ScoredDeal.model_validate(EXAMPLE_SCORED_DEAL)
    assert deal.as_of == date(2017, 12, 31)
    assert deal.reasons[0].code == "AGENT_PRODUCT_FIT"


def test_score_bounds() -> None:
    for bad in (-0.1, 100.1):
        with pytest.raises(ValidationError):
            ScoredDeal.model_validate({**EXAMPLE_SCORED_DEAL, "priority_score": bad})


def test_reason_direction_closed_set() -> None:
    with pytest.raises(ValidationError):
        Reason.model_validate(
            {"code": "ZOMBIE_RISK", "direction": "?", "weight": 0.0, "text_pt": "x"}
        )


def test_schema_version_is_semver() -> None:
    assert SCHEMA_VERSION.count(".") == 2


def test_sales_price_is_optional_and_nonnegative() -> None:
    row = {k: v for k, v in EXAMPLE_SCORED_DEAL.items() if k != "sales_price"}
    assert ScoredDeal.model_validate(row).sales_price is None
    assert ScoredDeal.model_validate(EXAMPLE_SCORED_DEAL).sales_price == 4821.0
    with pytest.raises(ValidationError):
        ScoredDeal.model_validate({**EXAMPLE_SCORED_DEAL, "sales_price": -1.0})
