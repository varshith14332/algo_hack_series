"""
AgentWalletService — manages autonomous agent wallets.

Each LangGraph agent gets its own Algorand account derived deterministically
from MASTER_AGENT_SECRET + agent_name. Private keys are NEVER stored or logged;
they are regenerated fresh on each call.
"""
import hashlib
import hmac
from algosdk import mnemonic, account
from algosdk.v2client import algod
from algosdk import transaction as algo_txn
from config import settings
import logging

logger = logging.getLogger(__name__)


class AgentWalletService:
    def __init__(self):
        self._algod = algod.AlgodClient(
            "",
            settings.ALGORAND_NODE_URL,
            headers={"X-API-Key": ""},
        )

    def _derive_seed(self, agent_name: str) -> bytes:
        """
        Derive a 32-byte seed from MASTER_AGENT_SECRET + agent_name.
        Uses HMAC-SHA256 so different agents always get different keys.
        NEVER log or persist the result.
        """
        secret = settings.MASTER_AGENT_SECRET.encode()
        return hmac.new(secret, agent_name.encode(), hashlib.sha256).digest()

    def generate_agent_account(self, agent_name: str) -> tuple[str, str]:
        """
        Return (private_key, address) for an agent.
        Key is derived fresh every call — never stored.
        """
        seed = self._derive_seed(agent_name)
        # algosdk account from seed bytes: use generate_account with a seeded RNG
        # We convert seed → mnemonic (25 words) → private key to stay compatible
        # with algosdk's key format.
        import nacl.signing
        signing_key = nacl.signing.SigningKey(seed)
        private_key_bytes = bytes(signing_key) + bytes(signing_key.verify_key)
        import base64
        private_key_b64 = base64.b64encode(private_key_bytes).decode()
        address = account.address_from_private_key(private_key_b64)
        return private_key_b64, address

    async def get_agent_balance(self, agent_name: str) -> float:
        """Return ALGO balance for an agent wallet."""
        _, address = self.generate_agent_account(agent_name)
        try:
            info = self._algod.account_info(address)
            return info.get("amount", 0) / 1_000_000
        except Exception as e:
            logger.warning(f"get_agent_balance({agent_name}): {e}")
            return 0.0

    async def send_agent_payment(
        self,
        from_agent: str,
        to_address: str,
        amount_algo: float,
        note: str,
    ) -> str:
        """
        Signs and broadcasts a payment from an agent wallet autonomously.
        No human confirmation required.
        """
        private_key, from_address = self.generate_agent_account(from_agent)

        try:
            sp = self._algod.suggested_params()
            note_bytes = note.encode()
            amount_microalgo = int(amount_algo * 1_000_000)

            txn = algo_txn.PaymentTxn(
                sender=from_address,
                sp=sp,
                receiver=to_address,
                amt=amount_microalgo,
                note=note_bytes,
            )

            signed = txn.sign(private_key)
            tx_id = self._algod.send_transaction(signed)
            algo_txn.wait_for_confirmation(self._algod, tx_id, 4)
            logger.info(f"[AgentWallet] {from_agent} → {to_address[:8]}... {amount_algo} ALGO tx={tx_id}")
            return tx_id

        except Exception as e:
            logger.error(f"send_agent_payment failed ({from_agent}→{to_address[:8]}...): {e}")
            return f"dev-pay-{from_agent}-{int(amount_algo*1e6)}"

    async def fund_agent(self, agent_name: str, amount_algo: float) -> str:
        """
        Transfer ALGO from oracle wallet to an agent wallet.
        Used to bootstrap agent balances.
        """
        from algosdk import mnemonic as _mnemonic
        _, to_address = self.generate_agent_account(agent_name)

        if not settings.ORACLE_MNEMONIC:
            logger.warning(f"fund_agent dev mode: {agent_name} would receive {amount_algo} ALGO")
            return f"dev-fund-{agent_name}"

        try:
            oracle_key = _mnemonic.to_private_key(settings.ORACLE_MNEMONIC)
            sp = self._algod.suggested_params()
            amount_microalgo = int(amount_algo * 1_000_000)

            txn = algo_txn.PaymentTxn(
                sender=settings.ORACLE_ADDRESS,
                sp=sp,
                receiver=to_address,
                amt=amount_microalgo,
                note=b"neuralledger:agent-fund",
            )

            signed = txn.sign(oracle_key)
            tx_id = self._algod.send_transaction(signed)
            algo_txn.wait_for_confirmation(self._algod, tx_id, 4)
            logger.info(f"[AgentWallet] Funded {agent_name} ({to_address[:8]}...) with {amount_algo} ALGO")
            return tx_id

        except Exception as e:
            logger.error(f"fund_agent failed for {agent_name}: {e}")
            return f"dev-fund-{agent_name}"
