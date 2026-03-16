"""Tests for FastAPI app factory — create_app lifecycle and basic routing."""

import pytest
from httpx import ASGITransport, AsyncClient

from forge_dashboard.main import create_app


async def _init_app(tmp_path, **kwargs):
    """Create app and manually init the store (ASGITransport skips lifespan)."""
    app = create_app(db_path=tmp_path / "test.db", auto_discover=False, **kwargs)
    await app.state.store.init()
    return app


class TestAppFactory:
    async def test_app_starts(self, tmp_path):
        """App should initialise, serve /api/overview, and return 200."""
        app = await _init_app(tmp_path)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/overview")
            assert resp.status_code == 200

    async def test_components_endpoint(self, tmp_path):
        """GET /api/components should return an empty list when no plugins are registered."""
        app = await _init_app(tmp_path)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/components")
            assert resp.status_code == 200
            assert isinstance(resp.json(), list)
            assert resp.json() == []

    async def test_cors_headers(self, tmp_path):
        """CORS middleware should allow any origin."""
        app = await _init_app(tmp_path)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.options(
                "/api/overview",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "GET",
                },
            )
            assert resp.status_code == 200
            assert resp.headers.get("access-control-allow-origin") == "*"

    async def test_events_endpoint(self, tmp_path):
        """GET /api/events should return an empty list when no events exist."""
        app = await _init_app(tmp_path)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/events")
            assert resp.status_code == 200
            assert resp.json() == []

    async def test_pipeline_flows_endpoint(self, tmp_path):
        """GET /api/pipeline/flows should return an empty list when no flows exist."""
        app = await _init_app(tmp_path)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/pipeline/flows")
            assert resp.status_code == 200
            assert resp.json() == []
