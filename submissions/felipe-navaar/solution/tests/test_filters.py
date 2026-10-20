import pandas as pd
import pytest

from src.filters import filter_queue


@pytest.fixture
def queue():
    return pd.DataFrame(
        {
            "opportunity_id": ["a", "b", "c"],
            "sales_agent": ["Ana", "Bruno", "Ana"],
            "manager": ["M1", "M1", "M2"],
            "regional_office": ["Central", "North", "Central"],
            "priority_score": [70, 40, 70],
            "rank": [1, 3, 2],
        }
    )


def test_combined_filters_preserve_score_and_global_rank(queue):
    result = filter_queue(queue, sales_agents=["Ana"], managers=["M2"], regional_offices=["Central"])

    assert result["opportunity_id"].tolist() == ["c"]
    assert result["priority_score"].tolist() == [70]
    assert result["rank"].tolist() == [2]


def test_empty_selection_means_no_filter(queue):
    result = filter_queue(queue, sales_agents=[], managers=[], regional_offices=[])

    assert result["opportunity_id"].tolist() == ["a", "b", "c"]


def test_no_match_is_empty(queue):
    result = filter_queue(queue, regional_offices=["South"])

    assert result.empty


def test_extended_filters_and_search(queue):
    enriched = queue.assign(product=["GTK 500", "MG Special", "GTK 500"], deal_stage=["Engaging", "Prospecting", "Engaging"], account=["Acme", "Beta", None])

    result = filter_queue(enriched, products=["GTK 500"], stages=["Engaging"], min_score=70, search_text="acme")

    assert result["opportunity_id"].tolist() == ["a"]


def test_missing_filter_column_is_reported(queue):
    with pytest.raises(ValueError, match="manager"):
        filter_queue(queue.drop(columns=["manager"]))
