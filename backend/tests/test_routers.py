"""Tests for REST routers — all CRUD endpoints with a MockPlugin injected."""

import pytest
from httpx import ASGITransport, AsyncClient

from forge_dashboard.main import create_app
from tests.conftest import MockPlugin


async def _make_client(tmp_path, register_mock: bool = True):
    """Create an app with a MockPlugin pre-registered and return an AsyncClient.

    Manually inits the StateStore since httpx ASGITransport does not trigger
    ASGI lifespan events.
    """
    app = create_app(db_path=tmp_path / "test.db", auto_discover=False)
    await app.state.store.init()

    if register_mock:
        app.state.registry.register(MockPlugin())

    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test"), app


class TestOverviewRouter:
    async def test_get_overview(self, tmp_path):
        client, _ = await _make_client(tmp_path)
        async with client:
            resp = await client.get("/api/overview")
            assert resp.status_code == 200
            data = resp.json()
            assert "components" in data
            assert len(data["components"]) == 1
            assert data["components"][0]["name"] == "mock"


class TestComponentsRouter:
    async def test_list_components(self, tmp_path):
        client, _ = await _make_client(tmp_path)
        async with client:
            resp = await client.get("/api/components")
            assert resp.status_code == 200
            items = resp.json()
            assert len(items) == 1
            assert items[0]["name"] == "mock"
            assert items[0]["status"] == "healthy"

    async def test_list_runs(self, tmp_path):
        client, _ = await _make_client(tmp_path)
        async with client:
            resp = await client.get("/api/components/mock/runs")
            assert resp.status_code == 200
            runs = resp.json()
            assert len(runs) == 1
            assert runs[0]["run_id"] == "r1"

    async def test_get_run(self, tmp_path):
        client, _ = await _make_client(tmp_path)
        async with client:
            resp = await client.get("/api/components/mock/runs/r1")
            assert resp.status_code == 200
            data = resp.json()
            assert data["run_id"] == "r1"
            assert data["component"] == "mock"

    async def test_get_artifacts(self, tmp_path):
        client, _ = await _make_client(tmp_path)
        async with client:
            resp = await client.get("/api/components/mock/runs/r1/artifacts")
            assert resp.status_code == 200
            assert resp.json() == []

    async def test_get_config(self, tmp_path):
        client, _ = await _make_client(tmp_path)
        async with client:
            resp = await client.get("/api/components/mock/config")
            assert resp.status_code == 200
            assert resp.json() == {"key": "value"}

    async def test_update_config(self, tmp_path):
        client, _ = await _make_client(tmp_path)
        async with client:
            resp = await client.put(
                "/api/components/mock/config",
                json={"key": "new_value"},
            )
            assert resp.status_code == 200
            assert resp.json() == {"status": "ok"}

    async def test_nonexistent_component_runs_404(self, tmp_path):
        client, _ = await _make_client(tmp_path)
        async with client:
            resp = await client.get("/api/components/nonexistent/runs")
            assert resp.status_code == 404
            data = resp.json()
            assert data["detail"]["error"] == "ComponentNotFound"

    async def test_nonexistent_component_run_detail_404(self, tmp_path):
        client, _ = await _make_client(tmp_path)
        async with client:
            resp = await client.get("/api/components/nonexistent/runs/r1")
            assert resp.status_code == 404

    async def test_nonexistent_component_config_404(self, tmp_path):
        client, _ = await _make_client(tmp_path)
        async with client:
            resp = await client.get("/api/components/nonexistent/config")
            assert resp.status_code == 404


class TestOperationsRouter:
    async def test_trigger(self, tmp_path):
        client, _ = await _make_client(tmp_path)
        async with client:
            resp = await client.post(
                "/api/components/mock/trigger",
                json={"goal": "test"},
            )
            assert resp.status_code == 200
            assert resp.json()["run_id"] == "run-new"

    async def test_cancel(self, tmp_path):
        client, _ = await _make_client(tmp_path)
        async with client:
            resp = await client.delete("/api/components/mock/runs/r1")
            assert resp.status_code == 200
            assert resp.json()["cancelled"] is True

    async def test_retry(self, tmp_path):
        client, _ = await _make_client(tmp_path)
        async with client:
            resp = await client.post("/api/components/mock/runs/r1/retry")
            assert resp.status_code == 200
            assert resp.json()["run_id"] == "run-retry"

    async def test_trigger_nonexistent_404(self, tmp_path):
        client, _ = await _make_client(tmp_path)
        async with client:
            resp = await client.post(
                "/api/components/nonexistent/trigger",
                json={"goal": "test"},
            )
            assert resp.status_code == 404


class TestPipelineRouter:
    async def test_list_flows(self, tmp_path):
        client, _ = await _make_client(tmp_path)
        async with client:
            resp = await client.get("/api/pipeline/flows")
            assert resp.status_code == 200
            assert isinstance(resp.json(), list)

    async def test_get_events(self, tmp_path):
        client, _ = await _make_client(tmp_path)
        async with client:
            resp = await client.get("/api/events")
            assert resp.status_code == 200
            assert isinstance(resp.json(), list)

    async def test_get_events_with_filters(self, tmp_path):
        client, _ = await _make_client(tmp_path)
        async with client:
            resp = await client.get(
                "/api/events",
                params={"since": "2026-01-01T00:00:00Z", "component": "mock", "limit": 50},
            )
            assert resp.status_code == 200
            assert isinstance(resp.json(), list)
