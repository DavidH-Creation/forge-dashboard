"""Tests for CrossfirePlugin."""

from __future__ import annotations

from pathlib import Path

import pytest

from forge_dashboard_crossfire.plugin import CrossfirePlugin
from forge_dashboard.plugin_sdk.protocol import ForgePlugin


# ── Test helpers ─────────────────────────────────────────────────────────────


def _write_crossfire_artifacts(work_dir: Path) -> None:
    """Create realistic Crossfire spec and review artifact files."""
    spec_dir = work_dir / "artifacts" / "spec"
    review_dir = work_dir / "artifacts" / "review"
    spec_dir.mkdir(parents=True, exist_ok=True)
    review_dir.mkdir(parents=True, exist_ok=True)

    (spec_dir / "claude_spec.md").write_text(
        "# Claude Spec\nAdversarial specification from Claude.",
        encoding="utf-8",
    )
    (spec_dir / "codex_spec.md").write_text(
        "# Codex Spec\nAdversarial specification from Codex.",
        encoding="utf-8",
    )
    (review_dir / "claude_review.md").write_text(
        "# Claude Review\nReview findings from Claude.",
        encoding="utf-8",
    )
    (review_dir / "codex_review.md").write_text(
        "# Codex Review\nReview findings from Codex.",
        encoding="utf-8",
    )
    (review_dir / "synthesis.md").write_text(
        "# Synthesis\nCombined adversarial review results.",
        encoding="utf-8",
    )


# ── Tests ────────────────────────────────────────────────────────────────────


class TestCrossfirePlugin:
    async def test_list_runs_empty(self, tmp_path: Path):
        plugin = CrossfirePlugin(work_dir=tmp_path)
        runs = await plugin.list_runs()
        assert runs == []

    async def test_list_runs_with_artifacts(self, tmp_path: Path):
        _write_crossfire_artifacts(tmp_path)
        plugin = CrossfirePlugin(work_dir=tmp_path)
        runs = await plugin.list_runs()
        assert len(runs) == 1
        assert runs[0].component == "crossfire"
        assert runs[0].run_id == "current"
        assert runs[0].status == "complete"

    async def test_get_artifacts(self, tmp_path: Path):
        _write_crossfire_artifacts(tmp_path)
        plugin = CrossfirePlugin(work_dir=tmp_path)
        artifacts = await plugin.get_artifacts("current")
        assert len(artifacts) == 5
        spec_arts = [a for a in artifacts if a.artifact_type == "spec"]
        review_arts = [a for a in artifacts if a.artifact_type == "review"]
        assert len(spec_arts) == 2
        assert len(review_arts) == 3
        for a in artifacts:
            assert a.size is not None
            assert a.size > 0

    async def test_get_run_detail(self, tmp_path: Path):
        _write_crossfire_artifacts(tmp_path)
        plugin = CrossfirePlugin(work_dir=tmp_path)
        detail = await plugin.get_run("current")
        assert detail.run_id == "current"
        assert detail.status == "complete"
        assert len(detail.stages) == 5
        for stage in detail.stages:
            assert stage.status == "complete"
        assert len(detail.artifacts) == 5

    async def test_health_available(self, tmp_path: Path):
        plugin = CrossfirePlugin(work_dir=tmp_path)
        h = await plugin.health()
        assert h.component == "crossfire"
        assert h.status == "healthy"

    async def test_health_unavailable(self):
        plugin = CrossfirePlugin(work_dir=Path("/nonexistent/path/crossfire"))
        h = await plugin.health()
        assert h.status == "unavailable"

    async def test_subscribe_returns_none(self, tmp_path: Path):
        plugin = CrossfirePlugin(work_dir=tmp_path)
        result = await plugin.subscribe()
        assert result is None

    def test_stages_defined(self):
        plugin = CrossfirePlugin()
        assert len(plugin.stages) == 5
        assert plugin.stages[0].name == "SPEC_CLAUDE"
        assert plugin.stages[4].name == "SYNTHESIS"

    async def test_poll_events(self, tmp_path: Path):
        plugin = CrossfirePlugin(work_dir=tmp_path)
        # No artifacts yet
        events = await plugin.poll_events()
        assert events == []
        # Add artifacts
        _write_crossfire_artifacts(tmp_path)
        events = await plugin.poll_events()
        assert len(events) == 5  # 2 spec + 3 review files
        for e in events:
            assert e.component == "crossfire"
            assert e.event_type == "artifact_created"
        # Poll again — no new events
        events = await plugin.poll_events()
        assert events == []

    def test_satisfies_protocol(self, tmp_path: Path):
        plugin = CrossfirePlugin(work_dir=tmp_path)
        assert isinstance(plugin, ForgePlugin)
