"""Operations router — trigger, cancel, retry actions on component runs."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


@router.post("/components/{name}/trigger")
async def trigger(request: Request, name: str):
    """Trigger a new run on a component."""
    plugin = request.app.state.registry.get(name)
    if not plugin:
        raise HTTPException(404, detail={"error": "ComponentNotFound"})
    body = await request.json()
    run_id = await request.app.state.registry.safe_call(
        plugin, "trigger", params=body
    )
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
    result = await request.app.state.registry.safe_call(
        plugin, "cancel", run_id=run_id
    )
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
    new_run_id = await request.app.state.registry.safe_call(
        plugin, "retry", run_id=run_id
    )
    await request.app.state.op_log.record(
        component=name,
        operation="retry",
        run_id=run_id,
        params={},
        result={"new_run_id": new_run_id},
    )
    return {"run_id": new_run_id}
