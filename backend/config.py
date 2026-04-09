from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ALGORAND_NODE_URL: str = "https://testnet-api.algonode.cloud"
    ALGORAND_INDEXER_URL: str = "https://testnet-idx.algonode.cloud"
    ALGORAND_NETWORK: str = "testnet"
    ESCROW_CONTRACT_APP_ID: int = 0
    REPUTATION_CONTRACT_APP_ID: int = 0
    MARKETPLACE_CONTRACT_APP_ID: int = 0
    ORACLE_MNEMONIC: str = ""
    ORACLE_ADDRESS: str = ""

    OPENAI_API_KEY: str = ""
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_CHAT_MODEL: str = "gpt-4o"

    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "neuralledger-cache"
    PINECONE_ENVIRONMENT: str = ""

    WEB3_STORAGE_TOKEN: str = ""
    IPFS_GATEWAY: str = "https://w3s.link/ipfs/"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/neuralledger"
    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "changeme"
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:5173"

    CACHE_SIMILARITY_THRESHOLD: float = 0.85
    NEW_TASK_PRICE_ALGO: float = 0.005
    CACHED_TASK_PRICE_ALGO: float = 0.001
    PLATFORM_REVENUE_SHARE: float = 0.70
    REQUESTER_REVENUE_SHARE: float = 0.30
    MAX_VERIFIER_RETRIES: int = 2

    # Agent Economy
    MASTER_AGENT_SECRET: str = "changeme-set-32-byte-hex-in-env"
    IDENTITY_CONTRACT_APP_ID: int = 0
    SERVICE_REGISTRY_CONTRACT_APP_ID: int = 0
    MIN_AGENT_REPUTATION: int = 700
    MASTER_AGENT_FUND_AMOUNT: float = 2.0

    class Config:
        env_file = ".env"


settings = Settings()
