from datetime import date

import pandas as pd

from src.analyze import analyze_pipeline


def _fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "opportunity_id": ["a", "b", "c", "d"],
            "deal_stage": ["Won", "Lost", "Engaging", "Prospecting"],
            "product": ["P", "P", "P", "Q"],
            "engage_date": ["2017-12-01", "2017-12-10", "2017-12-20", None],
            "close_date": ["2017-12-15", "2017-12-20", None, None],
            "close_value": [100, 0, None, None],
            "account": ["A", "A", None, None],
        }
    )


def test_analysis_uses_explicit_denominators_and_open_age():
    report = analyze_pipeline(_fixture(), date(2017, 12, 31))

    assert report["rows"] == 4
    assert report["unique_ids"] == 4
    assert report["stage_counts"] == {"Won": 1, "Lost": 1, "Engaging": 1, "Prospecting": 1}
    assert report["open"]["n"] == 2
    assert report["closed"]["n"] == 2
    assert report["won_only"]["n"] == 1
    assert report["won_only"]["by_product"]["P"]["mean"] == 100.0
    assert report["closed_all"]["by_product"]["P"]["mean"] == 50.0
    assert report["win_rate_among_closed"] == 0.5
    assert report["open_age_since_engage"]["n_known"] == 1
    assert report["open_age_since_engage"]["n_missing"] == 1
    assert report["open_age_since_engage"]["negative_count"] == 0


def test_analysis_rejects_missing_contract_column():
    frame = _fixture().drop(columns=["account"])

    try:
        analyze_pipeline(frame)
    except ValueError as error:
        assert "account" in str(error)
    else:
        raise AssertionError("Era esperado erro para coluna obrigatória ausente")

