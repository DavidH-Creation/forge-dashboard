"""Pipeline router — cross-component flows and event journal queries."""

from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/pipeline/flows")
async def list_flows(request: Request, limit: int = 20, offset: int = 0):
    """List pipeline flows, ordered by creation time descending."""
    return await request.app.state.flow_tracker.list_flows(limit=limit, offset=offset)


@router.get("/pipeline/flows/{flow_id}")
async def get_flow(request: Request, flow_id: str):
    """Get a specific pipeline flow with all its steps."""
    return await request.app.state.flow_tracker.get_flow(flow_id)


@router.get("/events")
async def get_events(
    request: Request,
    since: str | None = None,
    component: str | None = None,
    limit: int = 100,
):
    """Query the event journal with optional time, component, and limit filters."""
    events = await request.app.state.journal.query(
        since=since, limit=limit, component=component
    )
    return [e.model_dump() for e in events]
