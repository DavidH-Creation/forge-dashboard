"""CruciblePlugin — reads Crucible run manifests from disk and exposes them
via the ForgePlugin interface for the Forge Dashboard.

Crucible is a structured thinking engine with 8 stages.
Data directory: ``repo_root / ".crucible" / "runs"``
Manifest layout: ``{run_id}/manifest.json``
"""

from __future__ import annotations

import json
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

# The eight Crucible stages in execution order
_CRUCIBLE_STAGES = [
    "intake_dock",
    "thought_clarifier",
    "idea_expander",
    "perspective_collider",
    "scenario_tree",
    "thesis_distiller",
    "system_mapping",
    "system_aware_refutation",
]


class CruciblePlugin:
    """Forge Dashboard plugin for Crucible structured thinking runs."""

    name: str = "crucible"
    display_name: str = "Crucible"
    version: str = "0.1.0"
    stages: list[StageDefinition] = [
        StageDefinition(name=s, order=i) for i, s in enumerate(_CRUCIBLE_STAGES)
    ]

    def __init__(self, repo_root: Path | None = None) -> None:
        self._repo_root = Path(repo_root) if repo_root else Path(".")
        self._data_dir = self._repo_root / ".crucible" / "runs"
        self._last_poll_time: float = 0.0

    # ── helpers ───────────────────────────────────────────────────────────

    def _manifest_path(self, run_id: str) -> Path:
        return self._data_dir / run_id / "manifest.json"

    def _read_manifest(self, run_id: str) -> dict:
        path = self._manifest_path(run_id)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _manifest_to_summary(self, data: dict) -> RunSummary:
        stage_runs = data.get("stage_runs", [])
        completed = sum(
            1 for sr in stage_runs if sr.get("status") in ("complete", "done")
        )
        total = len(_CRUCIBLE_STAGES)
        status = data.get("status", "unknown")
        if status in ("complete", "done"):
            progress = 1.0
        else:
            progress = completed / total if total else 0.0
        return RunSummary(
            component=self.name,
            run_id=data["run_id"],
            status=status,
            current_stage=data.get("current_stage", ""),
            progress=progress,
            started_at=data.get("started_at", ""),
            finished_at=data.get("finished_at", ""),
        )

    def _manifest_to_detail(self, data: dict) -> RunDetail:
        summary = self._manifest_to_summary(data)
        stage_runs = data.get("stage_runs", [])

        # Build a lookup of stage_name -> stage run data
        stage_lookup: dict[str, dict] = {}
        for sr in stage_runs:
            stage_lookup[sr.get("stage_name", "")] = sr

        stage_records: list[StageRecord] = []
        for stage_name in _CRUCIBLE_STAGES:
            sr = stage_lookup.get(stage_name, {})
            stage_records.append(
                StageRecord(
                    name=stage_name,
                    status=sr.get("status", "pending"),
                    started_at=sr.get("started_at", ""),
                    finished_at=sr.get("ended_at", ""),
                )
            )

        return RunDetail(
            component=summary.component,
            run_id=summary.run_id,
            status=summary.status,
            current_stage=summary.current_stage,
            progress=summary.progress,
            started_at=summary.started_at,
            finished_at=summary.finished_at,
            stages=stage_records,
        )

    # ── ForgePlugin interface ─────────────────────────────────────────────

    async def list_runs(
        self,
        limit: int = 20,
        offset: int = 0,
        status_filter: str | None = None,
    ) -> list[RunSummary]:
        if not self._data_dir.is_dir():
            return []
        summaries: list[RunSummary] = []
        for entry in sorted(self._data_dir.iterdir()):
            manifest = entry / "manifest.json"
            if not manifest.is_file():
                continue
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            s = self._manifest_to_summary(data)
            if status_filter and s.status != status_filter:
                continue
            summaries.append(s)
        return summaries[offset : offset + limit]

    async def get_run(self, run_id: str) -> RunDetail:
        data = self._read_manifest(run_id)
        return self._manifest_to_detail(data)

    async def get_artifacts(self, run_id: str) -> list[Artifact]:
        data = self._read_manifest(run_id)
        artifacts: list[Artifact] = []
        for art in data.get("artifacts", []):
            artifacts.append(
                Artifact(
                    name=art.get("name", "unknown"),
                    artifact_type=art.get("type", "file"),
                    content_or_path=art.get("path", ""),
                )
            )
        return artifacts

    async def poll_events(
        self, since: str | None = None,
    ) -> list[ComponentEvent]:
        events: list[ComponentEvent] = []
        if not self._data_dir.is_dir():
            return events
        cutoff = self._last_poll_time
        now = time.time()
        for entry in self._data_dir.iterdir():
            manifest = entry / "manifest.json"
            if not manifest.is_file():
                continue
            mtime = manifest.stat().st_mtime
            if mtime <= cutoff:
                continue
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            # Crucible generates retroactive events for each completed stage
            for sr in data.get("stage_runs", []):
                if sr.get("status") in ("complete", "done"):
                    events.append(
                        ComponentEvent(
                            component=self.name,
                            event_type="stage_completed",
                            run_id=data.get("run_id", entry.name),
                            timestamp=sr.get("ended_at", ""),
                            data={
                                "stage": sr.get("stage_name", ""),
                                "status": sr.get("status", ""),
                            },
                            is_retroactive=True,
                        )
                    )
        self._last_poll_time = now
        return events

    async def subscribe(self) -> AsyncIterator[ComponentEvent] | None:
        return None

    async def trigger(self, params: dict) -> str:
        raise NotImplementedError("CruciblePlugin.trigger() is not yet implemented")

    async def cancel(self, run_id: str) -> bool:
        raise NotImplementedError("CruciblePlugin.cancel() is not yet implemented")

    async def retry(self, run_id: str) -> str:
        raise NotImplementedError("CruciblePlugin.retry() is not yet implemented")

    async def get_config(self) -> dict:
        return {}

    async def update_config(self, patch: dict) -> None:
        pass

    async def health(self) -> HealthStatus:
        ok = self._data_dir.is_dir()
        return HealthStatus(
            component=self.name,
            status="healthy" if ok else "unavailable",
            version=self.version,
            details={"data_dir": str(self._data_dir), "exists": ok},
        )
