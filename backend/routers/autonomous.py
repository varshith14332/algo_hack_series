"""
Autonomous agent pipeline router.

POST /api/autonomous/run   — launch master agent for a goal
GET  /api/autonomous/status/{task_id} — poll progress
GET  /api/autonomous/audit/{task_id}  — full audit trail once done
"""
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from services.algorand_service import AlgorandService
from agents.master_agent import MasterAgent
from datetime import datetime, timezone
import uuid
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
algorand = AlgorandService()

# Rate limit: 3 concurrent autonomous runs per owner (checked in Redis)
CONCURRENT_LIMIT = 3
CONCURRENT_WINDOW = 300  # 5 minutes

_master_agent: MasterAgent | None = None


def _get_master_agent() -> MasterAgent:
    global _master_agent
    if _master_agent is None:
        _master_agent = MasterAgent()
    return _master_agent


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _envelope(success: bool, data=None, error=None):
    return {"success": success, "data": data, "error": error, "timestamp": _now()}


class RunRequest(BaseModel):
    goal: str
    budget_algo: float
    owner_address: str

    @field_validator("owner_address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        if len(v) != 58:
            raise ValueError("owner_address must be a 58-character Algorand address")
        return v

    @field_validator("budget_algo")
    @classmethod
    def validate_budget(cls, v: float) -> float:
        if v < 0.5 or v > 50:
            raise ValueError("budget_algo must be between 0.5 and 50")
        return v


async def _check_concurrent_limit(owner_address: str) -> bool:
    """Return True if owner is within the concurrent run limit."""
    try:
        from db.redis_client import get_redis
        redis = await get_redis()
        key = f"autonomous_runs:{owner_address}"
        count = await redis.get(key)
        if count and int(count) >= CONCURRENT_LIMIT:
            return False
        pipe = redis.pipeline()
        await pipe.incr(key)
        await pipe.expire(key, CONCURRENT_WINDOW)
        await pipe.execute()
        return True
    except Exception:
        return True  # Fail open


async def _decrement_concurrent(owner_address: str):
    try:
        from db.redis_client import get_redis
        redis = await get_redis()
        key = f"autonomous_runs:{owner_address}"
        await redis.decr(key)
    except Exception:
        pass


async def _run_pipeline(task_id: str, goal: str, budget_algo: float, owner_address: str):
    """Background task: run the master agent pipeline."""
    try:
        agent = _get_master_agent()
        await agent.run(
            goal=goal,
            budget_algo=budget_algo,
            owner_address=owner_address,
            task_id=task_id,
        )
    except Exception as e:
        logger.error(f"[autonomous] Pipeline failed for task {task_id}: {e}")
        try:
            from db.redis_client import get_redis
            redis = await get_redis()
            await redis.setex(
                f"autonomous:{task_id}",
                3600 * 24,
                json.dumps({
                    "status": "failed",
                    "current_step": "Error",
                    "progress_percent": 0,
                    "audit_trail": [],
                    "error": str(e),
                }),
            )
        except Exception:
            pass
    finally:
        await _decrement_concurrent(owner_address)


@router.post("/run")
async def run_autonomous(req: RunRequest, background_tasks: BackgroundTasks):
    """
    Launch the master agent pipeline for a goal.
    Does NOT require x402 payment — the master agent funds itself internally.
    Rate limited to 3 concurrent runs per owner_address.
    """
    if not algorand.validate_address(req.owner_address):
        return JSONResponse(
            status_code=400,
            content=_envelope(False, error="Invalid Algorand address format"),
        )

    allowed = await _check_concurrent_limit(req.owner_address)
    if not allowed:
        return JSONResponse(
            status_code=429,
            content=_envelope(
                False,
                error=f"Rate limit: max {CONCURRENT_LIMIT} concurrent autonomous runs per address (5-minute window)",
            ),
        )

    task_id = str(uuid.uuid4())
    agent = _get_master_agent()

    # Persist initial state immediately so polling works right away
    try:
        from db.redis_client import get_redis
        redis = await get_redis()
        await redis.setex(
            f"autonomous:{task_id}",
            3600 * 24,
            json.dumps({
                "status": "running",
                "current_step": "Initialising master agent",
                "progress_percent": 0,
                "audit_trail": [],
            }),
        )
    except Exception:
        pass

    background_tasks.add_task(
        _run_pipeline,
        task_id=task_id,
        goal=req.goal,
        budget_algo=req.budget_algo,
        owner_address=req.owner_address,
    )

    # Estimate cost: research ~0.3, analysis ~0.4, writing ~0.2
    estimated = min(req.budget_algo * 0.45, req.budget_algo)

    return JSONResponse(content=_envelope(True, {
        "task_id": task_id,
        "status": "running",
        "master_agent_address": agent.address,
        "estimated_cost_algo": round(estimated, 4),
        "budget_algo": req.budget_algo,
    }))


@router.get("/status/{task_id}")
async def get_status(task_id: str):
    """Poll current status: progress, current step, partial audit trail, result if done."""
    try:
        from db.redis_client import get_redis
        redis = await get_redis()
        raw = await redis.get(f"autonomous:{task_id}")
        if not raw:
            return JSONResponse(
                status_code=404,
                content=_envelope(False, error="Task not found"),
            )
        data = json.loads(raw)
        return JSONResponse(content=_envelope(True, data))
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=_envelope(False, error=str(e)),
        )


@router.get("/audit/{task_id}")
async def get_audit(task_id: str):
    """Return the complete audit trail for a finished task."""
    try:
        from db.redis_client import get_redis
        redis = await get_redis()
        raw = await redis.get(f"autonomous:{task_id}")
        if not raw:
            return JSONResponse(
                status_code=404,
                content=_envelope(False, error="Task not found"),
            )
        data = json.loads(raw)
        return JSONResponse(content=_envelope(True, {
            "task_id": task_id,
            "status": data.get("status"),
            "audit_trail": data.get("audit_trail", []),
            "result": data.get("result"),
        }))
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=_envelope(False, error=str(e)),
        )
