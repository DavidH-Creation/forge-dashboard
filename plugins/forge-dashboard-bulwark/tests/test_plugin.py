"""Tests for BulwarkPlugin."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from forge_dashboard_bulwark.plugin import BulwarkPlugin
from forge_dashboard.plugin_sdk.protocol import ForgePlugin


# ── Test helpers ─────────────────────────────────────────────────────────────


def _write_bulwark_manifest(
    repo_root: Path,
    run_id: str,
    status: str = "complete",
    current_phase: str = "REVIEW",
) -> Path:
    """Create a realistic Bulwark manifest JSON on disk."""
    runs_dir = repo_root / ".bulwark" / "runs" / run_id
    runs_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_id": run_id,
        "overall_status": status,
        "current_phase": current_phase,
        "started_at": "2025-01-15T10:00:00Z",
        "finished_at": "2025-01-15T10:05:00Z" if status == "complete" else "",
        "task_contract": {"name": "implement-feature-x"},
        "phases": {
            "VALIDATE": {
                "status": "complete",
                "started_at": "2025-01-15T10:00:00Z",
                "finished_at": "2025-01-15T10:00:30Z",
                "attempt": 1,
            },
            "PLAN": {
                "status": "complete",
                "started_at": "2025-01-15T10:00:30Z",
                "finished_at": "2025-01-15T10:01:00Z",
                "attempt": 1,
            },
            "EXECUTE": {
                "status": "complete",
                "started_at": "2025-01-15T10:01:00Z",
                "finished_at": "2025-01-15T10:03:00Z",
                "attempt": 1,
            },
            "CHECK": {
                "status": "complete",
                "started_at": "2025-01-15T10:03:00Z",
                "finished_at": "2025-01-15T10:04:00Z",
                "attempt": 1,
            },
            "REVIEW": {
                "status": "complete" if status == "complete" else "running",
                "started_at": "2025-01-15T10:04:00Z",
                "finished_at": "2025-01-15T10:05:00Z" if status == "complete" else "",
                "attempt": 1,
            },
        },
    }
    manifest_path = runs_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest_path


# ── Tests ────────────────────────────────────────────────────────────────────


class TestBulwarkPlugin:
    async def test_list_runs_empty(self, tmp_path: Path):
        plugin = BulwarkPlugin(repo_root=tmp_path)
        runs = await plugin.list_runs()
        assert runs == []

    async def test_list_runs_found(self, tmp_path: Path):
        _write_bulwark_manifest(tmp_path, "run-001")
        _write_bulwark_manifest(tmp_path, "run-002", status="running", current_phase="EXECUTE")
        plugin = BulwarkPlugin(repo_root=tmp_path)
        runs = await plugin.list_runs()
        assert len(runs) == 2
        ids = {r.run_id for r in runs}
        assert ids == {"run-001", "run-002"}
        for r in runs:
            assert r.component == "bulwark"

    async def test_get_run_detail(self, tmp_path: Path):
        _write_bulwark_manifest(tmp_path, "run-100")
        plugin = BulwarkPlugin(repo_root=tmp_path)
        detail = await plugin.get_run(run_id="run-100")
        assert detail.run_id == "run-100"
        assert detail.status == "complete"
        assert len(detail.stages) == 5
        stage_names = [s.name for s in detail.stages]
        assert stage_names == ["VALIDATE", "PLAN", "EXECUTE", "CHECK", "REVIEW"]
        for stage in detail.stages:
            assert stage.status == "complete"
        assert detail.metadata.get("task_contract_name") == "implement-feature-x"
        assert detail.progress == 1.0

    async def test_poll_events(self, tmp_path: Path):
        plugin = BulwarkPlugin(repo_root=tmp_path)
        # First poll with no data
        events = await plugin.poll_events()
        assert events == []
        # Write a manifest and poll again
        _write_bulwark_manifest(tmp_path, "run-200")
        events = await plugin.poll_events()
        assert len(events) == 1
        assert events[0].component == "bulwark"
        assert events[0].event_type == "run_updated"
        assert events[0].run_id == "run-200"
        # Poll again without changes — no new events
        events = await plugin.poll_events()
        assert events == []

    async def test_health_available(self, tmp_path: Path):
        (tmp_path / ".bulwark" / "runs").mkdir(parents=True)
        plugin = BulwarkPlugin(repo_root=tmp_path)
        h = await plugin.health()
        assert h.component == "bulwark"
        assert h.status == "healthy"

    async def test_health_unavailable(self, tmp_path: Path):
        plugin = BulwarkPlugin(repo_root=tmp_path)
        h = await plugin.health()
        assert h.status == "unavailable"

    async def test_subscribe_returns_none(self, tmp_path: Path):
        plugin = BulwarkPlugin(repo_root=tmp_path)
        result = await plugin.subscribe()
        assert result is None

    def test_stages_defined(self):
        plugin = BulwarkPlugin(repo_root=Path("."))
        assert len(plugin.stages) == 5
        assert plugin.stages[0].name == "VALIDATE"
        assert plugin.stages[4].name == "REVIEW"

    def test_satisfies_protocol(self, tmp_path: Path):
        plugin = BulwarkPlugin(repo_root=tmp_path)
        assert isinstance(plugin, ForgePlugin)
