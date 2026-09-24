from fastapi.testclient import TestClient


def test_agents(client: TestClient) -> None:
    res = client.get("/api/v1/agents")
    assert res.status_code == 200
    assert res.headers["X-As-Of"] == "2017-12-31"
    body = res.json()
    assert len(body) == 4
    assert sum(a["open_deals"] for a in body) == 24
    darcel = next(a for a in body if a["sales_agent"] == "Darcel Schlecht")
    assert darcel["manager"] == "Melvin Marxen"
    assert darcel["regional_office"] == "Central"
    assert sum(darcel["tier_distribution"].values()) == 6
    evs = [a["expected_value"] for a in body]
    assert evs == sorted(evs, reverse=True)


def test_managers_and_regions(client: TestClient) -> None:
    managers = client.get("/api/v1/managers").json()
    assert {m["manager"] for m in managers} == {
        "Melvin Marxen",
        "Dustin Brinkmann",
        "Cara Losch",
        "Rocco Neubert",
    }
    assert all(len(m["sales_agents"]) == 1 for m in managers)

    res = client.get("/api/v1/regions", params={"as_of": "2017-09-30"})
    assert res.headers["X-Model-Version"] == "test-old"
    regions = {r["regional_office"]: r for r in res.json()}
    assert set(regions) == {"Central", "East", "West"}
    assert regions["Central"]["agents"] == 2
    assert regions["Central"]["open_deals"] == 12
    assert regions["Central"]["managers"] == ["Dustin Brinkmann", "Melvin Marxen"]


def test_pipeline_summary_default_by_manager(client: TestClient) -> None:
    res = client.get("/api/v1/pipeline/summary")
    assert res.status_code == 200
    body = res.json()
    assert body["group_by"] == "manager"
    assert body["zombie_threshold_days"] == 138
    total = body["total"]
    assert total["key"] == "*"
    assert total["open_deals"] == 24
    assert total["engaging"] == 20 and total["prospecting"] == 4
    assert total["zombie_count"] == 1
    assert total["zombie_value"] == 500.0 + 3 * 137.5
    assert total["account_coverage"] == round(16 / 24, 4)
    assert sum(total["tier_distribution"].values()) == 24
    assert 0 <= total["avg_priority_score"] <= 100
    assert len(body["groups"]) == 4
    assert sum(g["open_deals"] for g in body["groups"]) == 24


def test_pipeline_summary_filtered_by_agent(client: TestClient) -> None:
    body = client.get(
        "/api/v1/pipeline/summary",
        params={"group_by": "sales_agent", "manager": "Rocco Neubert"},
    ).json()
    assert [g["key"] for g in body["groups"]] == ["Kami Bicknell"]
    assert body["groups"][0]["zombie_count"] == 1  # T0003 belongs to Kami
    assert body["total"]["open_deals"] == 6
    by_region = client.get(
        "/api/v1/pipeline/summary", params={"group_by": "regional_office"}
    ).json()
    assert {g["key"] for g in by_region["groups"]} == {"Central", "East", "West"}


def test_pipeline_summary_validation_and_503(client: TestClient, empty_client: TestClient) -> None:
    assert client.get("/api/v1/pipeline/summary", params={"group_by": "product"}).status_code == 422
    res = empty_client.get("/api/v1/pipeline/summary")
    assert res.status_code == 503
    assert res.json()["error"]["code"] == "ARTIFACTS_MISSING"


def test_pipeline_summary_cooling_and_nominal_values(client: TestClient) -> None:
    body = client.get("/api/v1/pipeline/summary").json()
    assert body["cooling_min_days"] == 101
    total = body["total"]
    assert total["cooling_count"] == 4  # T0019..T0022 (105-120 days); T0018 = 100 excluded
    assert total["cooling_value"] == round(sum(500.0 + i * 137.5 for i in range(19, 23)), 2)
    assert total["nominal_zombie_value"] == 1000.0 + 3 * 250.0
    kami = next(g for g in body["groups"] if g["key"] == "Rocco Neubert")
    assert kami["nominal_zombie_value"] == 1750.0
    no_zombies = next(g for g in body["groups"] if g["key"] == "Melvin Marxen")
    assert no_zombies["zombie_count"] == 0 and no_zombies["nominal_zombie_value"] == 0.0

    old = client.get("/api/v1/pipeline/summary", params={"as_of": "2017-09-30"}).json()
    assert old["total"]["zombie_count"] == 1
    assert old["total"]["nominal_zombie_value"] is None  # partition without sales_price
