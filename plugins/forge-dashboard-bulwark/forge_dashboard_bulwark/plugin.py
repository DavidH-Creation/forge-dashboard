"""BulwarkPlugin — reads Bulwark run manifests from disk and exposes them
via the ForgePlugin interface for the Forge Dashboard.

Data directory: ``repo_root / ".bulwark" / "runs"``
Manifest layout: ``{run_id}/manifest.json``
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

# The five Bulwark phases in execution order
_BULWARK_STAGES = ["VALIDATE", "PLAN", "EXECUTE", "CHECK", "REVIEW"]


class BulwarkPlugin:
    """Forge Dashboard plugin for Bulwark task-execution runs."""

    name: str = "bulwark"
    display_name: str = "Bulwark"
    version: str = "0.1.0"
    stages: list[StageDefinition] = [
        StageDefinition(name=s, order=i) for i, s in enumerate(_BULWARK_STAGES)
    ]

    def __init__(self, repo_root: Path | None = None) -> None:
        self._repo_root = Path(repo_root) if repo_root else Path(".")
        self._data_dir = self._repo_root / ".bulwark" / "runs"
        self._last_poll_time: float = 0.0

    # ── helpers ───────────────────────────────────────────────────────────

    def _manifest_path(self, run_id: str) -> Path:
        return self._data_dir / run_id / "manifest.json"

    def _read_manifest(self, run_id: str) -> dict:
        path = self._manifest_path(run_id)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _manifest_to_summary(self, data: dict) -> RunSummary:
        phases = data.get("phases", {})
        completed = sum(
            1 for p in phases.values() if p.get("status") in ("complete", "passed")
        )
        progress = completed / len(_BULWARK_STAGES) if _BULWARK_STAGES else 0.0
        return RunSummary(
            component=self.name,
            run_id=data["run_id"],
            status=data.get("overall_status", "unknown"),
            current_stage=data.get("current_phase", ""),
            progress=progress,
            started_at=data.get("started_at", ""),
            finished_at=data.get("finished_at", ""),
        )

    def _manifest_to_detail(self, data: dict) -> RunDetail:
        summary = self._manifest_to_summary(data)
        phases = data.get("phases", {})
        stage_records: list[StageRecord] = []
        for stage_name in _BULWARK_STAGES:
            phase = phases.get(stage_name, {})
            stage_records.append(
                StageRecord(
                    name=stage_name,
                    status=phase.get("status", "pending"),
                    started_at=phase.get("started_at", ""),
                    finished_at=phase.get("finished_at", ""),
                )
            )
        task_contract = data.get("task_contract", {})
        metadata: dict = {}
        if task_contract:
            metadata["task_contract_name"] = task_contract.get("name", "")
        return RunDetail(
            component=summary.component,
            run_id=summary.run_id,
            status=summary.status,
            current_stage=summary.current_stage,
            progress=summary.progress,
            started_at=summary.started_at,
            finished_at=summary.finished_at,
            stages=stage_records,
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
        # Bulwark manifests may include an artifacts list
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
            events.append(
                ComponentEvent(
                    component=self.name,
                    event_type="run_updated",
                    run_id=data.get("run_id", entry.name),
                    timestamp=datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat(),
                    data={"status": data.get("overall_status", "unknown")},
                )
            )
        self._last_poll_time = now
        return events

    async def subscribe(self) -> AsyncIterator[ComponentEvent] | None:
        return None

    async def trigger(self, params: dict) -> str:
        raise NotImplementedError("BulwarkPlugin.trigger() is not yet implemented")

    async def cancel(self, run_id: str) -> bool:
        raise NotImplementedError("BulwarkPlugin.cancel() is not yet implemented")

    async def retry(self, run_id: str) -> str:
        raise NotImplementedError("BulwarkPlugin.retry() is not yet implemented")

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
