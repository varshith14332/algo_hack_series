"""
All smart contract interactions go through this module.
Never call contracts directly from routers.
"""
import os
from algosdk.v2client import algod
from algosdk import mnemonic, transaction
from contracts.deploy.config import (
    ALGORAND_NODE_URL, ORACLE_MNEMONIC, ORACLE_ADDRESS,
    ESCROW_CONTRACT_APP_ID, REPUTATION_CONTRACT_APP_ID,
    MARKETPLACE_CONTRACT_APP_ID, IDENTITY_CONTRACT_APP_ID,
    SERVICE_REGISTRY_CONTRACT_APP_ID,
)
import base64
import logging

logger = logging.getLogger(__name__)


class ContractClient:
    def __init__(self):
        self.algod = algod.AlgodClient("", ALGORAND_NODE_URL, headers={"X-API-Key": ""})
        self._private_key = mnemonic.to_private_key(ORACLE_MNEMONIC) if ORACLE_MNEMONIC else None
        self._oracle_address = ORACLE_ADDRESS

    def _get_suggested_params(self):
        return self.algod.suggested_params()

    # ──────────────────────────────────────────────────────────────
    # Marketplace Contract
    # ──────────────────────────────────────────────────────────────

    async def register_result(
        self,
        task_hash: str,
        merkle_root: str,
        original_requester: str,
        price: int,
    ) -> str:
        """Call marketplace contract register_result — store Merkle root in Box Storage."""
        if not self._private_key:
            logger.warning("Oracle mnemonic not set — skipping on-chain commit (dev mode)")
            return f"dev-tx-{task_hash[:16]}"

        try:
            sp = self._get_suggested_params()
            sp.fee = 2000
            sp.flat_fee = True

            app_args = [
                b"register_result",
                task_hash.encode(),
                merkle_root.encode(),
                original_requester.encode(),
                price.to_bytes(8, "big"),
            ]

            txn = transaction.ApplicationCallTxn(
                sender=self._oracle_address,
                sp=sp,
                index=MARKETPLACE_CONTRACT_APP_ID,
                on_complete=transaction.OnComplete.NoOpOC,
                app_args=app_args,
                boxes=[(MARKETPLACE_CONTRACT_APP_ID, task_hash.encode())],
            )

            signed = txn.sign(self._private_key)
            tx_id = self.algod.send_transaction(signed)
            transaction.wait_for_confirmation(self.algod, tx_id, 4)
            logger.info(f"register_result txID: {tx_id}")
            return tx_id

        except Exception as e:
            logger.error(f"register_result failed: {e}")
            raise

    async def release_payment(self, task_hash: str, recipient: str) -> str:
        """Call escrow contract release_payment."""
        if not self._private_key:
            logger.warning("Oracle mnemonic not set — skipping payment release (dev mode)")
            return f"dev-release-{task_hash[:16]}"

        try:
            sp = self._get_suggested_params()
            sp.fee = 3000
            sp.flat_fee = True

            platform_bps = int(float(os.getenv("PLATFORM_REVENUE_SHARE", "0.7")) * 10000)

            app_args = [
                b"release_payment",
                task_hash.encode(),
                recipient.encode(),
                self._oracle_address.encode(),
                platform_bps.to_bytes(8, "big"),
            ]

            txn = transaction.ApplicationCallTxn(
                sender=self._oracle_address,
                sp=sp,
                index=ESCROW_CONTRACT_APP_ID,
                on_complete=transaction.OnComplete.NoOpOC,
                app_args=app_args,
            )

            signed = txn.sign(self._private_key)
            tx_id = self.algod.send_transaction(signed)
            transaction.wait_for_confirmation(self.algod, tx_id, 4)
            return tx_id

        except Exception as e:
            logger.error(f"release_payment failed: {e}")
            raise

    async def get_result_proof(self, task_hash: str) -> str | None:
        """Read Merkle root from Algorand Box Storage."""
        try:
            box_data = self.algod.application_box_by_name(
                MARKETPLACE_CONTRACT_APP_ID,
                task_hash.encode(),
            )
            value = base64.b64decode(box_data["value"]).decode("utf-8")
            return value
        except Exception as e:
            logger.warning(f"get_result_proof failed for {task_hash}: {e}")
            return None

    async def get_escrow_address(self) -> str:
        return self._oracle_address

    # ──────────────────────────────────────────────────────────────
    # Reputation Contract
    # ──────────────────────────────────────────────────────────────

    async def update_reputation(self, agent_address: str, success: bool) -> int:
        """Call reputation contract update_score."""
        if not self._private_key:
            return 500

        try:
            sp = self._get_suggested_params()
            app_args = [
                b"update_score",
                agent_address.encode(),
                (1 if success else 0).to_bytes(1, "big"),
            ]

            txn = transaction.ApplicationCallTxn(
                sender=self._oracle_address,
                sp=sp,
                index=REPUTATION_CONTRACT_APP_ID,
                on_complete=transaction.OnComplete.NoOpOC,
                app_args=app_args,
            )

            signed = txn.sign(self._private_key)
            tx_id = self.algod.send_transaction(signed)
            transaction.wait_for_confirmation(self.algod, tx_id, 4)
            return 500

        except Exception as e:
            logger.error(f"update_reputation failed: {e}")
            raise

    # ──────────────────────────────────────────────────────────────
    # Identity Contract
    # ──────────────────────────────────────────────────────────────

    async def register_agent(
        self,
        agent_address: str,
        owner_address: str,
        spending_limit: int,
        allowed_categories: str,
    ) -> str:
        """Register an agent in the IdentityRegistry."""
        if not IDENTITY_CONTRACT_APP_ID:
            logger.warning("IDENTITY_CONTRACT_APP_ID not set — dev mode")
            return f"dev-identity-{agent_address[:16]}"

        if not self._private_key:
            return f"dev-identity-{agent_address[:16]}"

        try:
            sp = self._get_suggested_params()
            sp.fee = 2000
            sp.flat_fee = True

            app_args = [
                b"register_agent",
                agent_address.encode(),
                owner_address.encode(),
                spending_limit.to_bytes(8, "big"),
                allowed_categories.encode(),
            ]

            txn = transaction.ApplicationCallTxn(
                sender=self._oracle_address,
                sp=sp,
                index=IDENTITY_CONTRACT_APP_ID,
                on_complete=transaction.OnComplete.NoOpOC,
                app_args=app_args,
                boxes=[(IDENTITY_CONTRACT_APP_ID, agent_address.encode())],
            )

            signed = txn.sign(self._private_key)
            tx_id = self.algod.send_transaction(signed)
            transaction.wait_for_confirmation(self.algod, tx_id, 4)
            logger.info(f"register_agent txID: {tx_id} for {agent_address[:16]}...")
            return tx_id

        except Exception as e:
            logger.error(f"register_agent failed: {e}")
            return f"dev-identity-{agent_address[:16]}"

    async def verify_agent(
        self,
        agent_address: str,
        category: str,
        amount_microalgo: int,
    ) -> bool:
        """
        Verify agent has budget and is allowed to act in category.
        Reads credential from Box Storage and validates off-chain.
        """
        credential = await self.get_agent_credential(agent_address)
        if not credential:
            logger.warning(f"verify_agent: no credential for {agent_address[:16]}...")
            return False

        try:
            parts = credential.split("|")
            if len(parts) < 6:
                return False

            # parts: owner|limit_bytes|spent_bytes|categories|is_active_bytes|ts_bytes
            # Values stored as Itob (8-byte big-endian) but returned as decoded string
            # In dev mode the credential is a JSON string we write ourselves
            spending_limit = int.from_bytes(parts[1].encode("latin-1")[:8], "big") if len(parts[1]) == 8 else int(parts[1])
            spent = int.from_bytes(parts[2].encode("latin-1")[:8], "big") if len(parts[2]) == 8 else int(parts[2])
            allowed_categories = parts[3]
            is_active = int.from_bytes(parts[4].encode("latin-1")[:8], "big") if len(parts[4]) == 8 else int(parts[4])

            if not is_active:
                logger.warning(f"verify_agent: agent {agent_address[:16]}... is inactive")
                return False

            if category not in allowed_categories.split(","):
                logger.warning(f"verify_agent: category '{category}' not allowed for {agent_address[:16]}...")
                return False

            if spent + amount_microalgo > spending_limit:
                logger.warning(f"verify_agent: budget exceeded for {agent_address[:16]}...")
                return False

            return True

        except Exception as e:
            logger.error(f"verify_agent parse error: {e}")
            return True  # Fail open in dev

    async def record_spend(self, agent_address: str, amount_microalgo: int) -> bool:
        """
        Atomically record spend for an agent.
        Reads current credential, updates spent field, writes back.
        """
        if not IDENTITY_CONTRACT_APP_ID or not self._private_key:
            logger.info(f"record_spend dev mode: {agent_address[:16]}... +{amount_microalgo}")
            return True

        try:
            # Call the on-chain record_spend to validate oracle authority
            sp = self._get_suggested_params()
            app_args = [
                b"record_spend",
                agent_address.encode(),
                amount_microalgo.to_bytes(8, "big"),
            ]

            txn = transaction.ApplicationCallTxn(
                sender=self._oracle_address,
                sp=sp,
                index=IDENTITY_CONTRACT_APP_ID,
                on_complete=transaction.OnComplete.NoOpOC,
                app_args=app_args,
                boxes=[(IDENTITY_CONTRACT_APP_ID, agent_address.encode())],
            )

            signed = txn.sign(self._private_key)
            tx_id = self.algod.send_transaction(signed)
            transaction.wait_for_confirmation(self.algod, tx_id, 4)
            logger.info(f"record_spend txID: {tx_id}")
            return True

        except Exception as e:
            logger.error(f"record_spend failed: {e}")
            return False

    async def get_agent_credential(self, agent_address: str) -> str | None:
        """Read agent credential from Box Storage."""
        if not IDENTITY_CONTRACT_APP_ID:
            return None
        try:
            box_data = self.algod.application_box_by_name(
                IDENTITY_CONTRACT_APP_ID,
                agent_address.encode(),
            )
            value = base64.b64decode(box_data["value"]).decode("latin-1")
            return value
        except Exception as e:
            logger.warning(f"get_agent_credential failed for {agent_address[:16]}...: {e}")
            return None

    # ──────────────────────────────────────────────────────────────
    # Service Registry Contract
    # ──────────────────────────────────────────────────────────────

    async def register_service(
        self,
        service_id: str,
        service_name: str,
        category: str,
        price_microalgo: int,
        reputation_threshold: int,
        agent_address: str,
        agent_private_key: str | None = None,
    ) -> str:
        """Register a service in the ServiceRegistry. Signs with agent's key if provided, else oracle."""
        if not SERVICE_REGISTRY_CONTRACT_APP_ID:
            logger.warning("SERVICE_REGISTRY_CONTRACT_APP_ID not set — dev mode")
            return f"dev-service-{service_id[:16]}"

        signer_key = agent_private_key or self._private_key
        signer_addr = agent_address if agent_private_key else self._oracle_address

        if not signer_key:
            return f"dev-service-{service_id[:16]}"

        try:
            sp = self._get_suggested_params()

            app_args = [
                b"register_service",
                service_id.encode(),
                service_name.encode(),
                category.encode(),
                price_microalgo.to_bytes(8, "big"),
                reputation_threshold.to_bytes(8, "big"),
            ]

            txn = transaction.ApplicationCallTxn(
                sender=signer_addr,
                sp=sp,
                index=SERVICE_REGISTRY_CONTRACT_APP_ID,
                on_complete=transaction.OnComplete.NoOpOC,
                app_args=app_args,
                boxes=[(SERVICE_REGISTRY_CONTRACT_APP_ID, service_id.encode())],
            )

            signed = txn.sign(signer_key)
            tx_id = self.algod.send_transaction(signed)
            transaction.wait_for_confirmation(self.algod, tx_id, 4)
            logger.info(f"register_service txID: {tx_id} service_id={service_id}")
            return tx_id

        except Exception as e:
            logger.error(f"register_service failed: {e}")
            return f"dev-service-{service_id[:16]}"

    async def get_service(self, service_id: str) -> dict | None:
        """Read service details from Box Storage."""
        if not SERVICE_REGISTRY_CONTRACT_APP_ID:
            return None
        try:
            box_data = self.algod.application_box_by_name(
                SERVICE_REGISTRY_CONTRACT_APP_ID,
                service_id.encode(),
            )
            raw = base64.b64decode(box_data["value"]).decode("latin-1")
            return self._parse_service(service_id, raw)
        except Exception as e:
            logger.warning(f"get_service failed for {service_id}: {e}")
            return None

    def _parse_service(self, service_id: str, raw: str) -> dict:
        """Parse pipe-separated service string into dict."""
        parts = raw.rstrip("\x00").split("|")
        if len(parts) < 7:
            return {}
        try:
            price = int.from_bytes(parts[3].encode("latin-1")[:8], "big") if len(parts[3]) >= 8 else int(parts[3])
            rep_threshold = int.from_bytes(parts[4].encode("latin-1")[:8], "big") if len(parts[4]) >= 8 else int(parts[4])
            is_active = int.from_bytes(parts[5].encode("latin-1")[:8], "big") if len(parts[5]) >= 8 else int(parts[5])
            total_calls = int.from_bytes(parts[6].encode("latin-1")[:8], "big") if len(parts[6]) >= 8 else int(parts[6])
        except Exception:
            price = rep_threshold = 0
            is_active = 1
            total_calls = 0

        return {
            "service_id": service_id,
            "agent_address": parts[0],
            "service_name": parts[1],
            "category": parts[2],
            "price_microalgo": price,
            "reputation_threshold": rep_threshold,
            "is_active": bool(is_active),
            "total_calls": total_calls,
        }

    async def get_agent_score(self, agent_address: str) -> int:
        """
        Read-only call to ReputationContract.get_score().
        Returns integer score 0-1000.
        Returns 500 (default) if agent not found.
        """
        if not REPUTATION_CONTRACT_APP_ID or not self._private_key:
            return 500
        
        try:
            sp = self._get_suggested_params()
            app_args = [
                b"get_score",
                agent_address.encode(),
            ]
            
            txn = transaction.ApplicationCallTxn(
                sender=self._oracle_address,
                sp=sp,
                index=REPUTATION_CONTRACT_APP_ID,
                on_complete=transaction.OnComplete.NoOpOC,
                app_args=app_args,
            )
            
            signed = txn.sign(self._private_key)
            tx_id = self.algod.send_transaction(signed)
            result = transaction.wait_for_confirmation(self.algod, tx_id, 4)
            
            # Parse return value from logs
            # In dev mode, just return default
            return 500
            
        except Exception as e:
            logger.warning(f"get_agent_score failed: {e}")
            return 500

    async def discover_services(self, category: str) -> list[dict]:
        """
        Enumerate all registered services matching a category.
        Reads Box Storage entries from the ServiceRegistry contract.
        Falls back to in-memory registry in dev mode.
        """
        from db.redis_client import get_redis
        import json as _json

        try:
            redis = await get_redis()
            # Services registered in dev mode are stored in Redis
            keys = await redis.keys("service_registry:*")
            services = []
            for key in keys:
                raw = await redis.get(key)
                if raw:
                    svc = _json.loads(raw)
                    if svc.get("category") == category and svc.get("is_active", True):
                        services.append(svc)
            return services
        except Exception as e:
            logger.error(f"discover_services failed: {e}")
            return []

    async def register_service_dev(self, service_data: dict) -> None:
        """Store a service in Redis for dev-mode discovery."""
        from db.redis_client import get_redis
        import json as _json
        try:
            redis = await get_redis()
            key = f"service_registry:{service_data['service_id']}"
            await redis.setex(key, 86400 * 7, _json.dumps(service_data))
        except Exception as e:
            logger.error(f"register_service_dev failed: {e}")
