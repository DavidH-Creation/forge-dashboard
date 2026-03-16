"""FlowTracker — manage multi-component pipeline flows in SQLite."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from forge_dashboard.platform.state_store import StateStore


class FlowTracker:
    """Create and track cross-component pipeline flows."""

    def __init__(self, store: StateStore) -> None:
        self._store = store

    async def create_flow(self, name: str, components: list[str]) -> str:
        """Create a new pipeline flow with the given component steps.

        Returns the generated flow_id.
        """
        flow_id = f"flow-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc).isoformat()

        await self._store.db.execute(
            "INSERT INTO pipeline_flows (flow_id, name, status, created_at) "
            "VALUES (?, ?, 'pending', ?)",
            (flow_id, name, now),
        )

        for order, component in enumerate(components):
            await self._store.db.execute(
                "INSERT INTO flow_steps (flow_id, component, step_order, status) "
                "VALUES (?, ?, ?, 'pending')",
                (flow_id, component, order),
            )

        await self._store.db.commit()
        return flow_id

    async def start_step(self, flow_id: str, component: str, run_id: str) -> None:
        """Mark a step as running and set the flow status to running."""
        now = datetime.now(timezone.utc).isoformat()

        await self._store.db.execute(
            "UPDATE flow_steps SET status = 'running', run_id = ?, started_at = ? "
            "WHERE flow_id = ? AND component = ?",
            (run_id, now, flow_id, component),
        )
        await self._store.db.execute(
            "UPDATE pipeline_flows SET status = 'running' WHERE flow_id = ?",
            (flow_id,),
        )
        await self._store.db.commit()

    async def complete_step(self, flow_id: str, component: str) -> None:
        """Mark a step as completed. If all steps are done, complete the flow."""
        now = datetime.now(timezone.utc).isoformat()

        await self._store.db.execute(
            "UPDATE flow_steps SET status = 'completed', finished_at = ? "
            "WHERE flow_id = ? AND component = ?",
            (now, flow_id, component),
        )

        # Check if all steps are completed
        cursor = await self._store.db.execute(
            "SELECT COUNT(*) FROM flow_steps "
            "WHERE flow_id = ? AND status != 'completed'",
            (flow_id,),
        )
        (remaining,) = await cursor.fetchone()

        if remaining == 0:
            await self._store.db.execute(
                "UPDATE pipeline_flows SET status = 'completed', finished_at = ? "
                "WHERE flow_id = ?",
                (now, flow_id),
            )

        await self._store.db.commit()

    async def fail_step(self, flow_id: str, component: str, error: str) -> None:
        """Mark a step and its flow as failed."""
        now = datetime.now(timezone.utc).isoformat()

        await self._store.db.execute(
            "UPDATE flow_steps SET status = 'failed', finished_at = ? "
            "WHERE flow_id = ? AND component = ?",
            (now, flow_id, component),
        )
        await self._store.db.execute(
            "UPDATE pipeline_flows SET status = 'failed', finished_at = ? "
            "WHERE flow_id = ?",
            (now, flow_id),
        )
        await self._store.db.commit()

    async def get_flow(self, flow_id: str) -> dict:
        """Get a flow with all its steps."""
        cursor = await self._store.db.execute(
            "SELECT flow_id, name, status, created_at, finished_at "
            "FROM pipeline_flows WHERE flow_id = ?",
            (flow_id,),
        )
        row = await cursor.fetchone()
        if row is None:
            raise ValueError(f"Flow not found: {flow_id}")

        steps_cursor = await self._store.db.execute(
            "SELECT component, run_id, step_order, status, started_at, finished_at "
            "FROM flow_steps WHERE flow_id = ? ORDER BY step_order",
            (flow_id,),
        )
        step_rows = await steps_cursor.fetchall()

        return {
            "flow_id": row[0],
            "name": row[1],
            "status": row[2],
            "created_at": row[3],
            "finished_at": row[4],
            "steps": [
                {
                    "component": s[0],
                    "run_id": s[1],
                    "step_order": s[2],
                    "status": s[3],
                    "started_at": s[4],
                    "finished_at": s[5],
                }
                for s in step_rows
            ],
        }

    async def list_flows(self, limit: int = 20, offset: int = 0) -> list[dict]:
        """List flows (without steps) ordered by creation time descending."""
        cursor = await self._store.db.execute(
            "SELECT flow_id, name, status, created_at, finished_at "
            "FROM pipeline_flows ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        rows = await cursor.fetchall()
        return [
            {
                "flow_id": row[0],
                "name": row[1],
                "status": row[2],
                "created_at": row[3],
                "finished_at": row[4],
            }
            for row in rows
        ]
