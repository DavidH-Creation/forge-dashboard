"""Tests for CruciblePlugin."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from forge_dashboard_crucible.plugin import CruciblePlugin
from forge_dashboard.plugin_sdk.protocol import ForgePlugin


# ── Test helpers ─────────────────────────────────────────────────────────────


def _write_crucible_manifest(
    repo_root: Path,
    run_id: str,
    status: str = "complete",
    current_stage: str = "system_aware_refutation",
) -> Path:
    """Create a realistic Crucible manifest JSON on disk."""
    runs_dir = repo_root / ".crucible" / "runs" / run_id
    runs_dir.mkdir(parents=True, exist_ok=True)

    all_stages = [
        "intake_dock",
        "thought_clarifier",
        "idea_expander",
        "perspective_collider",
        "scenario_tree",
        "thesis_distiller",
        "system_mapping",
        "system_aware_refutation",
    ]

    stage_runs = []
    for i, stage_name in enumerate(all_stages):
        if status == "complete" or (status == "running" and stage_name != current_stage):
            # If complete run, all stages are complete
            # If running, mark stages before current as complete
            try:
                current_idx = all_stages.index(current_stage)
            except ValueError:
                current_idx = len(all_stages)
            if status == "complete" or i < current_idx:
                stage_runs.append({
                    "stage_name": stage_name,
                    "status": "complete",
                    "started_at": f"2025-03-01T10:{i:02d}:00Z",
                    "ended_at": f"2025-03-01T10:{i:02d}:30Z",
                })
            elif i == current_idx:
                stage_runs.append({
                    "stage_name": stage_name,
                    "status": "running",
                    "started_at": f"2025-03-01T10:{i:02d}:00Z",
                    "ended_at": "",
                })
        # Stages after current are not in stage_runs at all

    manifest = {
        "run_id": run_id,
        "status": status,
        "current_stage": current_stage,
        "started_at": "2025-03-01T10:00:00Z",
        "finished_at": "2025-03-01T10:08:00Z" if status == "complete" else "",
        "stage_runs": stage_runs,
    }
    manifest_path = runs_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest_path


# ── Tests ────────────────────────────────────────────────────────────────────


class TestCruciblePlugin:
    async def test_list_runs_empty(self, tmp_path: Path):
        plugin = CruciblePlugin(repo_root=tmp_path)
        runs = await plugin.list_runs()
        assert runs == []

    async def test_list_runs_found(self, tmp_path: Path):
        _write_crucible_manifest(tmp_path, "crucible-001")
        _write_crucible_manifest(
            tmp_path, "crucible-002",
            status="running",
            current_stage="idea_expander",
        )
        plugin = CruciblePlugin(repo_root=tmp_path)
        runs = await plugin.list_runs()
        assert len(runs) == 2
        ids = {r.run_id for r in runs}
        assert ids == {"crucible-001", "crucible-002"}
        for r in runs:
            assert r.component == "crucible"

    async def test_get_run_detail(self, tmp_path: Path):
        _write_crucible_manifest(tmp_path, "crucible-100")
        plugin = CruciblePlugin(repo_root=tmp_path)
        detail = await plugin.get_run("crucible-100")
        assert detail.run_id == "crucible-100"
        assert detail.status == "complete"
        assert len(detail.stages) == 8
        stage_names = [s.name for s in detail.stages]
        assert stage_names == [
            "intake_dock", "thought_clarifier", "idea_expander",
            "perspective_collider", "scenario_tree", "thesis_distiller",
            "system_mapping", "system_aware_refutation",
        ]
        for stage in detail.stages:
            assert stage.status == "complete"
        assert detail.progress == 1.0

    async def test_poll_events_retroactive(self, tmp_path: Path):
        plugin = CruciblePlugin(repo_root=tmp_path)
        # First poll empty
        events = await plugin.poll_events()
        assert events == []
        # Write a completed manifest (all 8 stages complete)
        _write_crucible_manifest(tmp_path, "crucible-300")
        events = await plugin.poll_events()
        assert len(events) == 8  # One per completed stage
        for e in events:
            assert e.component == "crucible"
            assert e.event_type == "stage_completed"
            assert e.is_retroactive is True
            assert e.run_id == "crucible-300"
        # Poll again — no new events
        events = await plugin.poll_events()
        assert events == []

    async def test_health_available(self, tmp_path: Path):
        (tmp_path / ".crucible" / "runs").mkdir(parents=True)
        plugin = CruciblePlugin(repo_root=tmp_path)
        h = await plugin.health()
        assert h.component == "crucible"
        assert h.status == "healthy"

    async def test_health_unavailable(self, tmp_path: Path):
        plugin = CruciblePlugin(repo_root=tmp_path)
        h = await plugin.health()
        assert h.status == "unavailable"

    async def test_subscribe_returns_none(self, tmp_path: Path):
        plugin = CruciblePlugin(repo_root=tmp_path)
        result = await plugin.subscribe()
        assert result is None

    def test_stages_defined(self):
        plugin = CruciblePlugin(repo_root=Path("."))
        assert len(plugin.stages) == 8
        assert plugin.stages[0].name == "intake_dock"
        assert plugin.stages[7].name == "system_aware_refutation"

    def test_satisfies_protocol(self, tmp_path: Path):
        plugin = CruciblePlugin(repo_root=tmp_path)
        assert isinstance(plugin, ForgePlugin)
