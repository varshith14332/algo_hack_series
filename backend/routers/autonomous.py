"""
Autonomous Agent Pipeline Router

Allows users to launch fully autonomous multi-agent workflows with budget control.
"""
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from algosdk import encoding
from agents.master_agent import MasterAgent
from db.redis_client import get_redis
from services.agent_wallet_service import AgentWalletService
from config import settings
from datetime import datetime, timezone
import json
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class AutonomousRunRequest(BaseModel):
    goal: str
    budget_algo: float
    owner_address: str

    @field_validator("goal")
    @classmethod
    def goal_not_empty(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError("Goal must be at least 10 characters")
        if len(v) > 1000:
            raise ValueError("Goal must be under 1000 characters")
        return v.strip()

    @field_validator("budget_algo")
    @classmethod
    def budget_in_range(cls, v):
        if v < 0.5 or v > 50:
            raise ValueError("Budget must be between 0.5 and 50 ALGO")
        return v

    @field_validator("owner_address")
    @classmethod
    def valid_algorand_address(cls, v):
        if not encoding.is_valid_address(v):
            raise ValueError("Invalid Algorand address")
        return v


@router.post("/run")
async def run_autonomous_pipeline(
    request: AutonomousRunRequest,
    background_tasks: BackgroundTasks,
):
    """
    Launch an autonomous agent pipeline.
    
    Rate limit: max 3 concurrent runs per owner address.
    
    Returns:
        task_id: unique identifier for polling status
        master_agent_address: the agent's on-chain identity
        estimated_cost_algo: rough estimate of total cost
    """
    redis = await get_redis()
    
    # Rate limit check
    rate_key = f"rate_limit:autonomous:{request.owner_address}"
    count = await redis.get(rate_key)
    if count and int(count) >= 3:
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "error": "Max 3 concurrent autonomous runs per address",
                "data": None,
                "timestamp": _utc_now(),
            }
        )
    
    # Increment rate limit counter
    await redis.incr(rate_key)
    await redis.expire(rate_key, 300)  # 5 minutes
    
    # Generate task ID
    task_id = str(uuid.uuid4())
    
    # Store initial status
    initial_status = {
        "status": "initializing",
        "progress_percent": 0,
        "current_step": "Setting up agent wallets",
        "audit_trail": [],
        "result": None,
        "goal": request.goal,
        "budget_algo": request.budget_algo,
    }
    await redis.setex(
        f"autonomous:{task_id}",
        3600,  # 1 hour TTL
        json.dumps(initial_status)
    )
    
    # Get master agent address (without running full pipeline yet)
    wallet_service = AgentWalletService()
    master_address = await wallet_service.get_address("master")
    
    # Launch background task
    background_tasks.add_task(
        _run_autonomous_pipeline,
        task_id,
        request.goal,
        request.budget_algo,
        request.owner_address,
    )
    
    return JSONResponse(
        content={
            "success": True,
            "data": {
                "task_id": task_id,
                "status": "initializing",
                "master_agent_address": master_address,
                "estimated_cost_algo": request.budget_algo * 0.4,
                "message": f"Agent pipeline launched. Poll /autonomous/status/{task_id}",
            },
            "error": None,
            "timestamp": _utc_now(),
        }
    )


async def _run_autonomous_pipeline(
    task_id: str,
    goal: str,
    budget_algo: float,
    owner_address: str,
):
    """
    Background task that runs the full pipeline and updates Redis.
    """
    redis = await get_redis()
    
    async def update_status(step: str, progress: int, extra: dict = None):
        try:
            current_str = await redis.get(f"autonomous:{task_id}")
            current = json.loads(current_str) if current_str else {}
            current.update({
                "current_step": step,
                "progress_percent": progress,
            })
            if extra:
                current.update(extra)
            await redis.setex(f"autonomous:{task_id}", 3600, json.dumps(current))
        except Exception as e:
            logger.error(f"update_status failed: {e}")
    
    try:
        await update_status("Initializing agent identity", 5)
        
        agent = MasterAgent(
            user_wallet_address=owner_address,
            budget_algo=budget_algo,
        )
        
        await update_status("Registering on Algorand", 10)
        await agent.initialize()
        
        await update_status("Parsing goal into subtasks", 20)
        
        await update_status("Running agent pipeline", 30)
        result = await agent.run(goal)
        
        await update_status(
            "Pipeline complete",
            100,
            {
                "status": "completed",
                "result": result,
                "audit_trail": result["audit_trail"],
            }
        )
        
        logger.info(f"[Autonomous] Pipeline {task_id} completed successfully")
        
    except Exception as e:
        logger.error(f"[Autonomous] Pipeline {task_id} failed: {e}")
        await update_status(
            "Pipeline failed",
            0,
            {
                "status": "failed",
                "error": str(e),
            }
        )
    
    finally:
        # Decrement rate limit counter
        rate_key = f"rate_limit:autonomous:{owner_address}"
        count = await redis.get(rate_key)
        if count and int(count) > 0:
            await redis.decr(rate_key)


@router.get("/status/{task_id}")
async def get_autonomous_status(task_id: str):
    """
    Poll status of an autonomous pipeline.
    
    Returns current progress, step, and result when complete.
    """
    redis = await get_redis()
    data_str = await redis.get(f"autonomous:{task_id}")
    
    if not data_str:
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": "Task not found",
                "data": None,
                "timestamp": _utc_now(),
            }
        )
    
    data = json.loads(data_str)
    
    return JSONResponse(
        content={
            "success": True,
            "data": data,
            "error": None,
            "timestamp": _utc_now(),
        }
    )


@router.get("/audit/{task_id}")
async def get_autonomous_audit(task_id: str):
    """
    Get audit trail for a completed autonomous pipeline.
    """
    redis = await get_redis()
    data_str = await redis.get(f"autonomous:{task_id}")
    
    if not data_str:
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": "Task not found",
                "data": None,
                "timestamp": _utc_now(),
            }
        )
    
    data = json.loads(data_str)
    audit_trail = data.get("audit_trail", [])
    status = data.get("status", "unknown")
    
    return JSONResponse(
        content={
            "success": True,
            "data": {
                "audit_trail": audit_trail,
                "status": status,
                "note": "Partial trail" if status != "completed" else "Complete",
            },
            "error": None,
            "timestamp": _utc_now(),
        }
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
