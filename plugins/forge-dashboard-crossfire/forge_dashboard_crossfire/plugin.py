"""CrossfirePlugin — reads Crossfire artifact directories from disk and exposes
them via the ForgePlugin interface for the Forge Dashboard.

Crossfire is a dual-model adversarial engine (Claude CLI + Codex CLI).
Unlike other plugins, it uses ``work_dir`` instead of ``repo_root`` and
reads artifacts from ``work_dir / "artifacts" / {run_id} / {spec,review}``.

Crossfire 3.6+ outputs artifacts to ``artifacts/{run_id}/`` subdirectories
where run_id is a per-run directory name (e.g. a timestamp or UUID).
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncIterator

from forge_dashboard.plugin_sdk.models import (
    Artifact,
    ComponentEvent,
    HealthStatus,
    RunDetail,
    RunSummary,
    StageDefinition,
    StageRecord,
)

# Crossfire stages
_CROSSFIRE_STAGES = [
    "SPEC_CLAUDE",
    "SPEC_CODEX",
    "REVIEW_CLAUDE",
    "REVIEW_CODEX",
    "SYNTHESIS",
]


class CrossfirePlugin:
    """Forge Dashboard plugin for Crossfire adversarial review sessions."""

    name: str = "crossfire"
    display_name: str = "Crossfire"
    version: str = "0.1.0"
    stages: list[StageDefinition] = [
        StageDefinition(name=s, order=i) for i, s in enumerate(_CROSSFIRE_STAGES)
    ]

    def __init__(self, work_dir: Path | None = None) -> None:
        self._work_dir = Path(work_dir) if work_dir else Path(".")
        self._artifacts_dir = self._work_dir / "artifacts"
        self._last_poll_time: float = 0.0

    # ── helpers ───────────────────────────────────────────────────────────

    def _list_run_dirs(self) -> list[str]:
        """Return all subdirectory names of artifacts_dir as run_ids (sorted by name)."""
        if not self._artifacts_dir.is_dir():
            return []
        return sorted(
            d.name for d in self._artifacts_dir.iterdir() if d.is_dir()
        )

    def _spec_dir(self, run_id: str) -> Path:
        return self._artifacts_dir / run_id / "spec"

    def _review_dir(self, run_id: str) -> Path:
        return self._artifacts_dir / run_id / "review"

    def _has_artifacts(self) -> bool:
        return bool(self._list_run_dirs())

    def _collect_files(self, directory: Path) -> list[Path]:
        """Return all files in a directory (non-recursive)."""
        if not directory.is_dir():
            return []
        return sorted(f for f in directory.iterdir() if f.is_file())

    def _infer_status(self, run_id: str) -> str:
        """Infer the overall run status from artifact directories."""
        spec_dir = self._spec_dir(run_id)
        review_dir = self._review_dir(run_id)
        has_spec = spec_dir.is_dir() and any(spec_dir.iterdir()) if spec_dir.is_dir() else False
        has_review = review_dir.is_dir() and any(review_dir.iterdir()) if review_dir.is_dir() else False
        if has_review:
            return "complete"
        elif has_spec:
            return "running"
        else:
            return "pending"

    def _infer_current_stage(self, run_id: str) -> str:
        """Infer the current stage from what artifacts exist."""
        spec_dir = self._spec_dir(run_id)
        review_dir = self._review_dir(run_id)
        has_review = review_dir.is_dir() and any(review_dir.iterdir()) if review_dir.is_dir() else False
        has_spec = spec_dir.is_dir() and any(spec_dir.iterdir()) if spec_dir.is_dir() else False
        if has_review:
            return "SYNTHESIS"
        elif has_spec:
            return "REVIEW_CLAUDE"
        else:
            return "SPEC_CLAUDE"

    def _build_summary(self, run_id: str) -> RunSummary:
        status = self._infer_status(run_id)
        current_stage = self._infer_current_stage(run_id)
        try:
            stage_idx = _CROSSFIRE_STAGES.index(current_stage)
        except ValueError:
            stage_idx = 0
        if status == "complete":
            progress = 1.0
        else:
            progress = stage_idx / len(_CROSSFIRE_STAGES)
        return RunSummary(
            component=self.name,
            run_id=run_id,
            status=status,
            current_stage=current_stage,
            progress=progress,
            started_at="",
            finished_at="",
        )

    # ── ForgePlugin interface ─────────────────────────────────────────────

    async def list_runs(
        self,
        limit: int = 20,
        offset: int = 0,
        status_filter: str | None = None,
    ) -> list[RunSummary]:
        run_ids = self._list_run_dirs()
        if not run_ids:
            return []
        summaries: list[RunSummary] = []
        for run_id in run_ids:
            summary = self._build_summary(run_id)
            if status_filter and summary.status != status_filter:
                continue
            summaries.append(summary)
        return summaries[offset : offset + limit]

    async def get_run(self, run_id: str) -> RunDetail:
        summary = self._build_summary(run_id)
        current_stage = summary.current_stage
        try:
            current_idx = _CROSSFIRE_STAGES.index(current_stage)
        except ValueError:
            current_idx = 0
        status = summary.status

        stage_records: list[StageRecord] = []
        for i, stage_name in enumerate(_CROSSFIRE_STAGES):
            if status == "complete":
                s_status = "complete"
            elif i < current_idx:
                s_status = "complete"
            elif i == current_idx:
                s_status = "running"
            else:
                s_status = "pending"
            stage_records.append(StageRecord(name=stage_name, status=s_status))

        artifacts = await self.get_artifacts(run_id)

        return RunDetail(
            component=summary.component,
            run_id=summary.run_id,
            status=summary.status,
            current_stage=summary.current_stage,
            progress=summary.progress,
            started_at=summary.started_at,
            finished_at=summary.finished_at,
            stages=stage_records,
            artifacts=artifacts,
        )

    async def get_artifacts(self, run_id: str) -> list[Artifact]:
        artifacts: list[Artifact] = []
        for directory, art_type in [
            (self._spec_dir(run_id), "spec"),
            (self._review_dir(run_id), "review"),
        ]:
            for f in self._collect_files(directory):
                artifacts.append(
                    Artifact(
                        name=f.name,
                        artifact_type=art_type,
                        content_or_path=str(f),
                        size=f.stat().st_size,
                    )
                )
        return artifacts

    async def poll_events(
        self, since: str | None = None,
    ) -> list[ComponentEvent]:
        events: list[ComponentEvent] = []
        if not self._artifacts_dir.is_dir():
            return events
        cutoff = self._last_poll_time
        now = time.time()
        for run_id in self._list_run_dirs():
            for sub in [self._spec_dir(run_id), self._review_dir(run_id)]:
                if not sub.is_dir():
                    continue
                for f in sub.iterdir():
                    if not f.is_file():
                        continue
                    mtime = f.stat().st_mtime
                    if mtime <= cutoff:
                        continue
                    events.append(
                        ComponentEvent(
                            component=self.name,
                            event_type="artifact_created",
                            run_id=run_id,
                            timestamp=datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat(),
                            data={"file": f.name, "type": sub.name},
                        )
                    )
        self._last_poll_time = now
        return events

    async def subscribe(self) -> AsyncIterator[ComponentEvent] | None:
        # MVP: no live streaming; would use EventEmitter in full version
        return None

    async def trigger(self, params: dict) -> str:
        raise NotImplementedError("CrossfirePlugin.trigger() is not yet implemented")

    async def cancel(self, run_id: str) -> bool:
        raise NotImplementedError("CrossfirePlugin.cancel() is not yet implemented")

    async def retry(self, run_id: str) -> str:
        raise NotImplementedError("CrossfirePlugin.retry() is not yet implemented")

    async def get_config(self) -> dict:
        return {}

    async def update_config(self, patch: dict) -> None:
        pass

    async def health(self) -> HealthStatus:
        ok = self._work_dir.is_dir()
        return HealthStatus(
            component=self.name,
            status="healthy" if ok else "unavailable",
            version=self.version,
            details={"work_dir": str(self._work_dir), "exists": ok},
        )
