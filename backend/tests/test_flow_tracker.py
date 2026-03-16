"""Tests for the FlowTracker."""

import pytest
from pathlib import Path

from forge_dashboard.platform.state_store import StateStore
from forge_dashboard.platform.flow_tracker import FlowTracker


async def _make_store(tmp_path: Path) -> StateStore:
    store = StateStore(tmp_path / "test.db")
    await store.init()
    return store


class TestFlowTracker:
    async def test_create_flow(self, tmp_path: Path):
        store = await _make_store(tmp_path)
        try:
            tracker = FlowTracker(store)
            flow_id = await tracker.create_flow("deploy-pipeline", ["cartographer", "bulwark"])

            assert flow_id.startswith("flow-")
            flow = await tracker.get_flow(flow_id)
            assert flow["name"] == "deploy-pipeline"
            assert flow["status"] == "pending"
            assert len(flow["steps"]) == 2
            assert flow["steps"][0]["component"] == "cartographer"
            assert flow["steps"][0]["step_order"] == 0
            assert flow["steps"][0]["status"] == "pending"
            assert flow["steps"][1]["component"] == "bulwark"
            assert flow["steps"][1]["step_order"] == 1
        finally:
            await store.close()

    async def test_start_step(self, tmp_path: Path):
        store = await _make_store(tmp_path)
        try:
            tracker = FlowTracker(store)
            flow_id = await tracker.create_flow("test-flow", ["cartographer", "bulwark"])

            await tracker.start_step(flow_id, "cartographer", "run-1")

            flow = await tracker.get_flow(flow_id)
            assert flow["status"] == "running"
            cart_step = flow["steps"][0]
            assert cart_step["status"] == "running"
            assert cart_step["run_id"] == "run-1"
            assert cart_step["started_at"] is not None
        finally:
            await store.close()

    async def test_complete_step(self, tmp_path: Path):
        store = await _make_store(tmp_path)
        try:
            tracker = FlowTracker(store)
            flow_id = await tracker.create_flow("test-flow", ["cartographer", "bulwark"])

            # Start and complete first step
            await tracker.start_step(flow_id, "cartographer", "run-1")
            await tracker.complete_step(flow_id, "cartographer")

            flow = await tracker.get_flow(flow_id)
            assert flow["steps"][0]["status"] == "completed"
            assert flow["steps"][0]["finished_at"] is not None
            # Flow should still be running/pending since not all steps done
            assert flow["status"] != "completed"

            # Start and complete second step
            await tracker.start_step(flow_id, "bulwark", "run-2")
            await tracker.complete_step(flow_id, "bulwark")

            flow = await tracker.get_flow(flow_id)
            assert flow["status"] == "completed"
            assert flow["finished_at"] is not None
        finally:
            await store.close()

    async def test_fail_step(self, tmp_path: Path):
        store = await _make_store(tmp_path)
        try:
            tracker = FlowTracker(store)
            flow_id = await tracker.create_flow("test-flow", ["cartographer", "bulwark"])

            await tracker.start_step(flow_id, "cartographer", "run-1")
            await tracker.fail_step(flow_id, "cartographer", "timeout exceeded")

            flow = await tracker.get_flow(flow_id)
            assert flow["steps"][0]["status"] == "failed"
            assert flow["status"] == "failed"
        finally:
            await store.close()

    async def test_list_flows(self, tmp_path: Path):
        store = await _make_store(tmp_path)
        try:
            tracker = FlowTracker(store)
            await tracker.create_flow("flow-a", ["cartographer"])
            await tracker.create_flow("flow-b", ["bulwark"])
            await tracker.create_flow("flow-c", ["crucible"])

            flows = await tracker.list_flows()
            assert len(flows) == 3
            # Flows returned should have basic structure
            names = {f["name"] for f in flows}
            assert names == {"flow-a", "flow-b", "flow-c"}
        finally:
            await store.close()
