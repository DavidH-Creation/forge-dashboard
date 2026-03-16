"""CartographerPlugin — reads Cartographer run manifests from disk and exposes
them via the ForgePlugin interface for the Forge Dashboard.

Data directory: ``repo_root / ".cartographer" / "runs"``
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

# The nine Cartographer stages in execution order
_CARTOGRAPHER_STAGES = [
    "INTAKE",
    "DISCOVER",
    "PROPOSE",
    "CRITIQUE",
    "REVISE",
    "APPROVE",
    "COMPILE",
    "HANDOFF",
    "LEARN",
]


class CartographerPlugin:
    """Forge Dashboard plugin for Cartographer planning runs."""

    name: str = "cartographer"
    display_name: str = "Cartographer"
    version: str = "0.1.0"
    stages: list[StageDefinition] = [
        StageDefinition(name=s, order=i) for i, s in enumerate(_CARTOGRAPHER_STAGES)
    ]

    def __init__(self, repo_root: Path) -> None:
        self._repo_root = Path(repo_root)
        self._data_dir = self._repo_root / ".cartographer" / "runs"
        self._last_poll_time: float = 0.0

    # ── helpers ───────────────────────────────────────────────────────────

    def _manifest_path(self, run_id: str) -> Path:
        return self._data_dir / run_id / "manifest.json"

    def _read_manifest(self, run_id: str) -> dict:
        path = self._manifest_path(run_id)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _stage_index(stage_name: str) -> int:
        """Return 0-based index of a stage, or 0 if not found."""
        try:
            return _CARTOGRAPHER_STAGES.index(stage_name)
        except ValueError:
            return 0

    def _manifest_to_summary(self, data: dict) -> RunSummary:
        current = data.get("current_stage", "")
        idx = self._stage_index(current)
        # If the run is complete, progress is 1.0
        status = data.get("status", "unknown")
        if status in ("complete", "done"):
            progress = 1.0
        else:
            progress = idx / len(_CARTOGRAPHER_STAGES) if _CARTOGRAPHER_STAGES else 0.0
        return RunSummary(
            component=self.name,
            run_id=data["run_id"],
            status=status,
            current_stage=current,
            progress=progress,
            started_at=data.get("started_at", ""),
            finished_at=data.get("finished_at", ""),
        )

    def _manifest_to_detail(self, data: dict) -> RunDetail:
        summary = self._manifest_to_summary(data)
        current = data.get("current_stage", "")
        current_idx = self._stage_index(current)
        status = data.get("status", "unknown")

        stage_records: list[StageRecord] = []
        for i, stage_name in enumerate(_CARTOGRAPHER_STAGES):
            if status in ("complete", "done"):
                s_status = "complete"
            elif i < current_idx:
                s_status = "complete"
            elif i == current_idx:
                s_status = "running"
            else:
                s_status = "pending"
            stage_records.append(
                StageRecord(name=stage_name, status=s_status)
            )

        artifacts_dict = data.get("artifacts", {})
        artifacts: list[Artifact] = []
        for art_name, art_path in artifacts_dict.items():
            artifacts.append(
                Artifact(
                    name=art_name,
                    artifact_type="file",
                    content_or_path=str(art_path),
                )
            )

        metadata: dict = {}
        if data.get("provenance"):
            metadata["provenance"] = data["provenance"]

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
            metadata=metadata,
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
        for art_name, art_path in data.get("artifacts", {}).items():
            artifacts.append(
                Artifact(
                    name=art_name,
                    artifact_type="file",
                    content_or_path=str(art_path),
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
            events.append(
                ComponentEvent(
                    component=self.name,
                    event_type="run_updated",
                    run_id=data.get("run_id", entry.name),
                    timestamp=datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat(),
                    data={"status": data.get("status", "unknown")},
                )
            )
        self._last_poll_time = now
        return events

    async def subscribe(self) -> AsyncIterator[ComponentEvent] | None:
        return None

    async def trigger(self, params: dict) -> str:
        raise NotImplementedError("CartographerPlugin.trigger() is not yet implemented")

    async def cancel(self, run_id: str) -> bool:
        raise NotImplementedError("CartographerPlugin.cancel() is not yet implemented")

    async def retry(self, run_id: str) -> str:
        raise NotImplementedError("CartographerPlugin.retry() is not yet implemented")

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
