"""Tests for /nowcast, /alerts, /ingest endpoints, and ML inference."""
import pytest
from ml.inference import run_nowcast


@pytest.mark.asyncio
async def test_get_nowcast(client):
    response = await client.get("/nowcast/")
    assert response.status_code == 200
    data = response.json()
    assert "cells" in data or "nowcasts" in data
    if "model" in data and data["model"]:
        assert "ps72" in data["model"].get("name", "")


@pytest.mark.asyncio
async def test_get_alerts(client):
    response = await client.get("/alerts/")
    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data
    assert isinstance(data["alerts"], list)
    assert len(data["alerts"]) > 0


@pytest.mark.asyncio
async def test_ingest_radar(client):
    response = await client.post("/ingest/radar")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["source"] == "radar"


@pytest.mark.asyncio
async def test_ingest_lightning(client):
    response = await client.post("/ingest/lightning")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["source"] == "lightning"


def test_ml_inference_mode():
    res = run_nowcast()
    assert res["model"]["mode"] == "real"
    assert len(res["cells"]) >= 3
    for cell in res["cells"]:
        assert len(cell["forecast_positions"]) == 8

