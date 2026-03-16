"""PluginRegistry — discover, register, and safely invoke component plugins."""

from __future__ import annotations

import asyncio
import importlib.metadata
import logging
from typing import Any

from forge_dashboard.plugin_sdk.models import HealthStatus

logger = logging.getLogger(__name__)


class PluginCallError(Exception):
    """Raised when a plugin method call fails (timeout, exception, etc.)."""

    def __init__(self, plugin_name: str, method: str, cause: BaseException) -> None:
        self.plugin_name = plugin_name
        self.method = method
        self.cause = cause
        super().__init__(
            f"Plugin '{plugin_name}' method '{method}' failed: {cause!r}"
        )


class _PluginEntry:
    """Internal bookkeeping for a registered plugin."""

    __slots__ = ("plugin", "status", "last_error")

    def __init__(self, plugin: Any) -> None:
        self.plugin = plugin
        self.status: str = "healthy"
        self.last_error: str | None = None


class PluginRegistry:
    """Central registry for Forge component plugins.

    Provides:
    - Registration and lookup
    - Health status tracking (healthy / degraded / down)
    - Safe method invocation with timeout and error handling
    - Entry-point-based plugin discovery
    """

    def __init__(
        self,
        call_timeout: float = 30.0,
        recovery_interval: float = 60.0,
    ) -> None:
        self._plugins: dict[str, _PluginEntry] = {}
        self.call_timeout = call_timeout
        self.recovery_interval = recovery_interval

    # ── Registration / lookup ────────────────────────────────────────────

    def register(self, plugin: Any) -> None:
        """Register a plugin instance.  ``plugin.name`` must be set."""
        name: str = plugin.name
        self._plugins[name] = _PluginEntry(plugin)
        logger.info("Registered plugin '%s' (v%s)", name, getattr(plugin, "version", "?"))

    def get(self, name: str) -> Any | None:
        """Return the plugin instance, or *None* if not registered."""
        entry = self._plugins.get(name)
        return entry.plugin if entry else None

    def list_plugins(self) -> list[str]:
        """Return the names of all registered plugins."""
        return list(self._plugins.keys())

    # ── Health status ────────────────────────────────────────────────────

    def get_status(self, name: str) -> str:
        """Return the current health status of a plugin."""
        entry = self._plugins.get(name)
        if entry is None:
            return "unknown"
        return entry.status

    def _mark_degraded(self, name: str, *, error: str) -> None:
        """Mark a plugin as degraded after a failure."""
        entry = self._plugins.get(name)
        if entry is not None:
            entry.status = "degraded"
            entry.last_error = error
            logger.warning("Plugin '%s' marked degraded: %s", name, error)

    def _mark_healthy(self, name: str) -> None:
        """Restore a plugin to healthy status."""
        entry = self._plugins.get(name)
        if entry is not None:
            entry.status = "healthy"
            entry.last_error = None
            logger.info("Plugin '%s' restored to healthy", name)

    # ── Safe invocation ──────────────────────────────────────────────────

    async def safe_call(
        self,
        plugin: Any,
        method: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Invoke *method* on *plugin* with a timeout guard.

        On success the result is returned.  On timeout or exception the
        plugin is marked degraded and a :class:`PluginCallError` is raised.
        """
        name: str = plugin.name
        fn = getattr(plugin, method)
        try:
            return await asyncio.wait_for(fn(*args, **kwargs), timeout=self.call_timeout)
        except asyncio.TimeoutError as exc:
            self._mark_degraded(name, error=f"Timeout calling {method}")
            raise PluginCallError(name, method, exc) from exc
        except Exception as exc:
            self._mark_degraded(name, error=f"{type(exc).__name__}: {exc}")
            raise PluginCallError(name, method, exc) from exc

    # ── Health checks ────────────────────────────────────────────────────

    async def check_health(self, name: str) -> None:
        """Call ``plugin.health()`` and update status accordingly."""
        entry = self._plugins.get(name)
        if entry is None:
            return
        try:
            result: HealthStatus = await asyncio.wait_for(
                entry.plugin.health(), timeout=self.call_timeout
            )
            if result.status == "healthy":
                self._mark_healthy(name)
            else:
                self._mark_degraded(name, error=f"Health reported: {result.status}")
        except Exception as exc:
            self._mark_degraded(name, error=f"Health check failed: {exc!r}")

    # ── Entry-point discovery ────────────────────────────────────────────

    def discover_plugins(self) -> list[str]:
        """Load plugins advertised via the ``forge_dashboard.plugins`` entry-point group.

        Returns the names of newly registered plugins.
        """
        discovered: list[str] = []
        eps = importlib.metadata.entry_points(group="forge_dashboard.plugins")
        for ep in eps:
            if ep.name in self._plugins:
                continue
            try:
                plugin_factory = ep.load()
                plugin = plugin_factory()
                self.register(plugin)
                discovered.append(plugin.name)
            except Exception:
                logger.exception("Failed to load plugin entry-point '%s'", ep.name)
        return discovered
