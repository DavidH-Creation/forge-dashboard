"""Components router — per-component runs, artifacts, and config."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


@router.get("/components")
async def list_components(request: Request):
    """List all registered component plugins with their health status."""
    registry = request.app.state.registry
    return [
        {"name": n, "status": registry.get_status(n)}
        for n in registry.list_plugins()
    ]


@router.get("/components/{name}/runs")
async def list_runs(
    request: Request,
    name: str,
    limit: int = 20,
    offset: int = 0,
    status: str | None = None,
):
    """List runs for a given component with optional pagination and status filter."""
    plugin = request.app.state.registry.get(name)
    if not plugin:
        raise HTTPException(
            404,
            detail={"error": "ComponentNotFound", "detail": f"No plugin: '{name}'"},
        )
    runs = await request.app.state.registry.safe_call(
        plugin, "list_runs", limit=limit, offset=offset, status_filter=status
    )
    return [r.model_dump() for r in runs]


@router.get("/components/{name}/runs/{run_id}")
async def get_run(request: Request, name: str, run_id: str):
    """Get detailed information about a specific run."""
    plugin = request.app.state.registry.get(name)
    if not plugin:
        raise HTTPException(
            404,
            detail={"error": "ComponentNotFound", "detail": f"No plugin: '{name}'"},
        )
    detail = await request.app.state.registry.safe_call(
        plugin, "get_run", run_id=run_id
    )
    return detail.model_dump()


@router.get("/components/{name}/runs/{run_id}/artifacts")
async def get_artifacts(request: Request, name: str, run_id: str):
    """List artifacts produced by a specific run."""
    plugin = request.app.state.registry.get(name)
    if not plugin:
        raise HTTPException(
            404,
            detail={"error": "ComponentNotFound", "detail": f"No plugin: '{name}'"},
        )
    artifacts = await request.app.state.registry.safe_call(
        plugin, "get_artifacts", run_id=run_id
    )
    return [a.model_dump() for a in artifacts]


@router.get("/components/{name}/config")
async def get_config(request: Request, name: str):
    """Get the configuration for a component."""
    plugin = request.app.state.registry.get(name)
    if not plugin:
        raise HTTPException(404, detail={"error": "ComponentNotFound"})
    return await request.app.state.registry.safe_call(plugin, "get_config")


@router.put("/components/{name}/config")
async def update_config(request: Request, name: str, patch: dict):
    """Update the configuration for a component."""
    plugin = request.app.state.registry.get(name)
    if not plugin:
        raise HTTPException(404, detail={"error": "ComponentNotFound"})
    await request.app.state.registry.safe_call(plugin, "update_config", patch=patch)
    return {"status": "ok"}
