from fastapi import APIRouter, Request, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.cache_service import CacheService
from agents.orchestrator import AgentOrchestrator
from datetime import datetime, timezone
import hashlib
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Lazy singletons — instantiated on first request, not at import time
_cache: CacheService | None = None
_orchestrator: AgentOrchestrator | None = None

def get_cache() -> CacheService:
    global _cache
    if _cache is None:
        _cache = CacheService()
    return _cache

def get_orchestrator() -> AgentOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator


def _now():
    return datetime.now(timezone.utc).isoformat()


def _envelope(success: bool, data=None, error=None):
    return {"success": success, "data": data, "error": error, "timestamp": _now()}


class HashRequest(BaseModel):
    content: str


@router.post("/run")
async def run_task(
    request: Request,
    background_tasks: BackgroundTasks,
    task_type: str = Form(...),
    prompt: str = Form(...),
    file: UploadFile | None = File(None),
):
    """Protected by X402Middleware — payment_verified is guaranteed True here."""
    # Validate file upload
    file_content = None
    if file:
        if file.content_type != "application/pdf":
            return JSONResponse(
                status_code=400,
                content=_envelope(False, error="Only PDF files accepted"),
            )
        raw = await file.read()
        if len(raw) > 10 * 1024 * 1024:
            return JSONResponse(
                status_code=400,
                content=_envelope(False, error="File exceeds 10MB limit"),
            )
        try:
            import fitz
            doc = fitz.open(stream=raw, filetype="pdf")
            file_content = "\n".join(page.get_text() for page in doc)
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return JSONResponse(
                status_code=400,
                content=_envelope(False, error="Failed to extract PDF content"),
            )

    task_text = f"{task_type}: {prompt}"
    if file_content:
        task_text += f"\n\nDocument content:\n{file_content[:3000]}"

    task_hash = request.headers.get("X-Task-Hash", "")
    tx_id = request.headers.get("X-Payment-Proof", "")
    requester = request.headers.get("X-Wallet-Address", "unknown")
    task_id = str(uuid.uuid4())

    # Check semantic cache before spawning pipeline
    cached = await get_cache().check_semantic(task_text)
    if cached:
        cached_result = await get_cache().get(cached["task_hash"])
        if cached_result:
            return JSONResponse(content=_envelope(True, {
                "task_id": task_id,
                "status": "cache_hit",
                "result": cached_result["result"],
                "merkle_root": cached_result["merkle_root"],
                "ipfs_cid": cached_result["ipfs_cid"],
                "similarity_score": cached["score"],
                "from_cache": True,
            }))

    # Run agent pipeline in background
    background_tasks.add_task(
        get_orchestrator().run,
        task_id=task_id,
        task_hash=task_hash,
        task_text=task_text,
        task_type=task_type,
        requester=requester,
        tx_id=tx_id,
        file_content=file_content,
    )

    return JSONResponse(content=_envelope(True, {
        "task_id": task_id,
        "status": "processing",
        "message": f"Task queued. Poll /api/tasks/result/{task_id} for updates.",
    }))


@router.get("/result/{task_id}")
async def get_result(task_id: str):
    from db.redis_client import get_redis
    import json
    redis = await get_redis()
    data = await redis.get(f"task_result:{task_id}")
    if data:
        return JSONResponse(content=_envelope(True, json.loads(data)))
    return JSONResponse(content=_envelope(True, {"status": "processing", "task_id": task_id}))


@router.post("/hash")
async def compute_hash(payload: HashRequest):
    """Compute task hash so frontend can attach it to the x402 flow."""
    content = payload.content
    task_hash = hashlib.sha256(content.encode()).hexdigest()
    is_cached = await get_cache().check_exact(task_hash)
    semantic = await get_cache().check_semantic(content)

    return JSONResponse(content=_envelope(True, {
        "task_hash": task_hash,
        "is_cached": is_cached or bool(semantic),
        "semantic_match": semantic,
    }))


@router.get("/history/{wallet_address}")
async def task_history(wallet_address: str):
    """Return all tasks for a wallet address."""
    from services.algorand_service import AlgorandService
    algo = AlgorandService()
    if not algo.validate_address(wallet_address):
        return JSONResponse(
            status_code=400,
            content=_envelope(False, error="Invalid wallet address"),
        )

    from db.redis_client import get_redis
    import json
    redis = await get_redis()
    keys = await redis.keys(f"wallet_tasks:{wallet_address}:*")
    tasks = []
    for key in keys:
        data = await redis.get(key)
        if data:
            tasks.append(json.loads(data))

    return JSONResponse(content=_envelope(True, {"tasks": tasks}))
