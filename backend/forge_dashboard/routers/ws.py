"""WebSocket endpoint — real-time event streaming with replay support."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from forge_dashboard.plugin_sdk.models import ComponentEvent

router = APIRouter()


@router.websocket("/ws/events")
async def events_ws(websocket: WebSocket):
    """Stream component events to the client in real-time.

    Supports two client-to-server message types:
    - ``{"type": "subscribe", "components": ["bulwark", ...]}`` — filter events
    - ``{"type": "replay", "since": "<ISO timestamp>"}`` — replay past events
    """
    await websocket.accept()
    bus = websocket.app.state.bus
    journal = websocket.app.state.journal
    component_filter: set[str] | None = None
    queue: asyncio.Queue = asyncio.Queue()

    def on_event(event: ComponentEvent):
        if component_filter and event.component not in component_filter:
            return
        queue.put_nowait(event)

    bus.add_listener(on_event)
    try:
        send_task = asyncio.create_task(_send_loop(websocket, queue))
        async for data in websocket.iter_json():
            msg_type = data.get("type")
            if msg_type == "replay":
                since = data.get("since")
                comp = (
                    next(iter(component_filter), None)
                    if component_filter
                    else None
                )
                events, truncated = await journal.query_with_truncation(
                    since=since, component=comp
                )
                for e in events:
                    await websocket.send_json(e.model_dump())
                await websocket.send_json(
                    {
                        "type": "replay_complete",
                        "truncated": truncated,
                        "count": len(events),
                    }
                )
            elif msg_type == "subscribe":
                components = data.get("components")
                component_filter = set(components) if components else None
    except WebSocketDisconnect:
        pass
    finally:
        bus.remove_listener(on_event)
        send_task.cancel()


async def _send_loop(websocket: WebSocket, queue: asyncio.Queue):
    """Continuously drain the queue and send events over the WebSocket."""
    while True:
        event = await queue.get()
        await websocket.send_json(event.model_dump())
