"""Tests for the SQLite StateStore — schema initialisation."""

import pytest
from pathlib import Path

from forge_dashboard.platform.state_store import StateStore


class TestStateStore:
    async def test_init_creates_tables(self, tmp_path: Path):
        db_path = tmp_path / "test.db"
        store = StateStore(db_path)
        await store.init()
        try:
            tables = await store.list_tables()
            expected = {
                "pipeline_flows",
                "flow_steps",
                "event_journal",
                "operation_log",
                "artifact_index",
            }
            assert expected == set(tables)
        finally:
            await store.close()

    async def test_init_idempotent(self, tmp_path: Path):
        db_path = tmp_path / "test.db"
        store = StateStore(db_path)
        await store.init()
        await store.init()  # second init should not fail
        try:
            tables = await store.list_tables()
            assert len(tables) == 5
        finally:
            await store.close()
