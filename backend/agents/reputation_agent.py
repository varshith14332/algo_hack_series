from services.reputation_service import ReputationService
from config import settings
import logging

logger = logging.getLogger(__name__)


class ReputationAgent:
    def __init__(self):
        self.reputation = ReputationService()

    async def reward(self, state: dict) -> dict:
        """Called on successful verification — only Reputation Agent updates scores."""
        agent_address = settings.ORACLE_ADDRESS or "seller-agent-default"
        task_id = state["task_id"]
        audit_trail: list = state.get("audit_trail", [])

        try:
            new_score = await self.reputation.update_score(agent_address, success=True)
            logger.info(f"[ReputationAgent] Rewarded {agent_address[:8]}...: score={new_score:.1f}")

            audit_trail.append({
                "agent": "reputation",
                "action": "reward",
                "detail": f"Score updated to {new_score:.1f} after successful verification",
                "payment_algo": None,
                "tx_id": None,
            })

            from routers.agents import broadcast_activity
            await broadcast_activity(
                event="reputation_updated",
                agent="reputation",
                details={
                    "task_id": task_id,
                    "action": "reward",
                    "score": new_score,
                },
            )
        except Exception as e:
            logger.error(f"[ReputationAgent] Reward error: {e}")

        state["audit_trail"] = audit_trail
        # Persist final result for polling
        await self._store_final_result(state)
        return state

    async def slash(self, state: dict) -> dict:
        """Called on verification failure — only Reputation Agent updates scores."""
        agent_address = settings.ORACLE_ADDRESS or "seller-agent-default"
        task_id = state["task_id"]
        audit_trail: list = state.get("audit_trail", [])

        try:
            new_score = await self.reputation.update_score(agent_address, success=False)
            logger.warning(f"[ReputationAgent] Slashed {agent_address[:8]}...: score={new_score:.1f}")

            audit_trail.append({
                "agent": "reputation",
                "action": "slash",
                "detail": f"Score penalized to {new_score:.1f} after verification failure",
                "payment_algo": None,
                "tx_id": None,
            })

            from routers.agents import broadcast_activity
            await broadcast_activity(
                event="reputation_updated",
                agent="reputation",
                details={
                    "task_id": task_id,
                    "action": "slash",
                    "score": new_score,
                },
            )
        except Exception as e:
            logger.error(f"[ReputationAgent] Slash error: {e}")

        state["audit_trail"] = audit_trail

        await self._store_final_result(state)
        return state

    async def _store_final_result(self, state: dict):
        try:
            from db.redis_client import get_redis
            import json
            redis = await get_redis()
            await redis.setex(
                f"task_result:{state['task_id']}",
                3600 * 24,
                json.dumps({
                    "status": state.get("status"),
                    "result": state.get("result"),
                    "merkle_root": state.get("merkle_root"),
                    "ipfs_cid": state.get("ipfs_cid"),
                    "verification_score": state.get("verification_score"),
                    "from_cache": state.get("from_cache", False),
                    "error": state.get("error"),
                }),
            )
        except Exception as e:
            logger.error(f"[ReputationAgent] Failed to store result: {e}")
