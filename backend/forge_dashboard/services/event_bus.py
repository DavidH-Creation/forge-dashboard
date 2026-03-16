"""EventBus — central event dispatcher that polls plugins and dispatches events."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Callable

from forge_dashboard.plugin_sdk.models import ComponentEvent

if TYPE_CHECKING:
    from forge_dashboard.platform.event_journal import EventJournal
    from forge_dashboard.plugin_sdk.registry import PluginRegistry

logger = logging.getLogger(__name__)


class EventBus:
    """Central event dispatcher.

    Periodically polls all healthy plugins for new events, records them
    in the EventJournal, and dispatches to registered listeners.
    """

    def __init__(
        self,
        registry: PluginRegistry,
        journal: EventJournal,
        poll_interval: float = 2.0,
    ) -> None:
        self._registry = registry
        self._journal = journal
        self._poll_interval = poll_interval
        self._listeners: list[Callable] = []
        self._last_poll_time: str | None = None
        self._task: asyncio.Task | None = None

    # ── Polling ───────────────────────────────────────────────────────────

    async def poll_once(self) -> None:
        """Iterate all healthy plugins, call poll_events(since), record to journal, dispatch to listeners."""
        for name in self._registry.list_plugins():
            if self._registry.get_status(name) != "healthy":
                continue
            plugin = self._registry.get(name)
            try:
                events = await self._registry.safe_call(
                    plugin, "poll_events", since=self._last_poll_time
                )
                for event in events:
                    await self._journal.record(event)
                    self._dispatch(event)
            except Exception:
                pass  # safe_call already marks degraded

        self._last_poll_time = datetime.now(timezone.utc).isoformat()

    def _dispatch(self, event: ComponentEvent) -> None:
        """Send event to all listeners."""
        for listener in list(self._listeners):
            try:
                result = listener(event)
                if asyncio.iscoroutine(result):
                    asyncio.create_task(result)
            except Exception:
                logger.debug("Listener %r failed for event %s", listener, event.event_type, exc_info=True)

    # ── Lifecycle ─────────────────────────────────────────────────────────

    async def start(self) -> None:
        """Start the background poll loop."""
        self._task = asyncio.create_task(self._poll_loop())

    async def _poll_loop(self) -> None:
        """Run poll_once in a loop until cancelled."""
        while True:
            await self.poll_once()
            await asyncio.sleep(self._poll_interval)

    async def stop(self) -> None:
        """Cancel the background poll loop."""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    # ── Listener management ───────────────────────────────────────────────

    def add_listener(self, callback: Callable) -> None:
        """Register a callback to receive dispatched events."""
        self._listeners.append(callback)

    def remove_listener(self, callback: Callable) -> None:
        """Unregister a previously registered callback."""
        self._listeners.remove(callback)
