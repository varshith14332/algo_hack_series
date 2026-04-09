from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.merkle_service import MerkleService
from services.cache_service import CacheService
from datetime import datetime, timezone
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
merkle = MerkleService()
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


class VerifyProofRequest(BaseModel):
    leaf_data: str
    proof: list[dict]
    root: str


@router.get("/result/{task_hash}")
async def verify_result(task_hash: str):
    """Fetch Merkle root from Algorand Box Storage for a task hash."""
    try:
        import sys, os
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from contracts.deploy.contract_client import ContractClient
        client = ContractClient()
        proof_data = await client.get_result_proof(task_hash)
    except Exception:
        proof_data = None

    cached = await get_cache().get(task_hash)

    if not proof_data and not cached:
        return JSONResponse(
            status_code=404,
            content=_envelope(False, error="Result not found on-chain or in cache"),
        )

    return JSONResponse(content=_envelope(True, {
        "task_hash": task_hash,
        "on_chain": proof_data is not None,
        "proof_data": proof_data,
        "cached_result": cached,
    }))


@router.post("/proof")
async def verify_merkle_proof(payload: VerifyProofRequest):
    """Client-side Merkle proof verification (server mirrors client logic)."""
    valid = merkle.verify_proof(
        leaf_data=payload.leaf_data,
        proof=payload.proof,
        root=payload.root,
    )
    return JSONResponse(content=_envelope(True, {
        "valid": valid,
        "leaf_data": payload.leaf_data[:50] + "..." if len(payload.leaf_data) > 50 else payload.leaf_data,
        "root": payload.root,
    }))
