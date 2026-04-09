import os
from dotenv import load_dotenv

load_dotenv()

ALGORAND_NODE_URL = os.getenv("ALGORAND_NODE_URL", "https://testnet-api.algonode.cloud")
ALGORAND_INDEXER_URL = os.getenv("ALGORAND_INDEXER_URL", "https://testnet-idx.algonode.cloud")
ORACLE_MNEMONIC = os.getenv("ORACLE_MNEMONIC", "")
ORACLE_ADDRESS = os.getenv("ORACLE_ADDRESS", "")
ESCROW_CONTRACT_APP_ID = int(os.getenv("ESCROW_CONTRACT_APP_ID", "0"))
REPUTATION_CONTRACT_APP_ID = int(os.getenv("REPUTATION_CONTRACT_APP_ID", "0"))
MARKETPLACE_CONTRACT_APP_ID = int(os.getenv("MARKETPLACE_CONTRACT_APP_ID", "0"))
IDENTITY_CONTRACT_APP_ID = int(os.getenv("IDENTITY_CONTRACT_APP_ID", "0"))
SERVICE_REGISTRY_CONTRACT_APP_ID = int(os.getenv("SERVICE_REGISTRY_CONTRACT_APP_ID", "0"))
PLATFORM_REVENUE_SHARE = float(os.getenv("PLATFORM_REVENUE_SHARE", "0.70"))
