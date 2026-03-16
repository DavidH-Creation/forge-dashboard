"""Aggregator — gathers health + recent runs from all registered plugins."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from forge_dashboard.plugin_sdk.registry import PluginRegistry

logger = logging.getLogger(__name__)


class Aggregator:
    """Service that collects an overview snapshot from all registered plugins.

    Calls health() and list_runs() on every plugin through the registry's
    safe_call mechanism, so failures are isolated and the overview degrades
    gracefully.
    """

    def __init__(self, registry: PluginRegistry) -> None:
        self._registry = registry

    async def get_overview(self) -> dict:
        """Gather health + recent runs from all plugins."""
        components: list[dict] = []

        for name in self._registry.list_plugins():
            plugin = self._registry.get(name)
            entry: dict = {
                "name": name,
                "status": self._registry.get_status(name),
            }

            # ── Health ────────────────────────────────────────────────
            try:
                health = await self._registry.safe_call(plugin, "health")
                entry["health"] = health.model_dump()
            except Exception:
                entry["health"] = {"status": "degraded", "component": name}

            # ── Recent runs ───────────────────────────────────────────
            try:
                runs = await self._registry.safe_call(plugin, "list_runs", limit=5)
                entry["recent_runs"] = len(runs)
                entry["latest_runs"] = [r.model_dump() for r in runs[:3]]
            except Exception:
                entry["recent_runs"] = 0
                entry["latest_runs"] = []

            components.append(entry)

        return {"components": components}
