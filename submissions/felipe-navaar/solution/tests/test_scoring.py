import pandas as pd

from src.scoring import load_policy, score_open_opportunities


def _open_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "opportunity_id": ["B", "A", "C", "closed"],
            "deal_stage": ["Engaging", "Engaging", "Prospecting", "Won"],
            "account": ["Acme", None, None, "Acme"],
            "engage_date": [pd.Timestamp("2017-12-01"), None, pd.Timestamp("2017-12-01"), pd.Timestamp("2017-01-01")],
            "sales_price": [100, 200, None, 500],
            "close_value": [None, None, None, 1000],
            "close_date": [None, None, None, pd.Timestamp("2017-02-01")],
        }
    )


def test_scores_only_open_deals_and_reconciles_factors():
    result = score_open_opportunities(_open_fixture())

    assert result["opportunity_id"].tolist() == ["A", "B", "C"]
    assert result["priority_score"].tolist() == [70, 70, 40]
    assert all(sum(f["contribution"] for f in factors) == score for factors, score in zip(result["score_factors"], result["priority_score"]))
    assert result["policy_version"].eq("heuristic-v1").all()
    assert result["reference_date"].eq("2017-12-31").all()
    assert result["rank"].tolist() == [1, 2, 3]


def test_missing_values_warn_but_do_not_change_stage_score():
    result = score_open_opportunities(_open_fixture())
    prospecting = result.loc[result["opportunity_id"].eq("C")].iloc[0]

    assert prospecting["priority_score"] == 40
    assert "account ausente; score não reduzido" in prospecting["warnings"]
    assert "preço de catálogo indisponível; desempate por preço não aplicado" in prospecting["warnings"]


def test_ranking_is_stable_after_input_shuffle():
    frame = _open_fixture()
    expected = score_open_opportunities(frame)["opportunity_id"].tolist()
    shuffled = score_open_opportunities(frame.sample(frac=1, random_state=42))["opportunity_id"].tolist()

    assert shuffled == expected


def test_policy_is_explicit():
    policy = load_policy()

    assert policy["policy_version"] == "heuristic-v1"
    assert policy["stage_points"] == {"Prospecting": 30, "Engaging": 60}
    assert "close_value" not in policy["weighted_fields"]

