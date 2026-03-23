"""API key authentication middleware for Forge Dashboard."""

from __future__ import annotations

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send


class ApiKeyMiddleware:
    """Require ``Authorization: Bearer <key>`` for /api/ and /ws/ paths.

    If *api_key* is empty the middleware is a no-op (development mode).
    """

    def __init__(self, app: ASGIApp, api_key: str) -> None:
        self.app = app
        self.api_key = api_key

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        path: str = scope.get("path", "")
        if not (path.startswith("/api/") or path.startswith("/ws/")):
            await self.app(scope, receive, send)
            return

        headers: dict[bytes, bytes] = dict(scope.get("headers", []))
        auth = headers.get(b"authorization", b"").decode()

        if auth != f"Bearer {self.api_key}":
            if scope["type"] == "http":
                response = JSONResponse({"detail": "Unauthorized"}, status_code=401)
                await response(scope, receive, send)
            else:
                # WebSocket: consume connect message, then close with 4401
                await receive()
                await send({"type": "websocket.close", "code": 4401})
            return

        await self.app(scope, receive, send)
