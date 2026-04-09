from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from services.reputation_service import ReputationService
from datetime import datetime, timezone
from typing import List
import asyncio
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
reputation_service = ReputationService()


def _now():
    return datetime.now(timezone.utc).isoformat()


def _envelope(success: bool, data=None, error=None):
    return {"success": success, "data": data, "error": error, "timestamp": _now()}


class ConnectionManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.connections:
            self.connections.remove(ws)

    async def broadcast(self, message: dict):
        disconnected = []
        for ws in self.connections:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(ws)


manager = ConnectionManager()


@router.websocket("/ws/activity")
async def agent_activity_feed(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await asyncio.sleep(30)
            await ws.send_json({"type": "ping", "timestamp": _now()})
    except WebSocketDisconnect:
        manager.disconnect(ws)


async def broadcast_activity(event: str, agent: str, details: dict):
    await manager.broadcast({
        "type": "activity",
        "event": event,
        "agent": agent,
        "details": details,
        "timestamp": _now(),
    })


@router.get("/reputation")
async def get_all_reputation():
    scores = await reputation_service.list_all()
    return JSONResponse(content=_envelope(True, {"agents": scores}))


@router.get("/reputation/{agent_address}")
async def get_agent_reputation(agent_address: str):
    info = await reputation_service.get_agent_info(agent_address)
    return JSONResponse(content=_envelope(True, info))


@router.get("/services")
async def get_services():
    """Return all services registered in the ServiceRegistry (Redis dev store)."""
    try:
        import json
        from db.redis_client import get_redis
        redis = await get_redis()
        keys = await redis.keys("service_registry:*")
        services = []
        for key in keys:
            raw = await redis.get(key)
            if raw:
                services.append(json.loads(raw))
        return JSONResponse(content=_envelope(True, {"services": services}))
    except Exception as e:
        return JSONResponse(content=_envelope(True, {"services": []}))


@router.get("/status")
async def agent_status():
    """Return current agent configuration and connection count."""
    return JSONResponse(content=_envelope(True, {
        "agents": ["buyer", "seller", "verifier", "reputation"],
        "active_connections": len(manager.connections),
        "status": "running",
    }))
