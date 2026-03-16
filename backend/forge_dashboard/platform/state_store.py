"""SQLite-backed state store for the Forge Dashboard platform layer.

Provides persistent storage for pipeline flows, events, operations,
and artifact metadata via aiosqlite.
"""

from __future__ import annotations

from pathlib import Path

import aiosqlite


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS pipeline_flows (
    flow_id    TEXT PRIMARY KEY,
    name       TEXT NOT NULL,
    status     TEXT NOT NULL,
    created_at TEXT NOT NULL,
    finished_at TEXT
);

CREATE TABLE IF NOT EXISTS flow_steps (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    flow_id     TEXT NOT NULL REFERENCES pipeline_flows(flow_id),
    component   TEXT NOT NULL,
    run_id      TEXT,
    step_order  INTEGER NOT NULL,
    status      TEXT NOT NULL,
    started_at  TEXT,
    finished_at TEXT,
    UNIQUE(flow_id, component)
);

CREATE INDEX IF NOT EXISTS idx_flow_steps_flow_id
    ON flow_steps(flow_id);

CREATE TABLE IF NOT EXISTS event_journal (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    component  TEXT NOT NULL,
    event_type TEXT NOT NULL,
    run_id     TEXT NOT NULL,
    timestamp  TEXT NOT NULL,
    data       TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_event_journal_component
    ON event_journal(component);
CREATE INDEX IF NOT EXISTS idx_event_journal_timestamp
    ON event_journal(timestamp);
CREATE INDEX IF NOT EXISTS idx_event_journal_run_id
    ON event_journal(run_id);

CREATE TABLE IF NOT EXISTS operation_log (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    component TEXT NOT NULL,
    operation TEXT NOT NULL,
    run_id    TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    params    TEXT NOT NULL DEFAULT '{}',
    result    TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS artifact_index (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    component     TEXT NOT NULL,
    run_id        TEXT NOT NULL,
    name          TEXT NOT NULL,
    artifact_type TEXT NOT NULL,
    path          TEXT NOT NULL,
    size          INTEGER,
    created_at    TEXT NOT NULL
);
"""


class StateStore:
    """Async SQLite state store for the platform layer."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._db: aiosqlite.Connection | None = None

    @property
    def db(self) -> aiosqlite.Connection:
        """Return the active database connection (raises if not initialised)."""
        if self._db is None:
            raise RuntimeError("StateStore not initialised — call init() first")
        return self._db

    async def init(self) -> None:
        """Open the database and ensure the schema exists."""
        if self._db is None:
            self._db = await aiosqlite.connect(self._db_path)
            self._db.row_factory = aiosqlite.Row
        await self._db.executescript(_SCHEMA_SQL)
        await self._db.commit()

    async def close(self) -> None:
        """Close the database connection."""
        if self._db is not None:
            await self._db.close()
            self._db = None

    async def list_tables(self) -> list[str]:
        """Return the names of all user tables in the database."""
        cursor = await self.db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        rows = await cursor.fetchall()
        return [row[0] for row in rows]
