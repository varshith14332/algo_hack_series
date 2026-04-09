from db.redis_client import get_redis
import json
import logging

logger = logging.getLogger(__name__)

REPUTATION_KEY_PREFIX = "reputation:"


class ReputationService:
    async def get_score(self, agent_address: str) -> float:
        redis = await get_redis()
        data = await redis.get(f"{REPUTATION_KEY_PREFIX}{agent_address}")
        if data:
            return json.loads(data).get("score", 500.0)
        return 500.0

    async def get_agent_info(self, agent_address: str) -> dict:
        redis = await get_redis()
        data = await redis.get(f"{REPUTATION_KEY_PREFIX}{agent_address}")
        if data:
            return json.loads(data)
        return {"score": 500.0, "total_tasks": 0, "successful_tasks": 0}

    async def update_score(self, agent_address: str, success: bool) -> float:
        redis = await get_redis()
        key = f"{REPUTATION_KEY_PREFIX}{agent_address}"
        data = await redis.get(key)

        if data:
            info = json.loads(data)
        else:
            info = {"score": 500.0, "total_tasks": 0, "successful_tasks": 0}

        if success:
            info["score"] = min(1000.0, info["score"] + 10.0)
            info["successful_tasks"] = info.get("successful_tasks", 0) + 1
        else:
            info["score"] = max(0.0, info["score"] - 20.0)

        info["total_tasks"] = info.get("total_tasks", 0) + 1

        await redis.set(key, json.dumps(info))
        logger.info(f"Reputation updated for {agent_address[:8]}...: {info['score']:.1f}")
        return info["score"]

    async def list_all(self) -> list[dict]:
        redis = await get_redis()
        keys = await redis.keys(f"{REPUTATION_KEY_PREFIX}*")
        result = []
        for key in keys:
            data = await redis.get(key)
            if data:
                info = json.loads(data)
                info["agent_address"] = key.replace(REPUTATION_KEY_PREFIX, "")
                result.append(info)
        return result
