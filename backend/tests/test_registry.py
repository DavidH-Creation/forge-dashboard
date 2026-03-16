import asyncio

import pytest
from unittest.mock import AsyncMock

from forge_dashboard.plugin_sdk.registry import PluginRegistry, PluginCallError
from forge_dashboard.plugin_sdk.models import HealthStatus


class FakePlugin:
    name = "fake"
    display_name = "Fake Component"
    version = "0.0.1"
    stages = []

    async def health(self):
        return HealthStatus(component="fake", status="healthy", version="0.0.1")

    async def list_runs(self, limit=20, offset=0, status_filter=None):
        return []

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


class TestPluginRegistry:
    def test_register_and_get(self):
        reg = PluginRegistry()
        plugin = FakePlugin()
        reg.register(plugin)
        assert reg.get("fake") is plugin
        assert "fake" in reg.list_plugins()

    def test_get_unknown_returns_none(self):
        reg = PluginRegistry()
        assert reg.get("nonexistent") is None

    def test_list_plugins_empty(self):
        reg = PluginRegistry()
        assert reg.list_plugins() == []

    def test_register_multiple(self):
        reg = PluginRegistry()
        p1 = FakePlugin()
        p2 = FakePlugin()
        p2.name = "fake2"
        reg.register(p1)
        reg.register(p2)
        assert sorted(reg.list_plugins()) == ["fake", "fake2"]

    def test_initial_status_healthy(self):
        reg = PluginRegistry()
        plugin = FakePlugin()
        reg.register(plugin)
        assert reg.get_status("fake") == "healthy"

    async def test_safe_call_success(self):
        reg = PluginRegistry()
        plugin = FakePlugin()
        reg.register(plugin)
        result = await reg.safe_call(plugin, "list_runs")
        assert result == []

    async def test_safe_call_timeout(self):
        reg = PluginRegistry(call_timeout=0.01)
        plugin = FakePlugin()

        async def slow_list_runs(**kw):
            await asyncio.sleep(10)

        plugin.list_runs = slow_list_runs
        reg.register(plugin)
        with pytest.raises(PluginCallError):
            await reg.safe_call(plugin, "list_runs")
        assert reg.get_status("fake") == "degraded"

    async def test_safe_call_exception_degrades(self):
        reg = PluginRegistry()
        plugin = FakePlugin()
        plugin.list_runs = AsyncMock(side_effect=RuntimeError("boom"))
        reg.register(plugin)
        with pytest.raises(PluginCallError):
            await reg.safe_call(plugin, "list_runs")
        assert reg.get_status("fake") == "degraded"

    async def test_safe_call_error_has_details(self):
        reg = PluginRegistry()
        plugin = FakePlugin()
        plugin.list_runs = AsyncMock(side_effect=ValueError("bad input"))
        reg.register(plugin)
        with pytest.raises(PluginCallError) as exc_info:
            await reg.safe_call(plugin, "list_runs")
        err = exc_info.value
        assert err.plugin_name == "fake"
        assert err.method == "list_runs"
        assert isinstance(err.cause, ValueError)

    async def test_health_recovery(self):
        reg = PluginRegistry()
        plugin = FakePlugin()
        reg.register(plugin)
        reg._mark_degraded("fake", error="test")
        assert reg.get_status("fake") == "degraded"
        await reg.check_health("fake")
        assert reg.get_status("fake") == "healthy"

    async def test_health_check_stays_degraded_on_failure(self):
        reg = PluginRegistry()
        plugin = FakePlugin()
        plugin.health = AsyncMock(
            return_value=HealthStatus(component="fake", status="down", version="0.0.1")
        )
        reg.register(plugin)
        reg._mark_degraded("fake", error="test")
        await reg.check_health("fake")
        # status should not recover if health reports non-healthy
        assert reg.get_status("fake") != "healthy"

    def test_mark_degraded(self):
        reg = PluginRegistry()
        plugin = FakePlugin()
        reg.register(plugin)
        reg._mark_degraded("fake", error="something broke")
        assert reg.get_status("fake") == "degraded"


class TestPluginCallError:
    def test_attributes(self):
        cause = RuntimeError("oops")
        err = PluginCallError("fake", "list_runs", cause)
        assert err.plugin_name == "fake"
        assert err.method == "list_runs"
        assert err.cause is cause

    def test_str(self):
        cause = RuntimeError("oops")
        err = PluginCallError("fake", "list_runs", cause)
        msg = str(err)
        assert "fake" in msg
        assert "list_runs" in msg


class TestForgePluginProtocol:
    """Test that FakePlugin satisfies the ForgePlugin protocol."""

    def test_fake_plugin_is_forge_plugin(self):
        from forge_dashboard.plugin_sdk.protocol import ForgePlugin
        plugin = FakePlugin()
        assert isinstance(plugin, ForgePlugin)
