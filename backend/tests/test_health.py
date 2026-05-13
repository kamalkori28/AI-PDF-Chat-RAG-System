import pytest


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["database"] == "ok"
    assert payload["ollama"] in {"ok", "unavailable", "models_missing"}


@pytest.mark.asyncio
async def test_readiness_reports_ollama_state(client):
    response = await client.get("/api/v1/health/ready")
    assert response.status_code in {200, 503}
    payload = response.json()
    if response.status_code == 200:
        assert payload["ollama"] == "ok"
    else:
        assert payload["detail"]["ollama"] in {"unavailable", "models_missing"}
