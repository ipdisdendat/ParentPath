"""Test health check endpoints"""
import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    """Test basic health check"""
    response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test root endpoint"""
    response = await client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "ParentPath API"
    assert data["status"] == "operational"
