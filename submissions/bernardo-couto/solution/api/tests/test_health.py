from fastapi.testclient import TestClient

EXPECTED_OPERATIONS = {
    "get_health",
    "get_meta",
    "list_deals",
    "get_deal",
    "list_agents",
    "list_managers",
    "list_regions",
    "get_pipeline_summary",
    "get_model_metrics",
    "create_feedback",
    "list_feedback",
}


def test_health(client: TestClient) -> None:
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "version": "1.0.0"}


def test_openapi_has_metadata(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    assert spec["info"]["title"] == "Lead Scorer API"
    assert spec["info"]["version"] == "1.0.0"
    assert spec["servers"]
    assert {t["name"] for t in spec["tags"]} >= {
        "operacao",
        "meta",
        "deals",
        "dimensoes",
        "pipeline",
        "modelo",
        "feedback",
    }
    assert all(t.get("description") for t in spec["tags"])
    assert "ScoredDeal" in spec["components"]["schemas"]
    assert "ErrorResponse" in spec["components"]["schemas"]
    assert spec["paths"]["/api/v1/meta"]["get"]["operationId"] == "get_meta"


def test_openapi_every_operation_documented(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    ops = {
        op["operationId"]: op
        for path in spec["paths"].values()
        for method, op in path.items()
        if method in {"get", "post"}
    }
    assert set(ops) == EXPECTED_OPERATIONS
    for op in ops.values():
        assert op["summary"] and op["description"] and op["tags"]
    deals = ops["list_deals"]
    assert {"404", "422", "503"} <= set(deals["responses"])
    assert "X-As-Of" in deals["responses"]["200"]["headers"]
    assert "X-Model-Version" in deals["responses"]["200"]["headers"]
    assert "503" in ops["get_model_metrics"]["responses"]
