"""FastAPI application factory for the Forge Dashboard backend."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from forge_dashboard.config import DashboardConfig
from forge_dashboard.platform.event_journal import EventJournal
from forge_dashboard.platform.flow_tracker import FlowTracker
from forge_dashboard.platform.operation_log import OperationLog
from forge_dashboard.platform.state_store import StateStore
from forge_dashboard.plugin_sdk.registry import PluginRegistry
from forge_dashboard.routers import components, operations, overview, pipeline, ws
from forge_dashboard.services.aggregator import Aggregator
from forge_dashboard.services.event_bus import EventBus


def _build_plugin_kwargs(config: DashboardConfig) -> dict[str, dict]:
    """Map DashboardConfig paths to per-plugin constructor kwargs."""
    return {
        "bulwark": {"repo_root": config.bulwark_root},
        "cartographer": {"repo_root": config.cartographer_root},
        "crossfire": {"work_dir": config.crossfire_root},
        "crucible": {"repo_root": config.crucible_root},
    }


def create_app(
    db_path: Path | None = None,
    auto_discover: bool = True,
) -> FastAPI:
    """Build and return a fully-wired FastAPI application.

    Parameters
    ----------
    db_path:
        Path for the SQLite database.  Defaults to ``.forge-dashboard/state.db``.
    auto_discover:
        If *True*, discover plugins via entry-points during startup.
    """
    config = DashboardConfig()
    store = StateStore(db_path or config.db_path)
    registry = PluginRegistry()
    journal = EventJournal(store)
    op_log = OperationLog(store)
    flow_tracker = FlowTracker(store)
    bus = EventBus(registry=registry, journal=journal)
    aggregator = Aggregator(registry=registry)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await store.init()
        if auto_discover:
            registry.discover_plugins(plugin_kwargs=_build_plugin_kwargs(config))
        await bus.start()
        yield
        await bus.stop()
        await store.close()

    app = FastAPI(title="Forge Dashboard", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Attach services to app.state so routers can access them via request.app.state
    app.state.store = store
    app.state.registry = registry
    app.state.journal = journal
    app.state.op_log = op_log
    app.state.flow_tracker = flow_tracker
    app.state.bus = bus
    app.state.aggregator = aggregator

    # Include routers
    app.include_router(overview.router, prefix="/api")
    app.include_router(components.router, prefix="/api")
    app.include_router(pipeline.router, prefix="/api")
    app.include_router(operations.router, prefix="/api")
    app.include_router(ws.router)

    return app


# Module-level instance for ``uvicorn forge_dashboard.main:app``
app = create_app()
