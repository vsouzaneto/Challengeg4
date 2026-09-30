import pytest


@pytest.mark.asyncio
async def test_health_ok(client):
    r = await client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] in ("ok", "degraded")


@pytest.mark.asyncio
async def test_liveness(client):
    r = await client.get("/api/v1/health/live")
    assert r.status_code == 200
