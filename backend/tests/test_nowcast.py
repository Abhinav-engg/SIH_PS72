"""Tests for /nowcast endpoint."""
import pytest


@pytest.mark.asyncio
async def test_get_nowcast(client):
    response = await client.get("/nowcast/")
    assert response.status_code == 200
    data = response.json()
    assert "cells" in data or "nowcasts" in data
    if "model" in data and data["model"]:
        assert "ps72" in data["model"].get("name", "")
