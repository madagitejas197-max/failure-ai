"""
Tests for GET /api/v1/health endpoint.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_200(client: AsyncClient):
    """Health endpoint must return HTTP 200."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_response_schema(client: AsyncClient):
    """Health response must include status, version, and environment."""
    response = await client.get("/api/v1/health")
    body = response.json()

    assert body["status"] == "ok"
    assert "version" in body
    assert "environment" in body


@pytest.mark.asyncio
async def test_health_status_is_ok(client: AsyncClient):
    """Status field must always be the string 'ok'."""
    response = await client.get("/api/v1/health")
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_health_version_is_string(client: AsyncClient):
    """Version field must be a non-empty string."""
    response = await client.get("/api/v1/health")
    version = response.json().get("version", "")
    assert isinstance(version, str) and len(version) > 0


@pytest.mark.asyncio
async def test_health_content_type_json(client: AsyncClient):
    """Response content-type must be application/json."""
    response = await client.get("/api/v1/health")
    assert "application/json" in response.headers.get("content-type", "")
