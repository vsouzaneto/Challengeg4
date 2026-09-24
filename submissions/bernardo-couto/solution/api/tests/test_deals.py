from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from api.repository import parse_sort, repository
from api.settings import settings
from tests.fixtures import build_rows, write_partition


def test_list_defaults_sorted_by_score(client: TestClient) -> None:
    res = client.get("/api/v1/deals")
    assert res.status_code == 200
    assert res.headers["X-As-Of"] == "2017-12-31"
    assert res.headers["X-Model-Version"] == "test-model-v1"
    body = res.json()
    assert body["total"] == 24
    assert body["as_of"] == "2017-12-31"
    assert body["model_version"] == "test-model-v1"
    assert body["sort"] == "-priority_score"
    assert body["limit"] == 50 and body["offset"] == 0
    scores = [d["priority_score"] for d in body["items"]]
    assert scores == sorted(scores, reverse=True)
    assert body["items"][0]["reasons"][0]["code"] == "AGENT_PRODUCT_FIT"


def test_pagination(client: TestClient) -> None:
    page1 = client.get("/api/v1/deals", params={"limit": 10, "offset": 0}).json()
    page2 = client.get("/api/v1/deals", params={"limit": 10, "offset": 10}).json()
    page3 = client.get("/api/v1/deals", params={"limit": 10, "offset": 20}).json()
    assert [len(p["items"]) for p in (page1, page2, page3)] == [10, 10, 4]
    ids = [d["opportunity_id"] for p in (page1, page2, page3) for d in p["items"]]
    assert len(set(ids)) == 24
    assert page1["total"] == 24


@pytest.mark.parametrize(
    ("params", "expected_total", "check"),
    [
        ({"sales_agent": "Darcel Schlecht"}, 6, lambda d: d["sales_agent"] == "Darcel Schlecht"),
        ({"manager": "Cara Losch"}, 6, lambda d: d["manager"] == "Cara Losch"),
        ({"regional_office": "Central"}, 12, lambda d: d["regional_office"] == "Central"),
        ({"deal_stage": "Prospecting"}, 4, lambda d: d["deal_stage"] == "Prospecting"),
        ({"tier": "A"}, 6, lambda d: d["tier"] == "A"),
        ({"min_score": 60}, 12, lambda d: d["priority_score"] >= 60),
        ({"account_known": "false"}, 8, lambda d: d["account"] is None),
        ({"account_known": "true"}, 16, lambda d: d["account"] is not None),
        ({"tier": "A", "manager": "Melvin Marxen"}, 6, lambda d: d["tier"] == "A"),
        ({"tier": "A", "regional_office": "East"}, 0, lambda d: False),
    ],
)
def test_filters(
    client: TestClient,
    params: dict[str, Any],
    expected_total: int,
    check: Callable[[dict[str, Any]], bool],
) -> None:
    body = client.get("/api/v1/deals", params={**params, "limit": 500}).json()
    assert body["total"] == expected_total
    assert len(body["items"]) == expected_total
    assert all(check(d) for d in body["items"])


def test_sort_multi_key_and_nulls_last(client: TestClient) -> None:
    body = client.get(
        "/api/v1/deals", params={"sort": "-days_in_engaging,opportunity_id", "limit": 500}
    ).json()
    days = [d["days_in_engaging"] for d in body["items"]]
    present = [x for x in days if x is not None]
    assert present == sorted(present, reverse=True)
    assert days[-4:] == [None] * 4  # Prospecting rows go last
    asc = client.get("/api/v1/deals", params={"sort": "expected_value"}).json()
    ev = [d["expected_value"] for d in asc["items"]]
    assert ev == sorted(ev)


def test_sort_invalid_field_is_422_envelope(client: TestClient) -> None:
    res = client.get("/api/v1/deals", params={"sort": "close_value"})
    assert res.status_code == 422
    err = res.json()["error"]
    assert err["code"] == "INVALID_SORT"
    assert "close_value" in err["message"]
    assert err["hint"]


def test_query_validation_422(client: TestClient) -> None:
    res = client.get("/api/v1/deals", params={"min_score": 150})
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "VALIDATION_ERROR"
    assert res.json()["error"]["details"][0]["loc"] == ["query", "min_score"]
    assert client.get("/api/v1/deals", params={"tier": "Z"}).status_code == 422
    assert client.get("/api/v1/deals", params={"limit": 0}).status_code == 422


def test_as_of_backtest_partition_with_json_reasons(client: TestClient) -> None:
    res = client.get("/api/v1/deals", params={"as_of": "2017-09-30"})
    assert res.status_code == 200
    assert res.headers["X-As-Of"] == "2017-09-30"
    assert res.headers["X-Model-Version"] == "test-old"
    body = res.json()
    assert body["as_of"] == "2017-09-30"
    assert body["items"][0]["as_of"] == "2017-09-30"  # filled from the partition folder
    assert isinstance(body["items"][0]["reasons"], list)
    assert body["items"][0]["reasons"][0]["text_pt"]


def test_as_of_missing_is_404(client: TestClient) -> None:
    res = client.get("/api/v1/deals", params={"as_of": "2016-01-01"})
    assert res.status_code == 404
    err = res.json()["error"]
    assert err["code"] == "AS_OF_NOT_FOUND"
    assert "2017-12-31" in err["hint"]


def test_get_deal(client: TestClient) -> None:
    res = client.get("/api/v1/deals/T0003")
    assert res.status_code == 200
    assert res.headers["X-As-Of"] == "2017-12-31"
    deal = res.json()
    assert deal["opportunity_id"] == "T0003"
    assert deal["days_in_engaging"] == 150
    assert deal["tier"] == "D"
    assert {r["code"] for r in deal["reasons"]} >= {"ZOMBIE_RISK", "ACCOUNT_UNKNOWN"}
    assert deal["next_action"]


def test_get_deal_404(client: TestClient) -> None:
    res = client.get("/api/v1/deals/NOPE")
    assert res.status_code == 404
    assert res.json()["error"] == {
        "code": "DEAL_NOT_FOUND",
        "message": "Deal 'NOPE' não está aberto em as_of=2017-12-31.",
        "hint": "Confira o opportunity_id ou troque o parâmetro `as_of`.",
    }


def test_503_when_partitions_absent(empty_client: TestClient) -> None:
    for path in ("/api/v1/deals", "/api/v1/deals/T0001", "/api/v1/agents"):
        res = empty_client.get(path)
        assert res.status_code == 503, path
        err = res.json()["error"]
        assert err["code"] == "ARTIFACTS_MISSING"
        assert "make pipeline" in err["hint"]


def test_invalid_parquet_fails_boot_and_503(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    scores = tmp_path / "scores"
    rows = build_rows(date(2017, 12, 31))
    rows[0]["priority_score"] = 250.0  # out of contract
    rows[1]["reasons"] = []
    write_partition(scores, date(2017, 12, 31), rows=rows)
    monkeypatch.setattr(settings, "scores_dir", scores)
    repository.reset()

    from api.main import app

    with pytest.raises(RuntimeError, match="ARTIFACTS_INVALID"), TestClient(app):
        pass

    monkeypatch.setattr(settings, "validate_on_boot", False)
    with TestClient(app) as c:
        res = c.get("/api/v1/deals")
        assert res.status_code == 503
        err = res.json()["error"]
        assert err["code"] == "ARTIFACTS_INVALID"
        assert {d["opportunity_id"] for d in err["details"]} == {"T0000", "T0001"}
        meta = c.get("/api/v1/meta").json()  # meta keeps answering
        assert meta["artifacts_present"] is True and meta["open_deals"] is None


def test_parse_sort_unit() -> None:
    assert parse_sort(None) == [("priority_score", True)]
    assert parse_sort("-expected_value, sales_agent") == [
        ("expected_value", True),
        ("sales_agent", False),
    ]
    with pytest.raises(ValueError, match="inválido"):
        parse_sort("close_date")


def test_repository_caches(client: TestClient) -> None:
    first = repository.snapshot()
    assert repository.snapshot() is first
    repository.reset()
    assert repository.snapshot() is not first


@pytest.mark.parametrize(
    ("params", "expected_ids"),
    [
        ({"queue": "confirm"}, {"T0003"}),
        ({"queue": "confirm", "min_days_in_engaging": 139, "max_days_in_engaging": 180}, {"T0003"}),
        ({"queue": "confirm", "min_days_in_engaging": 200}, set()),
        (
            {"min_days_in_engaging": 101, "max_days_in_engaging": 138},
            {"T0019", "T0020", "T0021", "T0022"},
        ),
        ({"max_days_in_engaging": 15}, {"T0000", "T0001"}),
    ],
)
def test_queue_and_days_filters(
    client: TestClient, params: dict[str, Any], expected_ids: set[str]
) -> None:
    body = client.get("/api/v1/deals", params={**params, "limit": 500}).json()
    assert {d["opportunity_id"] for d in body["items"]} == expected_ids
    assert body["total"] == len(expected_ids)


def test_work_queue_keeps_prospecting_and_excludes_stalled(client: TestClient) -> None:
    body = client.get("/api/v1/deals", params={"queue": "work", "limit": 500}).json()
    assert body["total"] == 23
    ids = {d["opportunity_id"] for d in body["items"]}
    assert "T0003" not in ids
    assert sum(1 for d in body["items"] if d["deal_stage"] == "Prospecting") == 4
    assert client.get("/api/v1/deals", params={"queue": "later"}).status_code == 422


def test_sales_price_present_or_null_per_partition(client: TestClient) -> None:
    latest = client.get("/api/v1/deals/T0003").json()
    assert latest["sales_price"] == 1000.0 + 3 * 250.0
    old = client.get("/api/v1/deals/T0003", params={"as_of": "2017-09-30"}).json()
    assert old["sales_price"] is None  # column absent in the parquet: tolerated
