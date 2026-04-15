"""
Agent Wallet Service — Deterministic wallet generation for autonomous agents.

SECURITY RULES:
- Never store private keys in memory beyond a single method call
- Never log private keys, mnemonics, or raw signatures
- Generate keys fresh every time from deterministic seed
"""
import hmac
import hashlib
import base64
import logging
from algosdk import account, encoding
from algosdk.v2client import algod
from algosdk.transaction import PaymentTxn, wait_for_confirmation
from algosdk import mnemonic as algo_mnemonic
from config import settings

logger = logging.getLogger(__name__)


class AgentWalletService:
    def __init__(self):
        self.algod_client = algod.AlgodClient(
            "", settings.ALGORAND_NODE_URL,
            headers={"X-API-Key": ""}
        )

    def generate_agent_account(self, agent_name: str) -> tuple[str, str]:
        """
        Derives a deterministic Algorand account for a named agent.
        
        Algorithm:
        1. Read MASTER_AGENT_SECRET from settings (32-byte hex string)
        2. Compute HMAC-SHA256(key=MASTER_AGENT_SECRET, msg=agent_name)
        3. Use the resulting 32 bytes as the ed25519 private key seed
        4. Derive Algorand address from that key
        5. Return (private_key_b64, address)
        6. Never store either value — caller is responsible
        
        Returns:
            tuple[str, str]: (private_key_base64, algorand_address)
        """
        try:
            # Get master secret (should be 32-byte hex string)
            master_secret = bytes.fromhex(settings.MASTER_AGENT_SECRET)
        except ValueError:
            # Fallback for dev: use the string directly
            master_secret = settings.MASTER_AGENT_SECRET.encode()
            logger.warning("MASTER_AGENT_SECRET is not valid hex — using raw bytes (dev mode)")

        # Derive 32-byte seed from agent name
        seed = hmac.new(master_secret, agent_name.encode(), hashlib.sha256).digest()
        
        # Generate ed25519 keypair from seed
        # algosdk uses nacl under the hood — we need to construct the private key properly
        # The private key in Algorand is 64 bytes: 32-byte seed + 32-byte public key
        import nacl.signing
        signing_key = nacl.signing.SigningKey(seed)
        verify_key = signing_key.verify_key
        
        # Construct Algorand private key (seed + public key)
        private_key_bytes = seed + bytes(verify_key)
        private_key_b64 = base64.b64encode(private_key_bytes).decode()
        
        # Derive address from public key
        address = encoding.encode_address(bytes(verify_key))
        
        return private_key_b64, address

    async def get_address(self, agent_name: str) -> str:
        """Generate account and return only the address."""
        _, address = self.generate_agent_account(agent_name)
        return address

    async def get_agent_balance(self, agent_name: str) -> float:
        """
        Get ALGO balance for a named agent's wallet.
        
        Generates account fresh to get address, then queries Algod.
        Returns balance in ALGO (not microALGO).
        Returns 0.0 if account not found on chain (not funded yet).
        """
        _, address = self.generate_agent_account(agent_name)
        try:
            info = self.algod_client.account_info(address)
            return info.get("amount", 0) / 1_000_000
        except Exception as e:
            logger.warning(f"get_agent_balance({agent_name}): {e}")
            return 0.0

    async def fund_agent(self, agent_name: str, amount_algo: float) -> str:
        """
        Transfer ALGO from oracle wallet to agent wallet.
        
        Steps:
        1. Get oracle private key from settings.ORACLE_MNEMONIC
        2. Get agent address via get_address(agent_name)
        3. Build PaymentTxn: oracle → agent_address, amount in microALGO
        4. Note field: f"fund_agent:{agent_name}"
        5. Sign with oracle private key
        6. Send via algod_client.send_raw_transaction()
        7. Wait for confirmation (4 rounds)
        8. Return txID
        
        Do not fund if agent already has sufficient balance (check first).
        """
        # Check current balance
        current_balance = await self.get_agent_balance(agent_name)
        if current_balance >= amount_algo * 0.9:
            logger.info(f"fund_agent({agent_name}): already funded ({current_balance:.3f} ALGO)")
            return f"skip-already-funded-{agent_name}"

        agent_address = await self.get_address(agent_name)
        
        if not settings.ORACLE_MNEMONIC:
            logger.warning(f"fund_agent({agent_name}): ORACLE_MNEMONIC not set (dev mode)")
            return f"dev-fund-{agent_name}"

        try:
            # Get oracle account
            oracle_private_key = algo_mnemonic.to_private_key(settings.ORACLE_MNEMONIC)
            oracle_address = settings.ORACLE_ADDRESS
            
            # Build transaction
            sp = self.algod_client.suggested_params()
            amount_microalgo = int(amount_algo * 1_000_000)
            note = f"fund_agent:{agent_name}".encode()
            
            txn = PaymentTxn(
                sender=oracle_address,
                sp=sp,
                receiver=agent_address,
                amt=amount_microalgo,
                note=note,
            )
            
            # Sign and send
            signed_txn = txn.sign(oracle_private_key)
            tx_id = self.algod_client.send_transaction(signed_txn)
            
            # Wait for confirmation
            wait_for_confirmation(self.algod_client, tx_id, 4)
            
            logger.info(f"fund_agent({agent_name}): funded {amount_algo} ALGO, txID={tx_id}")
            
            # Zero out private key
            oracle_private_key = None
            del oracle_private_key
            
            return tx_id
            
        except Exception as e:
            logger.error(f"fund_agent({agent_name}) failed: {e}")
            raise

    async def send_agent_payment(
        self,
        from_agent: str,
        to_address: str,
        amount_algo: float,
        note: str,
    ) -> str:
        """
        Autonomously sign and send payment from one agent to another.
        No human confirmation. No popup.
        
        Steps:
        1. Generate from_agent account (private_key, address)
        2. Build PaymentTxn: address → to_address
        3. Note field: note param encoded as bytes
        4. Sign with generated private_key
        5. Send and wait for confirmation (4 rounds)
        6. Immediately zero out private_key variable
        7. Return txID
        
        Raises:
            ValueError: if amount_algo < 0.0001 (dust prevention)
            ValueError: if to_address == from_address
        """
        if amount_algo < 0.0001:
            raise ValueError("Amount too small (dust prevention): minimum 0.0001 ALGO")
        
        private_key_b64, from_address = self.generate_agent_account(from_agent)
        
        if to_address == from_address:
            raise ValueError("Cannot send payment to self")
        
        if not encoding.is_valid_address(to_address):
            raise ValueError(f"Invalid destination address: {to_address}")
        
        try:
            # Build transaction
            sp = self.algod_client.suggested_params()
            amount_microalgo = int(amount_algo * 1_000_000)
            note_bytes = note.encode()
            
            txn = PaymentTxn(
                sender=from_address,
                sp=sp,
                receiver=to_address,
                amt=amount_microalgo,
                note=note_bytes,
            )
            
            # Sign with agent's private key
            private_key_bytes = base64.b64decode(private_key_b64)
            signed_txn = txn.sign(private_key_bytes)
            
            # Send
            tx_id = self.algod_client.send_transaction(signed_txn)
            
            # Wait for confirmation
            wait_for_confirmation(self.algod_client, tx_id, 4)
            
            logger.info(f"send_agent_payment: {from_agent} → {to_address[:16]}... {amount_algo} ALGO, txID={tx_id}")
            
            # Zero out private key immediately
            private_key_b64 = None
            private_key_bytes = None
            del private_key_b64
            del private_key_bytes
            
            return tx_id
            
        except Exception as e:
            logger.error(f"send_agent_payment({from_agent}) failed: {e}")
            # Zero out on error too
            private_key_b64 = None
            del private_key_b64
            raise

    async def get_all_agent_addresses(self) -> dict[str, str]:
        """
        Return addresses for all known agents.
        
        Returns:
            dict: {"master": address, "buyer": address, ...}
        """
        agents = ["master", "buyer", "seller", "verifier", "reputation"]
        addresses = {}
        for agent_name in agents:
            addresses[agent_name] = await self.get_address(agent_name)
        return addresses
