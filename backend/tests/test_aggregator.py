"""Tests for Aggregator — overview service that collects health + runs from all plugins."""

import pytest

from forge_dashboard.services.aggregator import Aggregator
from forge_dashboard.plugin_sdk.registry import PluginRegistry
from forge_dashboard.plugin_sdk.models import HealthStatus, RunSummary


class FakeOverviewPlugin:
    """Plugin that provides health and list_runs for aggregator tests."""

    name = "bulwark"
    display_name = "Bulwark"
    version = "4.0.0"
    stages = []

    async def health(self):
        return HealthStatus(component="bulwark", status="healthy", version="4.0.0")

    async def list_runs(self, limit=20, offset=0, status_filter=None):
        return [
            RunSummary(
                component="bulwark",
                run_id="r1",
                status="complete",
                current_stage="REVIEW",
                progress=1.0,
            )
        ]

    async def get_run(self, run_id):
        ...

    async def get_artifacts(self, run_id):
        return []

    async def poll_events(self, since=None):
        return []

    async def subscribe(self):
        return None

    async def trigger(self, params):
        return "run-1"

    async def cancel(self, run_id):
        return True

    async def retry(self, run_id):
        return "run-2"

    async def get_config(self):
        return {}

    async def update_config(self, patch):
        ...


class TestAggregator:
    async def test_overview(self):
        """get_overview should return health and recent runs for all plugins."""
        registry = PluginRegistry()
        registry.register(FakeOverviewPlugin())
        agg = Aggregator(registry=registry)
        overview = await agg.get_overview()

        assert "components" in overview
        assert len(overview["components"]) == 1

        comp = overview["components"][0]
        assert comp["name"] == "bulwark"
        assert comp["health"]["status"] == "healthy"
        assert comp["health"]["version"] == "4.0.0"
        assert comp["recent_runs"] == 1
        assert len(comp["latest_runs"]) == 1
        assert comp["latest_runs"][0]["run_id"] == "r1"

    async def test_overview_degraded_plugin(self):
        """get_overview should handle plugins whose health() raises."""
        registry = PluginRegistry()
        plugin = FakeOverviewPlugin()

        async def broken_health():
            raise RuntimeError("down")

        plugin.health = broken_health
        registry.register(plugin)

        agg = Aggregator(registry=registry)
        overview = await agg.get_overview()

        comp = overview["components"][0]
        assert comp["health"]["status"] == "degraded"
        assert comp["health"]["component"] == "bulwark"

    async def test_overview_plugin_list_runs_fails(self):
        """get_overview should handle plugins whose list_runs() raises."""
        registry = PluginRegistry()
        plugin = FakeOverviewPlugin()

        async def broken_list_runs(limit=20, offset=0, status_filter=None):
            raise RuntimeError("no runs")

        plugin.list_runs = broken_list_runs
        registry.register(plugin)

        agg = Aggregator(registry=registry)
        overview = await agg.get_overview()

        comp = overview["components"][0]
        # Health should still be present
        assert comp["health"]["status"] == "healthy"
        # But runs should fall back gracefully
        assert comp["recent_runs"] == 0
        assert comp["latest_runs"] == []

    async def test_overview_multiple_plugins(self):
        """get_overview should aggregate data from all registered plugins."""
        registry = PluginRegistry()

        plugin_a = FakeOverviewPlugin()
        plugin_a.name = "bulwark"
        registry.register(plugin_a)

        plugin_b = FakeOverviewPlugin()
        plugin_b.name = "cartographer"
        registry.register(plugin_b)

        agg = Aggregator(registry=registry)
        overview = await agg.get_overview()

        assert len(overview["components"]) == 2
        names = {c["name"] for c in overview["components"]}
        assert names == {"bulwark", "cartographer"}

    async def test_overview_includes_registry_status(self):
        """get_overview should include the registry status for each plugin."""
        registry = PluginRegistry()
        plugin = FakeOverviewPlugin()
        registry.register(plugin)
        registry._mark_degraded("bulwark", error="flaky")

        agg = Aggregator(registry=registry)
        overview = await agg.get_overview()

        comp = overview["components"][0]
        assert comp["status"] == "degraded"

    async def test_overview_empty_registry(self):
        """get_overview with no plugins returns empty components list."""
        registry = PluginRegistry()
        agg = Aggregator(registry=registry)
        overview = await agg.get_overview()

        assert overview == {"components": []}
