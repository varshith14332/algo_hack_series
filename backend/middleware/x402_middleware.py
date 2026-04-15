from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from services.algorand_service import AlgorandService
from services.cache_service import CacheService
from config import settings
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

PROTECTED_ROUTES = {
    "/api/tasks/run",
}

# Rate limiting: max 10 req/min per wallet (human mode)
RATE_LIMIT = 10
RATE_WINDOW = 60

# Rate limiting for autonomous runs: max 3 concurrent per owner
AUTONOMOUS_RATE_LIMIT = 3
AUTONOMOUS_RATE_WINDOW = 300  # 5 minutes


class X402Middleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._algorand = None
        self._cache = None

    @property
    def algorand(self):
        if self._algorand is None:
            self._algorand = AlgorandService()
        return self._algorand

    @property
    def cache(self):
        if self._cache is None:
            self._cache = CacheService()
        return self._cache

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path not in PROTECTED_ROUTES:
            return await call_next(request)

        # AGENT MODE DETECTION — must run BEFORE human mode
        agent_mode = request.headers.get("X-Agent-Mode", "").lower() == "true"
        agent_address = request.headers.get("X-Agent-Address", "")
        category = request.headers.get("X-Category", "general")
        task_hash = request.headers.get("X-Task-Hash", "")

        if agent_mode:
            # STEP 1 — Validate agent address format
            if not agent_address:
                return self._error(400, "X-Agent-Address header required in agent mode")
            
            if not self.algorand.validate_address(agent_address):
                return self._error(400, "Invalid agent address format")
            
            if not task_hash:
                return self._error(400, "X-Task-Hash header required")
            
            # STEP 2 — Get price for this route
            is_cached = await self.cache.check_exact(task_hash)
            price_microalgo = int(
                (settings.CACHED_TASK_PRICE_ALGO if is_cached else settings.NEW_TASK_PRICE_ALGO)
                * 1_000_000
            )
            
            # STEP 3 — Verify agent on-chain via contract_client
            try:
                from contracts.deploy.contract_client import ContractClient
                client = ContractClient()
                verified = await client.verify_agent(
                    agent_address=agent_address,
                    category=category,
                    amount_microalgo=price_microalgo,
                )
                
                if not verified:
                    return JSONResponse(
                        status_code=403,
                        content={
                            "success": False,
                            "error": "Agent authorization failed",
                            "data": {
                                "reason": "Agent inactive, over budget, or category not allowed",
                                "agent_address": agent_address,
                                "required_amount_microalgo": price_microalgo,
                            },
                            "timestamp": self._now(),
                        }
                    )
                
                # STEP 4 — Record spend on-chain
                await client.record_spend(agent_address, price_microalgo)
                
            except Exception as e:
                logger.error(f"Agent mode verification failed: {e}")
                # Fail open in dev mode (no contracts deployed)
                logger.warning("Agent mode: proceeding without on-chain verification (dev mode)")
            
            # STEP 5 — Attach to request state and proceed
            request.state.agent_mode = True
            request.state.agent_address = agent_address
            request.state.payment_verified = True
            request.state.task_hash = task_hash
            request.state.tx_id = f"agent-mode:{agent_address[:16]}"
            
            return await call_next(request)
        
        # Human payment flow (existing code)
        return await self._handle_human_mode(request, call_next)

    # ──────────────────────────────────────────────────────────────
    # Human x402 payment flow (Pera Wallet)
    # ──────────────────────────────────────────────────────────────

    async def _handle_human_mode(self, request: Request, call_next):
        wallet = request.headers.get("X-Wallet-Address", "")
        if wallet and not self.algorand.validate_address(wallet):
            return self._error(400, "Invalid wallet address format")

        if wallet:
            rate_ok = await self._check_rate_limit(wallet)
            if not rate_ok:
                return self._error(429, "Rate limit exceeded: max 10 requests/min")

        payment_proof = request.headers.get("X-Payment-Proof")
        task_hash = request.headers.get("X-Task-Hash")

        if not task_hash:
            return self._error(400, "X-Task-Hash header required")

        if not payment_proof:
            is_cached = await self.cache.check_exact(task_hash)
            price = settings.CACHED_TASK_PRICE_ALGO if is_cached else settings.NEW_TASK_PRICE_ALGO
            escrow_address = settings.ORACLE_ADDRESS

            return JSONResponse(status_code=402, content={
                "success": False,
                "error": "Payment required",
                "data": {
                    "payment_required": True,
                    "amount_algo": price,
                    "receiver": escrow_address,
                    "task_hash": task_hash,
                    "is_cached": is_cached,
                    "note": f"neuralledger:{task_hash}",
                },
                "timestamp": self._now(),
            })

        # Verify payment on-chain
        verified = await self.algorand.verify_transaction(
            tx_id=payment_proof,
            task_hash=task_hash,
        )

        if not verified:
            return self._error(402, "Payment verification failed")

        request.state.task_hash = task_hash
        request.state.tx_id = payment_proof
        request.state.payment_verified = True
        request.state.agent_mode = False

        return await call_next(request)

    async def _check_rate_limit(self, wallet: str) -> bool:
        try:
            from db.redis_client import get_redis
            redis = await get_redis()
            key = f"rate:{wallet}"
            count = await redis.get(key)
            if count and int(count) >= RATE_LIMIT:
                return False
            pipe = redis.pipeline()
            await pipe.incr(key)
            await pipe.expire(key, RATE_WINDOW)
            await pipe.execute()
            return True
        except Exception:
            return True  # Fail open on Redis error

    def _error(self, status: int, message: str):
        return JSONResponse(status_code=status, content={
            "success": False,
            "error": message,
            "data": None,
            "timestamp": self._now(),
        })

    def _now(self):
        return datetime.now(timezone.utc).isoformat()
