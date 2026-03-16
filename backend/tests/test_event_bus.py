"""Tests for EventBus — central event dispatcher."""

import asyncio

import pytest
from unittest.mock import AsyncMock

from forge_dashboard.services.event_bus import EventBus
from forge_dashboard.plugin_sdk.registry import PluginRegistry
from forge_dashboard.plugin_sdk.models import ComponentEvent, HealthStatus


class FakePollPlugin:
    """Minimal plugin that yields pre-loaded events from poll_events."""

    name = "test"
    display_name = "Test"
    version = "0.0.1"
    stages = []

    def __init__(self):
        self._events: list[ComponentEvent] = []

    async def poll_events(self, since=None):
        events = list(self._events)
        self._events.clear()
        return events

    async def subscribe(self):
        return None

    async def health(self):
        return HealthStatus(component="test", status="healthy")

    async def list_runs(self, limit=20, offset=0, status_filter=None):
        return []

    async def get_run(self, run_id):
        ...

    async def get_artifacts(self, run_id):
        return []

    async def trigger(self, params):
        return "run-1"

    async def cancel(self, run_id):
        return True

    async def retry(self, run_id):
        return "run-2"

    async def get_config(self):
        return {}

    async def update_config(self, patch):
        ...


class TestEventBus:
    async def test_poll_dispatches_events(self):
        """poll_once should collect events from healthy plugins, record them, and dispatch."""
        plugin = FakePollPlugin()
        plugin._events = [
            ComponentEvent(
                component="test",
                event_type="run_started",
                run_id="r1",
                timestamp="2026-03-16T10:00:00Z",
                data={},
            ),
        ]
        registry = PluginRegistry()
        registry.register(plugin)
        journal = AsyncMock()
        journal.record = AsyncMock()

        bus = EventBus(registry=registry, journal=journal)
        collected: list[ComponentEvent] = []
        bus.add_listener(collected.append)
        await bus.poll_once()

        assert len(collected) == 1
        assert collected[0].run_id == "r1"
        assert collected[0].event_type == "run_started"
        journal.record.assert_called_once()

    async def test_poll_dispatches_multiple_events(self):
        """poll_once should dispatch all events from a plugin."""
        plugin = FakePollPlugin()
        plugin._events = [
            ComponentEvent(
                component="test",
                event_type="run_started",
                run_id="r1",
                timestamp="2026-03-16T10:00:00Z",
                data={},
            ),
            ComponentEvent(
                component="test",
                event_type="stage_changed",
                run_id="r1",
                timestamp="2026-03-16T10:00:01Z",
                data={"stage": "PLAN"},
            ),
        ]
        registry = PluginRegistry()
        registry.register(plugin)
        journal = AsyncMock()
        journal.record = AsyncMock()

        bus = EventBus(registry=registry, journal=journal)
        collected: list[ComponentEvent] = []
        bus.add_listener(collected.append)
        await bus.poll_once()

        assert len(collected) == 2
        assert collected[0].run_id == "r1"
        assert collected[1].event_type == "stage_changed"
        assert journal.record.call_count == 2

    async def test_poll_skips_degraded_plugins(self):
        """poll_once should not call poll_events on degraded plugins."""
        plugin = FakePollPlugin()
        plugin._events = [
            ComponentEvent(
                component="test",
                event_type="e1",
                run_id="r1",
                timestamp="2026-03-16T10:00:00Z",
                data={},
            ),
        ]
        registry = PluginRegistry()
        registry.register(plugin)
        registry._mark_degraded("test", error="broken")

        journal = AsyncMock()
        bus = EventBus(registry=registry, journal=journal)
        collected: list[ComponentEvent] = []
        bus.add_listener(collected.append)
        await bus.poll_once()

        assert len(collected) == 0
        journal.record.assert_not_called()

    async def test_poll_updates_last_poll_time(self):
        """poll_once should update _last_poll_time after each poll."""
        registry = PluginRegistry()
        journal = AsyncMock()
        bus = EventBus(registry=registry, journal=journal)

        assert bus._last_poll_time is None
        await bus.poll_once()
        assert bus._last_poll_time is not None

    async def test_add_remove_listener(self):
        """Listeners can be added and removed."""
        registry = PluginRegistry()
        journal = AsyncMock()
        bus = EventBus(registry=registry, journal=journal)

        callback = lambda e: None
        bus.add_listener(callback)
        assert callback in bus._listeners
        bus.remove_listener(callback)
        assert callback not in bus._listeners

    async def test_dispatch_handles_listener_errors(self):
        """A failing listener should not prevent other listeners from receiving events."""
        plugin = FakePollPlugin()
        plugin._events = [
            ComponentEvent(
                component="test",
                event_type="run_started",
                run_id="r1",
                timestamp="2026-03-16T10:00:00Z",
                data={},
            ),
        ]
        registry = PluginRegistry()
        registry.register(plugin)
        journal = AsyncMock()
        journal.record = AsyncMock()

        bus = EventBus(registry=registry, journal=journal)

        def bad_listener(event):
            raise RuntimeError("listener boom")

        collected: list[ComponentEvent] = []
        bus.add_listener(bad_listener)
        bus.add_listener(collected.append)
        await bus.poll_once()

        # Second listener should still receive the event
        assert len(collected) == 1

    async def test_start_and_stop(self):
        """start() should create a background task, stop() should cancel it."""
        registry = PluginRegistry()
        journal = AsyncMock()
        bus = EventBus(registry=registry, journal=journal, poll_interval=0.05)

        await bus.start()
        assert bus._task is not None
        assert not bus._task.done()

        # Let it run briefly
        await asyncio.sleep(0.1)

        await bus.stop()
        assert bus._task.done()

    async def test_poll_multiple_plugins(self):
        """poll_once should poll events from all healthy plugins."""
        plugin_a = FakePollPlugin()
        plugin_a.name = "alpha"
        plugin_a._events = [
            ComponentEvent(
                component="alpha",
                event_type="run_started",
                run_id="a1",
                timestamp="2026-03-16T10:00:00Z",
                data={},
            ),
        ]

        plugin_b = FakePollPlugin()
        plugin_b.name = "beta"
        plugin_b._events = [
            ComponentEvent(
                component="beta",
                event_type="run_started",
                run_id="b1",
                timestamp="2026-03-16T10:00:01Z",
                data={},
            ),
        ]

        registry = PluginRegistry()
        registry.register(plugin_a)
        registry.register(plugin_b)
        journal = AsyncMock()
        journal.record = AsyncMock()

        bus = EventBus(registry=registry, journal=journal)
        collected: list[ComponentEvent] = []
        bus.add_listener(collected.append)
        await bus.poll_once()

        assert len(collected) == 2
        run_ids = {e.run_id for e in collected}
        assert run_ids == {"a1", "b1"}
        assert journal.record.call_count == 2
