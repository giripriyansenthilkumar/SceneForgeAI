"""
Integration tests for FastAPI REST Endpoints
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app

@pytest.mark.asyncio
async def test_api_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_api_generate_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/generate",
            json={"prompt": "Create a luxury yacht with teak decking", "category": "boat"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "model_url" in data
        assert data["vertex_count"] > 0
