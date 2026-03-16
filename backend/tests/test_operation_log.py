"""Tests for the OperationLog."""

import pytest
from pathlib import Path

from forge_dashboard.platform.state_store import StateStore
from forge_dashboard.platform.operation_log import OperationLog


async def _make_store(tmp_path: Path) -> StateStore:
    store = StateStore(tmp_path / "test.db")
    await store.init()
    return store


class TestOperationLog:
    async def test_log_and_list(self, tmp_path: Path):
        store = await _make_store(tmp_path)
        try:
            log = OperationLog(store)
            await log.record(
                component="bulwark",
                operation="trigger",
                run_id="run-1",
                params={"task": "build-feature"},
                result={"status": "accepted"},
            )

            entries = await log.list_recent()
            assert len(entries) == 1
            entry = entries[0]
            assert entry["component"] == "bulwark"
            assert entry["operation"] == "trigger"
            assert entry["run_id"] == "run-1"
            assert entry["params"]["task"] == "build-feature"
            assert entry["result"]["status"] == "accepted"
            assert "timestamp" in entry
        finally:
            await store.close()
