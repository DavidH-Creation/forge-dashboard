"""OperationLog — record and query dashboard operations in SQLite."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from forge_dashboard.platform.state_store import StateStore


class OperationLog:
    """Append-only log of operations performed via the dashboard."""

    def __init__(self, store: StateStore) -> None:
        self._store = store

    async def record(
        self,
        component: str,
        operation: str,
        run_id: str,
        params: dict | None = None,
        result: dict | None = None,
    ) -> None:
        """Record an operation."""
        now = datetime.now(timezone.utc).isoformat()
        await self._store.db.execute(
            "INSERT INTO operation_log (component, operation, run_id, timestamp, params, result) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                component,
                operation,
                run_id,
                now,
                json.dumps(params or {}),
                json.dumps(result or {}),
            ),
        )
        await self._store.db.commit()

    async def list_recent(self, limit: int = 20) -> list[dict]:
        """Return the most recent operations, newest first."""
        cursor = await self._store.db.execute(
            "SELECT component, operation, run_id, timestamp, params, result "
            "FROM operation_log ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        )
        rows = await cursor.fetchall()
        return [
            {
                "component": row[0],
                "operation": row[1],
                "run_id": row[2],
                "timestamp": row[3],
                "params": json.loads(row[4]),
                "result": json.loads(row[5]),
            }
            for row in rows
        ]
