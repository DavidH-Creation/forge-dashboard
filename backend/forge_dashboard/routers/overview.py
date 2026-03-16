"""Overview router — aggregated dashboard snapshot."""

from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/overview")
async def get_overview(request: Request):
    """Return a health + recent-runs overview for all registered components."""
    return await request.app.state.aggregator.get_overview()
