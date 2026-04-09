import redis.asyncio as aioredis
from config import settings
import logging

logger = logging.getLogger(__name__)

_redis: aioredis.Redis | None = None


async def init_redis():
    global _redis
    _redis = await aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    logger.info("Redis connected")


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis


async def close_redis():
    global _redis
    if _redis:
        await _redis.close()
        _redis = None
