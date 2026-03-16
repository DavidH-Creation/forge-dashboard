"""Tests for WebSocket endpoint /ws/events."""

import pytest
from starlette.testclient import TestClient

from forge_dashboard.main import create_app
from forge_dashboard.plugin_sdk.models import ComponentEvent
from tests.conftest import MockPlugin


class TestWebSocket:
    def test_ws_connect_and_receive_event(self, tmp_path):
        """Connect to /ws/events, inject an event via bus._dispatch, receive it."""
        app = create_app(db_path=tmp_path / "test.db", auto_discover=False)
        app.state.registry.register(MockPlugin())

        with TestClient(app) as client:
            with client.websocket_connect("/ws/events") as ws:
                # Inject an event through the bus dispatcher
                event = ComponentEvent(
                    component="mock",
                    event_type="run_started",
                    run_id="r1",
                    timestamp="2026-03-16T10:00:00Z",
                    data={"stage": "EXECUTE"},
                )
                app.state.bus._dispatch(event)

                data = ws.receive_json()
                assert data["component"] == "mock"
                assert data["event_type"] == "run_started"
                assert data["run_id"] == "r1"

    def test_ws_replay(self, tmp_path):
        """Send a replay message and receive replay_complete."""
        app = create_app(db_path=tmp_path / "test.db", auto_discover=False)

        with TestClient(app) as client:
            with client.websocket_connect("/ws/events") as ws:
                ws.send_json({"type": "replay", "since": "2026-01-01T00:00:00Z"})
                data = ws.receive_json()
                assert data["type"] == "replay_complete"
                assert data["truncated"] is False
                assert data["count"] == 0

    def test_ws_subscribe_filter(self, tmp_path):
        """Subscribe to specific components and only receive matching events."""
        app = create_app(db_path=tmp_path / "test.db", auto_discover=False)
        app.state.registry.register(MockPlugin())

        with TestClient(app) as client:
            with client.websocket_connect("/ws/events") as ws:
                # Subscribe to only "mock" component
                ws.send_json({"type": "subscribe", "components": ["mock"]})

                # Inject an event for "mock" — should be received
                event_mock = ComponentEvent(
                    component="mock",
                    event_type="run_started",
                    run_id="r1",
                    timestamp="2026-03-16T10:00:00Z",
                    data={},
                )
                app.state.bus._dispatch(event_mock)

                data = ws.receive_json()
                assert data["component"] == "mock"

    def test_ws_subscribe_filters_out_other_components(self, tmp_path):
        """Events for non-subscribed components should be filtered out."""
        app = create_app(db_path=tmp_path / "test.db", auto_discover=False)
        app.state.registry.register(MockPlugin())

        with TestClient(app) as client:
            with client.websocket_connect("/ws/events") as ws:
                # Subscribe to only "other" component
                ws.send_json({"type": "subscribe", "components": ["other"]})

                # Inject an event for "mock" — should be filtered
                event_mock = ComponentEvent(
                    component="mock",
                    event_type="run_started",
                    run_id="r1",
                    timestamp="2026-03-16T10:00:00Z",
                    data={},
                )
                app.state.bus._dispatch(event_mock)

                # Inject an event for "other" — should be received
                event_other = ComponentEvent(
                    component="other",
                    event_type="run_started",
                    run_id="r2",
                    timestamp="2026-03-16T10:00:01Z",
                    data={},
                )
                app.state.bus._dispatch(event_other)

                data = ws.receive_json()
                assert data["component"] == "other"
                assert data["run_id"] == "r2"
