"""EventJournal — persist and query ComponentEvents in SQLite."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from forge_dashboard.plugin_sdk.models import ComponentEvent

if TYPE_CHECKING:
    from forge_dashboard.platform.state_store import StateStore


class EventJournal:
    """Append-only journal backed by the event_journal table."""

    def __init__(self, store: StateStore, max_replay_events: int = 500) -> None:
        self._store = store
        self._max_replay = max_replay_events

    async def record(self, event: ComponentEvent) -> None:
        """Persist a single event."""
        await self._store.db.execute(
            "INSERT INTO event_journal (component, event_type, run_id, timestamp, data) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                event.component,
                event.event_type,
                event.run_id,
                event.timestamp,
                json.dumps(event.data),
            ),
        )
        await self._store.db.commit()

    async def query(
        self,
        since: str | None = None,
        limit: int = 100,
        component: str | None = None,
    ) -> list[ComponentEvent]:
        """Query events with optional time and component filters."""
        clauses: list[str] = []
        params: list[str | int] = []

        if since is not None:
            clauses.append("timestamp > ?")
            params.append(since)
        if component is not None:
            clauses.append("component = ?")
            params.append(component)

        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        sql = f"SELECT component, event_type, run_id, timestamp, data FROM event_journal{where} ORDER BY timestamp ASC LIMIT ?"
        params.append(limit)

        cursor = await self._store.db.execute(sql, params)
        rows = await cursor.fetchall()
        return [
            ComponentEvent(
                component=row[0],
                event_type=row[1],
                run_id=row[2],
                timestamp=row[3],
                data=json.loads(row[4]),
            )
            for row in rows
        ]

    async def query_with_truncation(
        self,
        since: str | None = None,
        component: str | None = None,
    ) -> tuple[list[ComponentEvent], bool]:
        """Query events, truncating to max_replay_events most recent if exceeded.

        Returns (events, truncated) where truncated is True if the full
        result set was larger than max_replay_events.
        """
        # First, get a count to determine if truncation is needed.
        clauses: list[str] = []
        params: list[str | int] = []

        if since is not None:
            clauses.append("timestamp > ?")
            params.append(since)
        if component is not None:
            clauses.append("component = ?")
            params.append(component)

        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""

        count_cursor = await self._store.db.execute(
            f"SELECT COUNT(*) FROM event_journal{where}", params
        )
        (total,) = await count_cursor.fetchone()

        truncated = total > self._max_replay

        # If truncated, fetch the last N rows. Use a subquery so we can
        # still return them in ASC order.
        if truncated:
            sql = (
                f"SELECT component, event_type, run_id, timestamp, data "
                f"FROM event_journal{where} "
                f"ORDER BY timestamp DESC LIMIT ?"
            )
            cursor = await self._store.db.execute(sql, [*params, self._max_replay])
            rows = list(await cursor.fetchall())
            rows.reverse()  # Back to ASC order
        else:
            sql = (
                f"SELECT component, event_type, run_id, timestamp, data "
                f"FROM event_journal{where} "
                f"ORDER BY timestamp ASC"
            )
            cursor = await self._store.db.execute(sql, params)
            rows = await cursor.fetchall()

        events = [
            ComponentEvent(
                component=row[0],
                event_type=row[1],
                run_id=row[2],
                timestamp=row[3],
                data=json.loads(row[4]),
            )
            for row in rows
        ]
        return events, truncated
