"""Shared fixtures for Forge Dashboard tests."""

import pytest

from forge_dashboard.plugin_sdk.models import (
    Artifact,
    ComponentEvent,
    HealthStatus,
    RunDetail,
    RunSummary,
)


class MockPlugin:
    """A minimal in-memory plugin that satisfies the ForgePlugin protocol."""

    name = "mock"
    display_name = "Mock Component"
    version = "1.0.0"
    stages = []

    async def health(self):
        return HealthStatus(component="mock", status="healthy", version="1.0.0")

    async def list_runs(self, limit=20, offset=0, status_filter=None):
        return [
            RunSummary(
                component="mock",
                run_id="r1",
                status="complete",
                progress=1.0,
            )
        ]

    async def get_run(self, run_id):
        return RunDetail(
            component="mock",
            run_id=run_id,
            status="complete",
            progress=1.0,
        )

    async def get_artifacts(self, run_id):
        return []

    async def poll_events(self, since=None):
        return []

    async def subscribe(self):
        return None

    async def trigger(self, params):
        return "run-new"

    async def cancel(self, run_id):
        return True

    async def retry(self, run_id):
        return "run-retry"

    async def get_config(self):
        return {"key": "value"}

    async def update_config(self, patch):
        pass


@pytest.fixture
def mock_plugin():
    """Return a fresh MockPlugin instance."""
    return MockPlugin()
