"""ForgePlugin Protocol — the contract every component plugin must satisfy."""

from __future__ import annotations

from typing import AsyncIterator, Protocol, runtime_checkable

from forge_dashboard.plugin_sdk.models import (
    Artifact,
    ComponentEvent,
    HealthStatus,
    RunDetail,
    RunSummary,
    StageDefinition,
)


@runtime_checkable
class ForgePlugin(Protocol):
    """Runtime-checkable protocol that every Forge component plugin implements.

    Plugins expose a uniform interface so the dashboard can list runs,
    stream events, trigger/cancel operations, and check health regardless
    of the underlying component (Bulwark, Cartographer, Crucible, etc.).
    """

    name: str
    display_name: str
    version: str
    stages: list[StageDefinition]

    async def list_runs(
        self,
        limit: int = 20,
        offset: int = 0,
        status_filter: str | None = None,
    ) -> list[RunSummary]: ...

    async def get_run(self, run_id: str) -> RunDetail: ...

    async def get_artifacts(self, run_id: str) -> list[Artifact]: ...

    async def poll_events(
        self, since: str | None = None
    ) -> list[ComponentEvent]: ...

    async def subscribe(self) -> AsyncIterator[ComponentEvent] | None: ...

    async def trigger(self, params: dict) -> str: ...

    async def cancel(self, run_id: str) -> bool: ...

    async def retry(self, run_id: str) -> str: ...

    async def get_config(self) -> dict: ...

    async def update_config(self, patch: dict) -> None: ...

    async def health(self) -> HealthStatus: ...
