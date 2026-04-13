"""WebSocket connection manager for real-time traffic broadcasting."""
from __future__ import annotations
import asyncio
import json
from typing import Any
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._active: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        async with self._lock:
            self._active.append(ws)

    async def disconnect(self, ws: WebSocket):
        async with self._lock:
            if ws in self._active:
                self._active.remove(ws)

    async def broadcast(self, data: Any):
        """Broadcast JSON-serialisable data to all connected clients."""
        msg = json.dumps(data, default=str)
        dead: list[WebSocket] = []
        async with self._lock:
            clients = list(self._active)
        for ws in clients:
            try:
                await ws.send_text(msg)
            except Exception:
                dead.append(ws)
        for ws in dead:
            await self.disconnect(ws)

    @property
    def count(self) -> int:
        return len(self._active)


ws_manager = ConnectionManager()
