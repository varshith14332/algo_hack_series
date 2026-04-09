from algosdk.v2client import algod, indexer
from algosdk import mnemonic
from config import settings
from db.redis_client import get_redis
import base64
import logging

logger = logging.getLogger(__name__)


class AlgorandService:
    def __init__(self):
        self.algod_client = algod.AlgodClient(
            "", settings.ALGORAND_NODE_URL,
            headers={"X-API-Key": ""}
        )
        self.indexer_client = indexer.IndexerClient(
            "", settings.ALGORAND_INDEXER_URL,
            headers={"X-API-Key": ""}
        )

    async def verify_transaction(self, tx_id: str, task_hash: str) -> bool:
        try:
            redis = await get_redis()

            # Replay attack prevention
            replay_key = f"used_tx:{tx_id}"
            if await redis.exists(replay_key):
                logger.warning(f"Replay attack detected: {tx_id}")
                return False

            # Fetch transaction from Algorand Indexer
            tx_info = self.indexer_client.transaction(tx_id)
            tx = tx_info.get("transaction", {})

            if not tx:
                return False

            pt = tx.get("payment-transaction", {})
            receiver = pt.get("receiver", "")
            amount_microalgo = pt.get("amount", 0)
            note_b64 = tx.get("note", "")

            try:
                note = base64.b64decode(note_b64).decode("utf-8")
            except Exception:
                note = ""

            expected_note = f"neuralledger:{task_hash}"
            escrow_address = settings.ORACLE_ADDRESS

            min_payment = int(settings.CACHED_TASK_PRICE_ALGO * 1_000_000)

            checks = [
                tx.get("tx-type") == "pay",
                receiver == escrow_address,
                amount_microalgo >= min_payment,
                note == expected_note,
            ]

            if all(checks):
                # Mark tx as used — 30 day TTL (replay prevention)
                await redis.setex(replay_key, 2592000, "1")
                return True

            logger.warning(f"Transaction verification failed — checks: {checks}")
            return False

        except Exception as e:
            logger.error(f"Transaction verification error: {e}")
            return False

    def get_oracle_account(self):
        private_key = mnemonic.to_private_key(settings.ORACLE_MNEMONIC)
        return private_key, settings.ORACLE_ADDRESS

    async def get_account_balance(self, address: str) -> float:
        try:
            info = self.algod_client.account_info(address)
            return info.get("amount", 0) / 1_000_000
        except Exception as e:
            logger.error(f"Failed to get balance for {address}: {e}")
            return 0.0

    def validate_address(self, address: str) -> bool:
        """Validate 58-character Algorand address format."""
        try:
            from algosdk import encoding
            return encoding.is_valid_address(address)
        except Exception:
            return False
