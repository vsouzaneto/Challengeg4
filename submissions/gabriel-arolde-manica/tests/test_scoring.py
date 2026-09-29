import pandas as pd

from solution.scoring import (
    calculate_product_win_rates,
    calculate_score
)


def test_product_win_rates():
    data = pd.DataFrame({
        "product": [
            "Product A",
            "Product A",
            "Product B",
            "Product B"
        ],
        "deal_stage": [
            "Won",
            "Lost",
            "Won",
            "Won"
        ]
    })

    rates = calculate_product_win_rates(data)

    assert rates["Product A"] == 0.5
    assert rates["Product B"] == 1.0


def test_engaging_deal_gets_priority_score():

    deal = pd.Series({
        "deal_stage": "Engaging",
        "engage_date": "2026-01-01",
        "product": "Product A",
        "revenue": 5000,
        "account": "Test Account"
    })

    rates = {
        "Product A": 0.65
    }

    result = calculate_score(
        deal,
        rates,
        "2026-10-01"
    )

    assert 0 <= result["score"] <= 100
    assert result["score"] > 0
    assert len(result["reasons"]) > 0


def test_prospecting_deal_gets_risk_flag():

    deal = pd.Series({
        "deal_stage": "Prospecting",
        "engage_date": None,
        "product": "Product A",
        "revenue": 500,
        "account": None
    })

    rates = {
        "Product A": 0.60
    }

    result = calculate_score(
        deal,
        rates,
        "2026-10-01"
    )

    assert result["score"] >= 0
    assert len(result["risk_flags"]) > 0
