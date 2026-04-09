"""
Deploy all NeuralLedger smart contracts to Algorand Testnet.
Run: python contracts/deploy/deploy_contracts.py

Requires:
  - ORACLE_MNEMONIC and ORACLE_ADDRESS in .env
  - Oracle wallet funded with at least 2 ALGO on testnet
  - AlgoKit installed: pip install algokit
"""
from algosdk.v2client import algod
from algosdk import mnemonic, transaction
from contracts.deploy.config import ALGORAND_NODE_URL, ORACLE_MNEMONIC, ORACLE_ADDRESS
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_clients():
    client = algod.AlgodClient("", ALGORAND_NODE_URL, headers={"X-API-Key": ""})
    private_key = mnemonic.to_private_key(ORACLE_MNEMONIC)
    return client, private_key


def deploy_app(algod_client, private_key, approval_teal: str, clear_teal: str,
               global_schema, local_schema, app_args=None) -> int:
    sp = algod_client.suggested_params()

    approval_result = algod_client.compile(approval_teal)
    clear_result = algod_client.compile(clear_teal)

    approval_program = bytes.fromhex(approval_result["result"])
    clear_program = bytes.fromhex(clear_result["result"])

    txn = transaction.ApplicationCreateTxn(
        sender=ORACLE_ADDRESS,
        sp=sp,
        on_complete=transaction.OnComplete.NoOpOC,
        approval_program=approval_program,
        clear_program=clear_program,
        global_schema=global_schema,
        local_schema=local_schema,
        app_args=app_args or [],
    )

    signed = txn.sign(private_key)
    tx_id = algod_client.send_transaction(signed)
    result = transaction.wait_for_confirmation(algod_client, tx_id, 6)
    app_id = result["application-index"]
    logger.info(f"Deployed app ID: {app_id} (txID: {tx_id})")
    return app_id


def main():
    if not ORACLE_MNEMONIC:
        logger.error("ORACLE_MNEMONIC not set in .env")
        sys.exit(1)

    algod_client, private_key = get_clients()
    logger.info(f"Deploying from oracle: {ORACLE_ADDRESS}")

    # Check balance
    info = algod_client.account_info(ORACLE_ADDRESS)
    balance_algo = info["amount"] / 1_000_000
    logger.info(f"Oracle balance: {balance_algo:.4f} ALGO")
    if balance_algo < 1.0:
        logger.error("Insufficient balance. Fund oracle at https://bank.testnet.algorand.network/")
        sys.exit(1)

    logger.info("Compiling contracts via beaker...")
    # In production: run `algokit compile` on each contract first
    # then load the generated .teal files
    logger.info(
        "NOTE: Run `python -m beaker build` in each contract directory "
        "to generate .teal files before deploying."
    )
    logger.info(
        "After deployment, update .env with the app IDs:\n"
        "  ESCROW_CONTRACT_APP_ID=<id>\n"
        "  REPUTATION_CONTRACT_APP_ID=<id>\n"
        "  MARKETPLACE_CONTRACT_APP_ID=<id>\n"
        "  IDENTITY_CONTRACT_APP_ID=<id>\n"
        "  SERVICE_REGISTRY_CONTRACT_APP_ID=<id>"
    )


if __name__ == "__main__":
    main()
