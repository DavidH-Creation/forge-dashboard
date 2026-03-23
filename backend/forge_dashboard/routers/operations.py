"""Operations router — trigger, cancel, retry actions on component runs."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from forge_dashboard.plugin_sdk.registry import PluginCallError

router = APIRouter()


@router.post("/components/{name}/trigger")
async def trigger(request: Request, name: str):
    """Trigger a new run on a component."""
    plugin = request.app.state.registry.get(name)
    if not plugin:
        raise HTTPException(404, detail={"error": "ComponentNotFound"})
    body = await request.json()
    try:
        run_id = await request.app.state.registry.safe_call(
            plugin, "trigger", params=body
        )
    except PluginCallError as exc:
        if isinstance(exc.cause, NotImplementedError):
            raise HTTPException(501, detail={"error": "Operation not yet supported for this component"})
        raise
    await request.app.state.op_log.record(
        component=name,
        operation="trigger",
        run_id=run_id,
        params=body,
        result={"success": True},
    )
    return {"run_id": run_id}


@router.delete("/components/{name}/runs/{run_id}")
async def cancel(request: Request, name: str, run_id: str):
    """Cancel a running component run."""
    plugin = request.app.state.registry.get(name)
    if not plugin:
        raise HTTPException(404, detail={"error": "ComponentNotFound"})
    try:
        result = await request.app.state.registry.safe_call(
            plugin, "cancel", run_id=run_id
        )
    except PluginCallError as exc:
        if isinstance(exc.cause, NotImplementedError):
            raise HTTPException(501, detail={"error": "Operation not yet supported for this component"})
        raise
    await request.app.state.op_log.record(
        component=name,
        operation="cancel",
        run_id=run_id,
        params={},
        result={"success": result},
    )
    return {"cancelled": result}


@router.post("/components/{name}/runs/{run_id}/retry")
async def retry(request: Request, name: str, run_id: str):
    """Retry a failed component run."""
    plugin = request.app.state.registry.get(name)
    if not plugin:
        raise HTTPException(404, detail={"error": "ComponentNotFound"})
    try:
        new_run_id = await request.app.state.registry.safe_call(
            plugin, "retry", run_id=run_id
        )
    except PluginCallError as exc:
        if isinstance(exc.cause, NotImplementedError):
            raise HTTPException(501, detail={"error": "Operation not yet supported for this component"})
        raise
    await request.app.state.op_log.record(
        component=name,
        operation="retry",
        run_id=run_id,
        params={},
        result={"new_run_id": new_run_id},
    )
    return {"run_id": new_run_id}
