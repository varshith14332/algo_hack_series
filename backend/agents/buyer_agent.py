from services.cache_service import CacheService
from services.agent_wallet_service import AgentWalletService
from config import settings
from db.redis_client import get_redis
import json
import logging

logger = logging.getLogger(__name__)

agent_wallet_service = AgentWalletService()


class BuyerAgent:
    def __init__(self):
        self.cache = CacheService()
        # Generate this agent's own Algorand wallet (derived, never stored)
        self._private_key, self.address = agent_wallet_service.generate_agent_account("buyer")
        logger.info(f"[BuyerAgent] Wallet: {self.address[:16]}...")

    async def run(self, state: dict) -> dict:
        task_text = state["task_text"]
        task_hash = state["task_hash"]
        task_id = state["task_id"]
        audit_trail: list = state.get("audit_trail", [])

        logger.info(f"[BuyerAgent] Processing task {task_id}")

        # Broadcast activity
        try:
            from routers.agents import broadcast_activity
            await broadcast_activity(
                event="task_received",
                agent="buyer",
                details={"task_id": task_id, "task_hash": task_hash[:16] + "..."},
            )
        except Exception:
            pass

        # ── Step 1: Check semantic cache ─────────────────────────
        cached = await self.cache.check_semantic(task_text)
        if cached:
            cached_result = await self.cache.get(cached["task_hash"])
            if cached_result:
                audit_trail.append({
                    "agent": "buyer",
                    "action": "cache_hit",
                    "detail": f"Semantic cache hit (score={cached['score']:.3f}) — no computation needed",
                    "payment_algo": None,
                    "tx_id": None,
                })
                state["result"] = cached_result["result"]
                state["merkle_root"] = cached_result["merkle_root"]
                state["ipfs_cid"] = cached_result["ipfs_cid"]
                state["status"] = "cache_hit"
                state["from_cache"] = True
                state["similarity_score"] = cached["score"]
                state["audit_trail"] = audit_trail

                # Store result for polling
                redis = await get_redis()
                await redis.setex(
                    f"task_result:{task_id}",
                    3600,
                    json.dumps({
                        "status": "cache_hit",
                        "result": cached_result["result"],
                        "merkle_root": cached_result["merkle_root"],
                        "ipfs_cid": cached_result["ipfs_cid"],
                        "from_cache": True,
                        "similarity_score": cached["score"],
                    }),
                )
                logger.info(f"[BuyerAgent] Cache hit for task {task_id}")
                return state

        # ── Step 2: Discover available services ──────────────────
        category = state.get("task_type", "analysis")
        try:
            from contracts.deploy.contract_client import ContractClient
            client = ContractClient()
            services = await client.discover_services(category)
        except Exception as e:
            logger.warning(f"[BuyerAgent] Service discovery failed: {e}")
            services = []

        # Filter: reputation >= MIN_AGENT_REPUTATION
        min_rep = settings.MIN_AGENT_REPUTATION
        qualified = [s for s in services if s.get("reputation_score", 0) >= min_rep]

        if qualified:
            # Pick cheapest qualifying service
            chosen = min(qualified, key=lambda s: s.get("price_microalgo", 999_999_999))
            price_microalgo = chosen["price_microalgo"]
            price_algo = price_microalgo / 1_000_000

            audit_trail.append({
                "agent": "buyer",
                "action": "service_discovered",
                "detail": f"Discovered {len(services)} services for '{category}', selected '{chosen.get('service_name')}' (reputation={chosen.get('reputation_score', 0)}, price={price_algo} ALGO)",
                "payment_algo": None,
                "tx_id": None,
            })

            # Verify agent budget on-chain before paying
            ok = await client.verify_agent(self.address, category, price_microalgo)
            if not ok:
                audit_trail.append({
                    "agent": "buyer",
                    "action": "budget_exceeded",
                    "detail": "Buyer agent over budget or category not allowed — routing to local seller",
                    "payment_algo": None,
                    "tx_id": None,
                })
            else:
                # Record spend on-chain (atomic)
                await client.record_spend(self.address, price_microalgo)
                audit_trail.append({
                    "agent": "buyer",
                    "action": "payment_recorded",
                    "detail": f"On-chain spend recorded: {price_algo} ALGO to '{chosen.get('service_name')}'",
                    "payment_algo": price_algo,
                    "tx_id": f"agent-mode:{self.address[:16]}",
                })
                logger.info(f"[BuyerAgent] Selected service '{chosen.get('service_name')}' at {price_algo} ALGO")
        else:
            audit_trail.append({
                "agent": "buyer",
                "action": "no_external_service",
                "detail": f"No qualified external services found for '{category}' (min_rep={min_rep}) — routing to local SellerAgent",
                "payment_algo": None,
                "tx_id": None,
            })

        state["status"] = "routed_to_seller"
        state["audit_trail"] = audit_trail
        logger.info(f"[BuyerAgent] Routing task {task_id} to seller")
        return state
