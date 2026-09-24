from pathlib import Path
from typing import Any

import pyarrow.parquet as pq
import pytest
from fastapi.testclient import TestClient

from api.settings import settings


def test_model_metrics(client: TestClient) -> None:
    res = client.get("/api/v1/model/metrics")
    assert res.status_code == 200
    body = res.json()
    assert body["model_version"] == "test-model-v1"
    assert body["metrics"]["backtest"]["2017-09-30"]["precision_at_10"] == 0.78
    assert body["feature_list"] == ["product_base_rate", "days_in_engaging"]
    assert body["model_card_path"].endswith("test-model-v1/model_card.md")
    assert body["model_card_markdown"].startswith("# Model card")


def test_model_metrics_503_when_absent(empty_client: TestClient) -> None:
    res = empty_client.get("/api/v1/model/metrics")
    assert res.status_code == 503
    err = res.json()["error"]
    assert err["code"] == "MODEL_ARTIFACTS_MISSING"
    assert "make pipeline" in err["hint"]


def test_model_metrics_503_when_metrics_json_missing(
    client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    models = tmp_path / "models"
    (models / "v9").mkdir(parents=True)
    (models / "latest").write_text("v9")
    monkeypatch.setattr(settings, "models_dir", models)
    res = client.get("/api/v1/model/metrics")
    assert res.status_code == 503
    assert "metrics.json" in res.json()["error"]["message"]


def test_feedback_roundtrip(client: TestClient) -> None:
    assert client.get("/api/v1/feedback").json() == []
    payload = {
        "opportunity_id": "T0001",
        "action": "contacted",
        "note": "Falei com o comprador.",
        "actor": "Anna Snelling",
    }
    res = client.post("/api/v1/feedback", json=payload)
    assert res.status_code == 201, res.text
    assert res.headers["X-As-Of"] == "2017-12-31"
    saved = res.json()
    assert saved["opportunity_id"] == "T0001"
    assert saved["action"] == "contacted"
    assert saved["note"] == payload["note"]
    assert saved["actor"] == "Anna Snelling"
    assert saved["as_of"] == "2017-12-31"
    assert saved["model_version"] == "test-model-v1"
    assert saved["priority_score"] == pytest.approx(64.5)
    assert len(saved["id"]) == 32
    assert saved["recorded_at"].endswith("Z") or "+00:00" in saved["recorded_at"]

    second = client.post(
        "/api/v1/feedback",
        json={"opportunity_id": "T0002", "action": "discard", "actor": "Vicki Laflamme"},
    )
    assert second.status_code == 201
    assert second.json()["note"] is None

    table = pq.read_table(str(settings.feedback_file))
    assert table.num_rows == 2
    assert set(table.column_names) >= {"id", "opportunity_id", "action", "recorded_at", "as_of"}
    assert not list(settings.feedback_file.parent.glob(".*.tmp"))

    listed = client.get("/api/v1/feedback").json()
    assert [r["opportunity_id"] for r in listed] == ["T0002", "T0001"]
    assert (
        client.get("/api/v1/feedback", params={"opportunity_id": "T0001"}).json()[0]["id"]
        == saved["id"]
    )


@pytest.mark.parametrize(
    "payload",
    [
        {"opportunity_id": "T0001", "action": "phoned", "actor": "x"},  # unknown action
        {"opportunity_id": "T0001", "action": "note", "actor": "x", "note": "n" * 501},
        {"opportunity_id": "", "action": "note", "actor": "x"},
        {"opportunity_id": "T0001", "action": "note"},  # actor missing
        {"action": "note", "actor": "x"},
    ],
)
def test_feedback_422(client: TestClient, payload: dict[str, Any]) -> None:
    res = client.post("/api/v1/feedback", json=payload)
    assert res.status_code == 422
    err = res.json()["error"]
    assert err["code"] == "VALIDATION_ERROR"
    assert err["details"]


def test_feedback_unknown_deal_404(client: TestClient) -> None:
    res = client.post(
        "/api/v1/feedback", json={"opportunity_id": "NOPE", "action": "note", "actor": "x"}
    )
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "DEAL_NOT_FOUND"


def test_feedback_503_without_artifacts(empty_client: TestClient) -> None:
    res = empty_client.post(
        "/api/v1/feedback", json={"opportunity_id": "T0001", "action": "note", "actor": "x"}
    )
    assert res.status_code == 503
    assert res.json()["error"]["code"] == "ARTIFACTS_MISSING"


def test_unknown_route_uses_envelope(client: TestClient) -> None:
    res = client.get("/api/v1/nope")
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "NOT_FOUND"


def test_feedback_closed_in_crm(client: TestClient) -> None:
    res = client.post(
        "/api/v1/feedback",
        json={"opportunity_id": "T0003", "action": "closed_in_crm", "actor": "Kami Bicknell"},
    )
    assert res.status_code == 201, res.text
    assert res.json()["action"] == "closed_in_crm"
    spec = client.get("/openapi.json").json()
    assert "closed_in_crm" in spec["components"]["schemas"]["FeedbackAction"]["enum"]
