"""Tests for the EventJournal — persist and query events."""

import pytest
from datetime import datetime, timezone
from pathlib import Path

from forge_dashboard.plugin_sdk.models import ComponentEvent
from forge_dashboard.platform.state_store import StateStore
from forge_dashboard.platform.event_journal import EventJournal


async def _make_store(tmp_path: Path) -> StateStore:
    store = StateStore(tmp_path / "test.db")
    await store.init()
    return store


def _event(component: str, event_type: str, run_id: str, ts: str, **data) -> ComponentEvent:
    return ComponentEvent(
        component=component,
        event_type=event_type,
        run_id=run_id,
        timestamp=ts,
        data=data,
    )


class TestEventJournal:
    async def test_record_and_query(self, tmp_path: Path):
        store = await _make_store(tmp_path)
        try:
            journal = EventJournal(store)
            ev = _event("bulwark", "phase_completed", "run-1", "2026-03-16T10:00:00Z", phase="EXECUTE")
            await journal.record(ev)

            events = await journal.query()
            assert len(events) == 1
            assert events[0].component == "bulwark"
            assert events[0].event_type == "phase_completed"
            assert events[0].run_id == "run-1"
            assert events[0].data["phase"] == "EXECUTE"
        finally:
            await store.close()

    async def test_query_since(self, tmp_path: Path):
        store = await _make_store(tmp_path)
        try:
            journal = EventJournal(store)
            await journal.record(_event("bulwark", "start", "run-1", "2026-03-16T09:00:00Z"))
            await journal.record(_event("bulwark", "done", "run-1", "2026-03-16T10:00:00Z"))
            await journal.record(_event("bulwark", "start", "run-2", "2026-03-16T11:00:00Z"))

            events = await journal.query(since="2026-03-16T09:30:00Z")
            assert len(events) == 2
            assert events[0].event_type == "done"
            assert events[1].event_type == "start"
        finally:
            await store.close()

    async def test_query_component_filter(self, tmp_path: Path):
        store = await _make_store(tmp_path)
        try:
            journal = EventJournal(store)
            await journal.record(_event("bulwark", "start", "run-1", "2026-03-16T10:00:00Z"))
            await journal.record(_event("cartographer", "start", "run-2", "2026-03-16T10:01:00Z"))
            await journal.record(_event("bulwark", "done", "run-1", "2026-03-16T10:02:00Z"))

            events = await journal.query(component="cartographer")
            assert len(events) == 1
            assert events[0].component == "cartographer"
        finally:
            await store.close()

    async def test_replay_limits(self, tmp_path: Path):
        store = await _make_store(tmp_path)
        try:
            journal = EventJournal(store, max_replay_events=2)
            for i in range(5):
                await journal.record(
                    _event("bulwark", f"ev-{i}", "run-1", f"2026-03-16T10:0{i}:00Z")
                )

            events, truncated = await journal.query_with_truncation()
            assert truncated is True
            assert len(events) == 2
            # Should be the last 2 events (most recent)
            assert events[0].event_type == "ev-3"
            assert events[1].event_type == "ev-4"
        finally:
            await store.close()
