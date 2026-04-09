from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.cache_service import CacheService
from datetime import datetime, timezone
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
_cache: CacheService | None = None

def get_cache() -> CacheService:
    global _cache
    if _cache is None:
        _cache = CacheService()
    return _cache


def _now():
    return datetime.now(timezone.utc).isoformat()


def _envelope(success: bool, data=None, error=None):
    return {"success": success, "data": data, "error": error, "timestamp": _now()}


class SemanticCheckRequest(BaseModel):
    task_text: str


@router.post("/check")
async def check_cache(payload: SemanticCheckRequest):
    """Check semantic similarity cache."""
    semantic = await get_cache().check_semantic(payload.task_text)
    if semantic:
        result = await get_cache().get(semantic["task_hash"])
        return JSONResponse(content=_envelope(True, {
            "cache_hit": True,
            "similarity_score": semantic["score"],
            "task_hash": semantic["task_hash"],
            "result": result,
        }))
    return JSONResponse(content=_envelope(True, {"cache_hit": False}))


@router.get("/result/{task_hash}")
async def get_cached_result(task_hash: str):
    result = await get_cache().get(task_hash)
    if result:
        return JSONResponse(content=_envelope(True, result))
    return JSONResponse(
        status_code=404,
        content=_envelope(False, error="Not found in cache"),
    )


@router.get("/stats")
async def cache_stats():
    from db.redis_client import get_redis
    redis = await get_redis()
    result_keys = await redis.keys("result:*")
    tx_keys = await redis.keys("used_tx:*")
    return JSONResponse(content=_envelope(True, {
        "cached_results": len(result_keys),
        "verified_transactions": len(tx_keys),
    }))
