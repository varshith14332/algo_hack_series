from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.algorand_service import AlgorandService
from datetime import datetime, timezone
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
algorand = AlgorandService()


def _now():
    return datetime.now(timezone.utc).isoformat()


def _envelope(success: bool, data=None, error=None):
    return {"success": success, "data": data, "error": error, "timestamp": _now()}


class ReleasePaymentRequest(BaseModel):
    task_hash: str
    recipient: str
    tx_id: str


@router.post("/release")
async def release_payment(payload: ReleasePaymentRequest):
    """Oracle-triggered payment release after Merkle root is committed."""
    if not algorand.validate_address(payload.recipient):
        return JSONResponse(
            status_code=400,
            content=_envelope(False, error="Invalid recipient address"),
        )

    try:
        from contracts.deploy.contract_client import ContractClient
        client = ContractClient()
        tx_id = await client.release_payment(
            task_hash=payload.task_hash,
            recipient=payload.recipient,
        )
        return JSONResponse(content=_envelope(True, {"release_tx_id": tx_id}))
    except Exception as e:
        logger.error(f"Payment release error: {e}")
        return JSONResponse(
            status_code=500,
            content=_envelope(False, error=str(e)),
        )


@router.get("/status/{tx_id}")
async def payment_status(tx_id: str):
    """Check if a payment transaction has been verified."""
    from db.redis_client import get_redis
    redis = await get_redis()
    used = await redis.exists(f"used_tx:{tx_id}")
    return JSONResponse(content=_envelope(True, {
        "tx_id": tx_id,
        "verified": bool(used),
    }))


@router.get("/balance/{address}")
async def get_balance(address: str):
    if not algorand.validate_address(address):
        return JSONResponse(
            status_code=400,
            content=_envelope(False, error="Invalid address"),
        )
    balance = await algorand.get_account_balance(address)
    return JSONResponse(content=_envelope(True, {"address": address, "balance_algo": balance}))
