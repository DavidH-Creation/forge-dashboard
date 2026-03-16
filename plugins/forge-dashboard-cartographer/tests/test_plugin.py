"""Tests for CartographerPlugin."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from forge_dashboard_cartographer.plugin import CartographerPlugin
from forge_dashboard.plugin_sdk.protocol import ForgePlugin


# ── Test helpers ─────────────────────────────────────────────────────────────


def _write_carto_manifest(
    repo_root: Path,
    run_id: str,
    stage: str = "HANDOFF",
    status: str = "running",
) -> Path:
    """Create a realistic Cartographer manifest JSON on disk."""
    runs_dir = repo_root / ".cartographer" / "runs" / run_id
    runs_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_id": run_id,
        "status": status,
        "current_stage": stage,
        "started_at": "2025-02-10T09:00:00Z",
        "finished_at": "2025-02-10T09:30:00Z" if status == "complete" else "",
        "artifacts": {
            "task_contract": "handoff/bulwark_tasks/task-001.yaml",
            "discovery_report": "handoff/discovery.md",
        },
        "provenance": {"adapter": "claude-code-cli", "model": "claude-sonnet-4-20250514"},
    }
    manifest_path = runs_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest_path


# ── Tests ────────────────────────────────────────────────────────────────────


class TestCartographerPlugin:
    async def test_list_runs_empty(self, tmp_path: Path):
        plugin = CartographerPlugin(repo_root=tmp_path)
        runs = await plugin.list_runs()
        assert runs == []

    async def test_list_runs_found(self, tmp_path: Path):
        _write_carto_manifest(tmp_path, "carto-001", stage="COMPILE", status="running")
        _write_carto_manifest(tmp_path, "carto-002", stage="HANDOFF", status="complete")
        plugin = CartographerPlugin(repo_root=tmp_path)
        runs = await plugin.list_runs()
        assert len(runs) == 2
        ids = {r.run_id for r in runs}
        assert ids == {"carto-001", "carto-002"}
        for r in runs:
            assert r.component == "cartographer"

    async def test_get_run_detail(self, tmp_path: Path):
        _write_carto_manifest(tmp_path, "carto-100", stage="PROPOSE", status="running")
        plugin = CartographerPlugin(repo_root=tmp_path)
        detail = await plugin.get_run(run_id="carto-100")
        assert detail.run_id == "carto-100"
        assert detail.status == "running"
        assert len(detail.stages) == 9
        stage_names = [s.name for s in detail.stages]
        assert stage_names == [
            "INTAKE", "DISCOVER", "PROPOSE", "CRITIQUE", "REVISE",
            "APPROVE", "COMPILE", "HANDOFF", "LEARN",
        ]
        # INTAKE and DISCOVER should be complete (before PROPOSE)
        assert detail.stages[0].status == "complete"  # INTAKE
        assert detail.stages[1].status == "complete"  # DISCOVER
        assert detail.stages[2].status == "running"   # PROPOSE (current)
        assert detail.stages[3].status == "pending"   # CRITIQUE
        # Artifacts from manifest
        assert len(detail.artifacts) == 2
        assert detail.metadata.get("provenance") is not None
        # Progress = index of PROPOSE (2) / 9
        assert detail.progress == pytest.approx(2 / 9)

    async def test_get_run_detail_complete(self, tmp_path: Path):
        _write_carto_manifest(tmp_path, "carto-200", stage="LEARN", status="complete")
        plugin = CartographerPlugin(repo_root=tmp_path)
        detail = await plugin.get_run(run_id="carto-200")
        assert detail.progress == 1.0
        for stage in detail.stages:
            assert stage.status == "complete"

    async def test_health_available(self, tmp_path: Path):
        (tmp_path / ".cartographer" / "runs").mkdir(parents=True)
        plugin = CartographerPlugin(repo_root=tmp_path)
        h = await plugin.health()
        assert h.component == "cartographer"
        assert h.status == "healthy"

    async def test_health_unavailable(self, tmp_path: Path):
        plugin = CartographerPlugin(repo_root=tmp_path)
        h = await plugin.health()
        assert h.status == "unavailable"

    def test_stages_defined(self):
        plugin = CartographerPlugin(repo_root=Path("."))
        assert len(plugin.stages) == 9
        assert plugin.stages[0].name == "INTAKE"
        assert plugin.stages[8].name == "LEARN"

    async def test_subscribe_returns_none(self, tmp_path: Path):
        plugin = CartographerPlugin(repo_root=tmp_path)
        result = await plugin.subscribe()
        assert result is None

    def test_satisfies_protocol(self, tmp_path: Path):
        plugin = CartographerPlugin(repo_root=tmp_path)
        assert isinstance(plugin, ForgePlugin)
