"""Tests for API key authentication middleware."""

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from forge_dashboard.config import DashboardConfig
from forge_dashboard.main import create_app


async def _init_app(tmp_path, **kwargs):
    app = create_app(db_path=tmp_path / "test.db", auto_discover=False, **kwargs)
    await app.state.store.init()
    return app


class TestAuthDisabled:
    async def test_no_api_key_allows_all(self, tmp_path):
        """Without api_key configured, all requests pass through."""
        app = await _init_app(tmp_path)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/overview")
            assert resp.status_code == 200

    async def test_no_api_key_no_header_needed(self, tmp_path):
        """Requests without Authorization header succeed when api_key is not set."""
        app = await _init_app(tmp_path)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/components")
            assert resp.status_code == 200


class TestAuthEnabled:
    async def test_missing_header_returns_401(self, tmp_path):
        """Requests to /api/ without Authorization header → 401."""
        cfg = DashboardConfig(api_key="secret")
        app = await _init_app(tmp_path, config=cfg)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/overview")
            assert resp.status_code == 401
            assert resp.json()["detail"] == "Unauthorized"

    async def test_wrong_key_returns_401(self, tmp_path):
        """Requests with wrong Bearer token → 401."""
        cfg = DashboardConfig(api_key="secret")
        app = await _init_app(tmp_path, config=cfg)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(
                "/api/overview", headers={"Authorization": "Bearer wrong"}
            )
            assert resp.status_code == 401

    async def test_correct_key_returns_200(self, tmp_path):
        """Requests with correct Bearer token → 200."""
        cfg = DashboardConfig(api_key="secret")
        app = await _init_app(tmp_path, config=cfg)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(
                "/api/overview", headers={"Authorization": "Bearer secret"}
            )
            assert resp.status_code == 200

    async def test_non_api_path_no_auth_needed(self, tmp_path):
        """Paths outside /api/ and /ws/ are not protected."""
        cfg = DashboardConfig(api_key="secret")
        app = await _init_app(tmp_path, config=cfg)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # /docs is outside /api/ and /ws/
            resp = await client.get("/docs")
            assert resp.status_code != 401

    def test_ws_without_auth_rejected(self, tmp_path):
        """WebSocket /ws/events without auth header → connection closed."""
        cfg = DashboardConfig(api_key="secret")
        app = create_app(db_path=tmp_path / "test.db", auto_discover=False, config=cfg)
        with TestClient(app) as client:
            with pytest.raises(WebSocketDisconnect):
                with client.websocket_connect("/ws/events") as ws:
                    ws.receive_json()

    def test_ws_with_correct_auth_accepted(self, tmp_path):
        """WebSocket /ws/events with correct Authorization → accepted."""
        cfg = DashboardConfig(api_key="secret")
        app = create_app(db_path=tmp_path / "test.db", auto_discover=False, config=cfg)
        with TestClient(app) as client:
            with client.websocket_connect(
                "/ws/events", headers={"Authorization": "Bearer secret"}
            ) as ws:
                ws.send_json({"type": "replay", "since": "2026-01-01T00:00:00Z"})
                data = ws.receive_json()
                assert data["type"] == "replay_complete"


class TestCorsConfigurable:
    async def test_cors_uses_configured_origins(self, tmp_path):
        """CORS should reflect the cors_origins config instead of hardcoded *."""
        cfg = DashboardConfig(cors_origins=["http://localhost:3000"])
        app = await _init_app(tmp_path, config=cfg)
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
            assert resp.headers.get("access-control-allow-origin") == "http://localhost:3000"
