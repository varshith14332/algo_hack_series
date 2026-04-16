from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from services.algorand_service import AlgorandService
from services.cache_service import CacheService
from config import settings
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

PROTECTED_ROUTES = {
    "/api/tasks/run",
    "/api/tasks/result",
}

# All origins that should be allowed during development
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]


def add_cors_headers(response: Response, origin: str) -> Response:
    """Manually attach CORS headers to any response."""
    allowed = origin if origin in ALLOWED_ORIGINS else ALLOWED_ORIGINS[0]
    response.headers["Access-Control-Allow-Origin"] = allowed
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = (
        "Content-Type, Authorization, X-Payment-Proof, "
        "X-Task-Hash, X-Wallet-Address, X-Agent-Mode, "
        "X-Agent-Address, X-Category"
    )
    response.headers["Access-Control-Expose-Headers"] = (
        "X-Payment-Recorded, X-Spend-Remaining"
    )
    return response


def _now():
    return datetime.now(timezone.utc).isoformat()


def _envelope(success: bool, data=None, error=None):
    return {
        "success": success,
        "data": data,
        "error": error,
        "timestamp": _now()
    }


class X402Middleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)
        self.algorand = AlgorandService()
        self.cache = CacheService()

    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin", ALLOWED_ORIGINS[0])

        # Always pass through OPTIONS preflight — let CORS middleware handle it
        if request.method == "OPTIONS":
            return await call_next(request)

        path = request.url.path

        # Only intercept protected routes
        if path not in PROTECTED_ROUTES:
            return await call_next(request)

        # ── AGENT MODE ──────────────────────────────────────────────
        agent_mode = request.headers.get("X-Agent-Mode", "").lower() == "true"
        agent_address = request.headers.get("X-Agent-Address", "")
        category = request.headers.get("X-Category", "general")
        task_hash = request.headers.get("X-Task-Hash", "")

        if agent_mode:
            from algosdk import encoding
            if not agent_address or not encoding.is_valid_address(agent_address):
                resp = JSONResponse(
                    status_code=400,
                    content=_envelope(False, error="Invalid or missing X-Agent-Address")
                )
                return add_cors_headers(resp, origin)

            price = int(settings.NEW_TASK_PRICE_ALGO * 1_000_000)

            try:
                from contracts.deploy.contract_client import ContractClient
                client = ContractClient()
                verified = await client.verify_agent(agent_address, category, price)
            except Exception as e:
                logger.error(f"Agent verification error: {e}")
                verified = False

            if not verified:
                resp = JSONResponse(
                    status_code=403,
                    content=_envelope(False, error="Agent authorization failed", data={
                        "reason": "Agent inactive, over budget, or category not allowed",
                        "agent_address": agent_address,
                        "required_amount_microalgo": price
                    })
                )
                return add_cors_headers(resp, origin)

            try:
                await client.record_spend(agent_address, price)
            except Exception as e:
                logger.warning(f"record_spend failed: {e}")

            request.state.agent_mode = True
            request.state.agent_address = agent_address
            request.state.payment_verified = True
            request.state.task_hash = task_hash
            response = await call_next(request)
            return add_cors_headers(response, origin)

        # ── HUMAN MODE (x402) ────────────────────────────────────────
        payment_proof = request.headers.get("X-Payment-Proof")

        if not task_hash:
            resp = JSONResponse(
                status_code=400,
                content=_envelope(False, error="X-Task-Hash header required")
            )
            return add_cors_headers(resp, origin)

        if not payment_proof:
            # Return 402 — this is the payment request
            is_cached = await self.cache.check_exact(task_hash)
            price = (
                settings.CACHED_TASK_PRICE_ALGO
                if is_cached
                else settings.NEW_TASK_PRICE_ALGO
            )

            try:
                from contracts.deploy.contract_client import ContractClient
                escrow_address = settings.ORACLE_ADDRESS
            except Exception:
                escrow_address = settings.ORACLE_ADDRESS

            resp = JSONResponse(
                status_code=402,
                content=_envelope(False, error="Payment required", data={
                    "payment_required": True,
                    "amount_algo": price,
                    "receiver": escrow_address,
                    "task_hash": task_hash,
                    "is_cached": is_cached,
                    "note": f"neuralledger:{task_hash}"
                })
            )
            # ← THIS IS THE CRITICAL LINE — CORS on 402
            return add_cors_headers(resp, origin)

        # Payment proof provided — verify it
        verified = await self.algorand.verify_transaction(
            tx_id=payment_proof,
            task_hash=task_hash,
        )

        if not verified:
            resp = JSONResponse(
                status_code=402,
                content=_envelope(False, error="Payment verification failed")
            )
            return add_cors_headers(resp, origin)

        request.state.task_hash = task_hash
        request.state.tx_id = payment_proof
        request.state.payment_verified = True
        request.state.agent_mode = False

        response = await call_next(request)
        return add_cors_headers(response, origin)
