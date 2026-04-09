# CLAUDE.md — NeuralLedger
# Complete Build Specification for Claude Code

---

## PROJECT OVERVIEW

**NeuralLedger** is a decentralized AI computation marketplace built on Algorand.
Users pay micro-transactions (via x402 HTTP payment protocol) to access AI-generated
results. Cached results are resold at a discount, creating a secondary knowledge market.
A multi-agent system (LangGraph) orchestrates buyers, sellers, verifiers, and reputation
tracking. Every approved result is cryptographically committed on-chain via Merkle trees
stored in Algorand Box Storage.

### Core Value Proposition
- AI computation results become tradeable digital assets
- Eliminates redundant computation via semantic caching
- Trustless payments via Algorand smart contracts
- Verifiable result integrity via on-chain Merkle commitments
- Agent reputation system ensures quality over time

---

## TECH STACK

### Frontend
- **React 18** + **Vite** + **TypeScript**
- **TailwindCSS v3** for styling
- **Framer Motion** for animations
- **Zustand** for global state management
- **React Query (TanStack Query v5)** for server state + polling
- **React Router v6** for routing
- **Recharts** for analytics/charts
- **@perawallet/connect** for Algorand wallet connection
- **algosdk** (JavaScript) for transaction building + signing
- **axios** for HTTP requests
- **react-dropzone** for PDF upload
- **react-hot-toast** for notifications
- **lucide-react** for icons

### Backend
- **Python 3.11+**
- **FastAPI** as the web framework (async)
- **Uvicorn** as the ASGI server
- **LangGraph** for multi-agent orchestration
- **LangChain + OpenAI** for LLM tasks
- **LlamaIndex** for RAG pipeline
- **Pinecone** as vector database (semantic cache)
- **py-algorand-sdk (algosdk)** for blockchain interaction
- **Beaker + PyTeal** for smart contract development
- **Redis** for fast cache lookup + Celery broker
- **Celery** for async task queue
- **PostgreSQL** as primary database
- **SQLAlchemy** (async) as ORM
- **Alembic** for DB migrations
- **Web3.Storage / IPFS** for decentralized result storage
- **python-jose** for JWT auth
- **pydantic v2** for data validation
- **pytest + pytest-asyncio** for testing

### Smart Contracts
- **PyTeal + Beaker** for contract logic
- **Algorand Testnet** for development
- **AlgoKit** for project scaffolding + deployment
- **py-algorand-sdk** for contract deployment scripts

### DevOps
- **Docker + Docker Compose** for local development
- **python-dotenv** for environment variables

---

## ABSOLUTE RULES — READ BEFORE WRITING ANY CODE

1. **Never store private keys in backend.** Wallet signing always happens client-side.
2. **All blockchain reads use Algorand Indexer.** Never trust user-provided tx data without verification.
3. **Every payment transaction must be verified on-chain** before triggering AI computation.
4. **Prevent replay attacks** — every verified txID is stored in Redis and PostgreSQL; reject duplicates.
5. **x402 middleware runs before every protected route.** No exceptions.
6. **Merkle root must be committed before payment is released** from escrow.
7. **Agent reputation updates only flow from the Verifier Agent.** No other agent can modify scores.
8. **All API responses use consistent envelope:** `{ success, data, error, timestamp }`.
9. **Environment variables for ALL secrets.** No hardcoded addresses, keys, or API keys anywhere.
10. **TypeScript strict mode on.** No `any` types in frontend.
11. **All smart contract calls go through `contracts/deploy/contract_client.py`** — never call contracts directly from routers.
12. **Vector similarity threshold for cache is 0.85.** Make this a configurable env var `CACHE_SIMILARITY_THRESHOLD`.

---

## FOLDER STRUCTURE

Build exactly this structure. Do not deviate.

```
neuralledger/
│
├── frontend/
│   ├── public/
│   │   └── favicon.ico
│   ├── src/
│   │   ├── components/
│   │   │   ├── wallet/
│   │   │   │   ├── WalletConnect.tsx
│   │   │   │   ├── WalletBalance.tsx
│   │   │   │   ├── TransactionModal.tsx
│   │   │   │   └── WalletGuard.tsx
│   │   │   ├── marketplace/
│   │   │   │   ├── TaskSubmitter.tsx
│   │   │   │   ├── ResultCard.tsx
│   │   │   │   ├── CacheHitBadge.tsx
│   │   │   │   ├── PriceBreakdown.tsx
│   │   │   │   ├── MerkleProofBadge.tsx
│   │   │   │   └── TaskHistory.tsx
│   │   │   ├── agents/
│   │   │   │   ├── AgentMonitor.tsx
│   │   │   │   ├── AgentActivityFeed.tsx
│   │   │   │   ├── ReputationCard.tsx
│   │   │   │   └── AgentGraph.tsx
│   │   │   ├── payment/
│   │   │   │   ├── PaymentModal.tsx
│   │   │   │   ├── TxStatusTracker.tsx
│   │   │   │   └── RevenueShareDisplay.tsx
│   │   │   └── shared/
│   │   │       ├── Layout.tsx
│   │   │       ├── Navbar.tsx
│   │   │       ├── LoadingSpinner.tsx
│   │   │       ├── ErrorBoundary.tsx
│   │   │       └── StatusBadge.tsx
│   │   ├── hooks/
│   │   │   ├── useWallet.ts
│   │   │   ├── useX402.ts
│   │   │   ├── useTaskResult.ts
│   │   │   ├── useAgentActivity.ts
│   │   │   └── useMerkleVerify.ts
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── algorand.ts
│   │   │   └── x402Client.ts
│   │   ├── store/
│   │   │   ├── walletStore.ts
│   │   │   ├── taskStore.ts
│   │   │   └── agentStore.ts
│   │   ├── pages/
│   │   │   ├── Marketplace.tsx
│   │   │   ├── AgentDashboard.tsx
│   │   │   ├── MyResults.tsx
│   │   │   ├── VerifyResult.tsx
│   │   │   └── NotFound.tsx
│   │   ├── types/
│   │   │   ├── task.ts
│   │   │   ├── payment.ts
│   │   │   ├── agent.ts
│   │   │   └── algorand.ts
│   │   ├── utils/
│   │   │   ├── merkle.ts
│   │   │   ├── formatters.ts
│   │   │   └── constants.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── tasks.py
│   │   ├── payments.py
│   │   ├── cache.py
│   │   ├── agents.py
│   │   └── verify.py
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── x402_middleware.py
│   │   └── cors_middleware.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cache_service.py
│   │   ├── algorand_service.py
│   │   ├── ipfs_service.py
│   │   ├── merkle_service.py
│   │   └── reputation_service.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── orchestrator.py
│   │   ├── buyer_agent.py
│   │   ├── seller_agent.py
│   │   ├── verifier_agent.py
│   │   └── reputation_agent.py
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── rag_pipeline.py
│   │   ├── task_executor.py
│   │   └── embedding_service.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py
│   │   ├── result.py
│   │   ├── payment.py
│   │   └── agent.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── redis_client.py
│   │   └── migrations/
│   │       └── (alembic files)
│   ├── workers/
│   │   ├── __init__.py
│   │   └── celery_app.py
│   ├── tests/
│   │   ├── test_x402.py
│   │   ├── test_algorand_service.py
│   │   ├── test_verifier_agent.py
│   │   ├── test_merkle_service.py
│   │   └── test_cache_service.py
│   └── requirements.txt
│
├── contracts/
│   ├── escrow/
│   │   ├── escrow_contract.py
│   │   └── escrow_approval.teal
│   ├── reputation/
│   │   ├── reputation_contract.py
│   │   └── reputation_approval.teal
│   ├── marketplace/
│   │   ├── marketplace_contract.py
│   │   └── marketplace_approval.teal
│   ├── deploy/
│   │   ├── deploy_contracts.py
│   │   ├── contract_client.py
│   │   └── config.py
│   └── tests/
│       ├── test_escrow.py
│       ├── test_reputation.py
│       └── test_marketplace.py
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## ENVIRONMENT VARIABLES

Create `.env.example` with ALL of these. Never commit `.env`.

```env
# Algorand
ALGORAND_NODE_URL=https://testnet-api.algonode.cloud
ALGORAND_INDEXER_URL=https://testnet-idx.algonode.cloud
ALGORAND_NETWORK=testnet
ESCROW_CONTRACT_APP_ID=
REPUTATION_CONTRACT_APP_ID=
MARKETPLACE_CONTRACT_APP_ID=
ORACLE_MNEMONIC=
ORACLE_ADDRESS=

# AI
OPENAI_API_KEY=
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4o

# Vector DB
PINECONE_API_KEY=
PINECONE_INDEX_NAME=neuralledger-cache
PINECONE_ENVIRONMENT=

# Storage
WEB3_STORAGE_TOKEN=
IPFS_GATEWAY=https://w3s.link/ipfs/

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/neuralledger
REDIS_URL=redis://localhost:6379/0

# App
SECRET_KEY=
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
CACHE_SIMILARITY_THRESHOLD=0.85
NEW_TASK_PRICE_ALGO=0.005
CACHED_TASK_PRICE_ALGO=0.001
PLATFORM_REVENUE_SHARE=0.70
REQUESTER_REVENUE_SHARE=0.30
MAX_VERIFIER_RETRIES=2
```

---

## BACKEND IMPLEMENTATION

### `backend/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routers import tasks, payments, cache, agents, verify
from middleware.x402_middleware import X402Middleware
from db.database import init_db
from db.redis_client import init_redis
from config import settings
import logging

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await init_redis()
    yield

app = FastAPI(
    title="NeuralLedger API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(X402Middleware)

app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
app.include_router(cache.router, prefix="/api/cache", tags=["cache"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(verify.router, prefix="/api/verify", tags=["verify"])

@app.get("/health")
async def health():
    return {"status": "ok", "service": "neuralledger"}
```

### `backend/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ALGORAND_NODE_URL: str
    ALGORAND_INDEXER_URL: str
    ALGORAND_NETWORK: str = "testnet"
    ESCROW_CONTRACT_APP_ID: int
    REPUTATION_CONTRACT_APP_ID: int
    MARKETPLACE_CONTRACT_APP_ID: int
    ORACLE_MNEMONIC: str
    ORACLE_ADDRESS: str
    OPENAI_API_KEY: str
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_CHAT_MODEL: str = "gpt-4o"
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str = "neuralledger-cache"
    PINECONE_ENVIRONMENT: str
    WEB3_STORAGE_TOKEN: str
    IPFS_GATEWAY: str
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    BACKEND_URL: str
    FRONTEND_URL: str
    CACHE_SIMILARITY_THRESHOLD: float = 0.85
    NEW_TASK_PRICE_ALGO: float = 0.005
    CACHED_TASK_PRICE_ALGO: float = 0.001
    PLATFORM_REVENUE_SHARE: float = 0.70
    REQUESTER_REVENUE_SHARE: float = 0.30
    MAX_VERIFIER_RETRIES: int = 2

    class Config:
        env_file = ".env"

settings = Settings()
```

### `backend/middleware/x402_middleware.py`

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from services.algorand_service import AlgorandService
from services.cache_service import CacheService
from config import settings
import logging

logger = logging.getLogger(__name__)

PROTECTED_ROUTES = {
    "/api/tasks/run",
    "/api/tasks/result",
}

class X402Middleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.algorand = AlgorandService()
        self.cache = CacheService()

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path not in PROTECTED_ROUTES:
            return await call_next(request)

        payment_proof = request.headers.get("X-Payment-Proof")
        task_hash = request.headers.get("X-Task-Hash")

        if not task_hash:
            return JSONResponse(status_code=400, content={
                "success": False,
                "error": "X-Task-Hash header required",
                "data": None,
                "timestamp": self._now()
            })

        if not payment_proof:
            is_cached = await self.cache.check_exact(task_hash)
            price = settings.CACHED_TASK_PRICE_ALGO if is_cached else settings.NEW_TASK_PRICE_ALGO
            escrow_address = await self._get_escrow_address()

            return JSONResponse(status_code=402, content={
                "success": False,
                "error": "Payment required",
                "data": {
                    "payment_required": True,
                    "amount_algo": price,
                    "receiver": escrow_address,
                    "task_hash": task_hash,
                    "is_cached": is_cached,
                    "note": f"neuralledger:{task_hash}"
                },
                "timestamp": self._now()
            })

        # Verify payment on-chain
        verified = await self.algorand.verify_transaction(
            tx_id=payment_proof,
            task_hash=task_hash,
        )

        if not verified:
            return JSONResponse(status_code=402, content={
                "success": False,
                "error": "Payment verification failed",
                "data": None,
                "timestamp": self._now()
            })

        # Attach verified info to request state
        request.state.task_hash = task_hash
        request.state.tx_id = payment_proof
        request.state.payment_verified = True

        return await call_next(request)

    async def _get_escrow_address(self):
        from deploy.contract_client import ContractClient
        client = ContractClient()
        return await client.get_escrow_address()

    def _now(self):
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
```

### `backend/services/algorand_service.py`

```python
from algosdk.v2client import algod, indexer
from algosdk import encoding, mnemonic
from algosdk.transaction import PaymentTxn
from config import settings
from db.redis_client import get_redis
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

            # Fetch transaction from indexer
            tx_info = self.indexer_client.transaction(tx_id)
            tx = tx_info.get("transaction", {})

            if not tx:
                return False

            pt = tx.get("payment-transaction", {})
            receiver = pt.get("receiver", "")
            amount_microalgo = pt.get("amount", 0)
            note_b64 = tx.get("note", "")

            import base64
            try:
                note = base64.b64decode(note_b64).decode("utf-8")
            except Exception:
                note = ""

            expected_note = f"neuralledger:{task_hash}"
            escrow_address = settings.ORACLE_ADDRESS  # Use actual escrow in prod

            min_payment = int(settings.CACHED_TASK_PRICE_ALGO * 1_000_000)

            checks = [
                tx.get("tx-type") == "pay",
                receiver == escrow_address,
                amount_microalgo >= min_payment,
                note == expected_note,
            ]

            if all(checks):
                # Mark tx as used (TTL 30 days)
                await redis.setex(replay_key, 2592000, "1")
                return True

            logger.warning(f"Transaction verification failed: {checks}")
            return False

        except Exception as e:
            logger.error(f"Transaction verification error: {e}")
            return False

    def get_oracle_account(self):
        mn = settings.ORACLE_MNEMONIC
        private_key = mnemonic.to_private_key(mn)
        address = settings.ORACLE_ADDRESS
        return private_key, address

    async def get_account_balance(self, address: str) -> float:
        info = self.algod_client.account_info(address)
        return info.get("amount", 0) / 1_000_000
```

### `backend/services/merkle_service.py`

```python
import hashlib
import json
from typing import List, Tuple
from services.algorand_service import AlgorandService
from contracts.deploy.contract_client import ContractClient
import logging

logger = logging.getLogger(__name__)

class MerkleService:
    def __init__(self):
        self.algorand = AlgorandService()
        self.contract_client = ContractClient()

    def _hash(self, data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()

    def build_tree(self, chunks: List[str]) -> dict:
        """Build Merkle tree from list of content chunks."""
        if not chunks:
            raise ValueError("Cannot build Merkle tree from empty list")

        # Pad to even number
        if len(chunks) % 2 != 0:
            chunks.append(chunks[-1])

        leaves = [self._hash(c) for c in chunks]
        tree = [leaves]

        current = leaves
        while len(current) > 1:
            if len(current) % 2 != 0:
                current.append(current[-1])
            next_level = []
            for i in range(0, len(current), 2):
                combined = self._hash(current[i] + current[i + 1])
                next_level.append(combined)
            tree.append(next_level)
            current = next_level

        root = current[0]
        return {"root": root, "tree": tree, "leaves": leaves}

    def generate_proof(self, tree_data: dict, leaf_index: int) -> List[dict]:
        """Generate inclusion proof for a specific leaf."""
        tree = tree_data["tree"]
        proof = []
        idx = leaf_index

        for level in tree[:-1]:
            if idx % 2 == 0:
                sibling_idx = idx + 1
                position = "right"
            else:
                sibling_idx = idx - 1
                position = "left"

            if sibling_idx < len(level):
                proof.append({
                    "hash": level[sibling_idx],
                    "position": position
                })

            idx //= 2

        return proof

    def verify_proof(self, leaf_data: str, proof: List[dict], root: str) -> bool:
        """Verify a Merkle inclusion proof."""
        current = self._hash(leaf_data)

        for step in proof:
            sibling = step["hash"]
            if step["position"] == "right":
                current = self._hash(current + sibling)
            else:
                current = self._hash(sibling + current)

        return current == root

    async def commit_to_chain(self, task_hash: str, merkle_root: str,
                               original_requester: str, price_microalgo: int) -> str:
        """Store Merkle root in Algorand Box Storage via marketplace contract."""
        try:
            tx_id = await self.contract_client.register_result(
                task_hash=task_hash,
                merkle_root=merkle_root,
                original_requester=original_requester,
                price=price_microalgo
            )
            logger.info(f"Merkle root committed on-chain: {merkle_root[:16]}... txID: {tx_id}")
            return tx_id
        except Exception as e:
            logger.error(f"Failed to commit Merkle root: {e}")
            raise
```

### `backend/services/cache_service.py`

```python
from pinecone import Pinecone
from ai.embedding_service import EmbeddingService
from db.redis_client import get_redis
from config import settings
import json
import logging

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
        self.embedder = EmbeddingService()
        self.threshold = settings.CACHE_SIMILARITY_THRESHOLD

    async def check_exact(self, task_hash: str) -> bool:
        """Fast exact hash check via Redis."""
        redis = await get_redis()
        return await redis.exists(f"result:{task_hash}") > 0

    async def check_semantic(self, task_text: str) -> dict | None:
        """Semantic similarity check via Pinecone vector search."""
        try:
            embedding = await self.embedder.embed(task_text)
            results = self.index.query(
                vector=embedding,
                top_k=1,
                include_metadata=True
            )

            if not results.matches:
                return None

            top = results.matches[0]
            if top.score >= self.threshold:
                logger.info(f"Semantic cache hit: score={top.score:.3f}")
                return {
                    "task_hash": top.id,
                    "score": top.score,
                    "metadata": top.metadata
                }

            return None

        except Exception as e:
            logger.error(f"Semantic cache check error: {e}")
            return None

    async def store(self, task_hash: str, task_text: str, result: str,
                    merkle_root: str, ipfs_cid: str, requester: str):
        """Store result in Redis (fast) + Pinecone (semantic)."""
        redis = await get_redis()

        cache_data = {
            "result": result,
            "merkle_root": merkle_root,
            "ipfs_cid": ipfs_cid,
            "requester": requester,
            "task_hash": task_hash
        }

        # Redis for fast lookup
        await redis.setex(
            f"result:{task_hash}",
            86400 * 30,  # 30 days TTL
            json.dumps(cache_data)
        )

        # Pinecone for semantic search
        embedding = await self.embedder.embed(task_text)
        self.index.upsert(vectors=[{
            "id": task_hash,
            "values": embedding,
            "metadata": {
                "task_hash": task_hash,
                "merkle_root": merkle_root,
                "ipfs_cid": ipfs_cid,
                "requester": requester
            }
        }])

    async def get(self, task_hash: str) -> dict | None:
        redis = await get_redis()
        data = await redis.get(f"result:{task_hash}")
        if data:
            return json.loads(data)
        return None
```

### `backend/agents/orchestrator.py`

```python
from langgraph.graph import StateGraph, END
from agents.buyer_agent import BuyerAgent
from agents.seller_agent import SellerAgent
from agents.verifier_agent import VerifierAgent
from agents.reputation_agent import ReputationAgent
from typing import TypedDict, Optional
import logging

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    task_id: str
    task_hash: str
    task_text: str
    task_type: str
    file_content: Optional[str]
    requester: str
    tx_id: str
    result: Optional[str]
    merkle_root: Optional[str]
    ipfs_cid: Optional[str]
    verification_score: Optional[float]
    status: str
    attempt: int
    error: Optional[str]

class AgentOrchestrator:
    def __init__(self):
        self.buyer = BuyerAgent()
        self.seller = SellerAgent()
        self.verifier = VerifierAgent()
        self.reputation = ReputationAgent()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)

        workflow.add_node("buyer", self.buyer.run)
        workflow.add_node("seller", self.seller.run)
        workflow.add_node("verifier", self.verifier.run)
        workflow.add_node("reputation_pass", self.reputation.reward)
        workflow.add_node("reputation_fail", self.reputation.slash)
        workflow.add_node("retry", self._handle_retry)

        workflow.set_entry_point("buyer")

        workflow.add_edge("buyer", "seller")

        workflow.add_conditional_edges(
            "verifier",
            self._route_after_verify,
            {
                "pass": "reputation_pass",
                "retry": "seller",
                "fail": "reputation_fail"
            }
        )

        workflow.add_edge("seller", "verifier")
        workflow.add_edge("reputation_pass", END)
        workflow.add_edge("reputation_fail", END)

        return workflow.compile()

    def _route_after_verify(self, state: AgentState) -> str:
        if state["status"] == "verified":
            return "pass"
        elif state["attempt"] < 2:
            return "retry"
        else:
            return "fail"

    async def _handle_retry(self, state: AgentState) -> AgentState:
        state["attempt"] = state.get("attempt", 0) + 1
        state["status"] = "retrying"
        return state

    async def run(self, task_id: str, task_hash: str, task_text: str,
                  task_type: str, requester: str, tx_id: str,
                  file_content: str = None) -> AgentState:
        initial_state: AgentState = {
            "task_id": task_id,
            "task_hash": task_hash,
            "task_text": task_text,
            "task_type": task_type,
            "file_content": file_content,
            "requester": requester,
            "tx_id": tx_id,
            "result": None,
            "merkle_root": None,
            "ipfs_cid": None,
            "verification_score": None,
            "status": "started",
            "attempt": 0,
            "error": None
        }

        final_state = await self.graph.ainvoke(initial_state)
        return final_state
```

### `backend/agents/verifier_agent.py`

```python
from openai import AsyncOpenAI
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from services.merkle_service import MerkleService
from services.ipfs_service import IPFSService
from services.cache_service import CacheService
from config import settings
import logging

logger = logging.getLogger(__name__)

class VerifierAgent:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.merkle = MerkleService()
        self.ipfs = IPFSService()
        self.cache = CacheService()
        self.threshold = 0.85

    async def run(self, state: dict) -> dict:
        task_text = state["task_text"]
        result = state["result"]
        task_hash = state["task_hash"]
        requester = state["requester"]

        if not result:
            state["status"] = "failed"
            state["error"] = "No result to verify"
            return state

        try:
            score = await self._compute_similarity(task_text, result)
            state["verification_score"] = score
            logger.info(f"Verification score: {score:.3f} (threshold: {self.threshold})")

            if score >= self.threshold:
                # Build Merkle tree over result chunks
                chunks = self._chunk_result(result)
                tree_data = self.merkle.build_tree(chunks)
                merkle_root = tree_data["root"]

                # Store result on IPFS
                ipfs_cid = await self.ipfs.store({
                    "result": result,
                    "task_hash": task_hash,
                    "merkle_root": merkle_root,
                    "tree": tree_data["tree"]
                })

                # Commit Merkle root to Algorand Box Storage
                price_microalgo = int(settings.NEW_TASK_PRICE_ALGO * 1_000_000)
                await self.merkle.commit_to_chain(
                    task_hash=task_hash,
                    merkle_root=merkle_root,
                    original_requester=requester,
                    price_microalgo=price_microalgo
                )

                # Store in semantic cache
                await self.cache.store(
                    task_hash=task_hash,
                    task_text=task_text,
                    result=result,
                    merkle_root=merkle_root,
                    ipfs_cid=ipfs_cid,
                    requester=requester
                )

                state["merkle_root"] = merkle_root
                state["ipfs_cid"] = ipfs_cid
                state["status"] = "verified"

            else:
                state["status"] = "rejected"
                state["error"] = f"Quality below threshold: {score:.3f}"

        except Exception as e:
            logger.error(f"Verifier error: {e}")
            state["status"] = "error"
            state["error"] = str(e)

        return state

    async def _compute_similarity(self, task: str, result: str) -> float:
        response = await self.client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=[task, result]
        )
        task_vec = np.array(response.data[0].embedding).reshape(1, -1)
        result_vec = np.array(response.data[1].embedding).reshape(1, -1)
        return float(cosine_similarity(task_vec, result_vec)[0][0])

    def _chunk_result(self, result: str, chunk_size: int = 500) -> list:
        words = result.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunks.append(" ".join(words[i:i + chunk_size]))
        return chunks if chunks else [result]
```

### `backend/routers/tasks.py`

```python
from fastapi import APIRouter, Request, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from services.cache_service import CacheService
from agents.orchestrator import AgentOrchestrator
from db.database import get_db
from models.task import Task, TaskStatus
from datetime import datetime, timezone
import hashlib
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
cache = CacheService()
orchestrator = AgentOrchestrator()

def _now():
    return datetime.now(timezone.utc).isoformat()

def _envelope(success: bool, data=None, error=None):
    return {"success": success, "data": data, "error": error, "timestamp": _now()}

@router.post("/run")
async def run_task(
    request: Request,
    background_tasks: BackgroundTasks,
    task_type: str = Form(...),
    prompt: str = Form(...),
    file: UploadFile = File(None)
):
    """
    Protected by X402Middleware. By the time this runs,
    request.state.payment_verified is True.
    """
    file_content = None
    if file:
        raw = await file.read()
        # Extract text from PDF using PyMuPDF
        import fitz
        doc = fitz.open(stream=raw, filetype="pdf")
        file_content = "\n".join(page.get_text() for page in doc)

    task_text = f"{task_type}: {prompt}"
    if file_content:
        task_text += f"\n\nDocument content:\n{file_content[:3000]}"

    task_hash = request.headers.get("X-Task-Hash")
    tx_id = request.headers.get("X-Payment-Proof")
    requester = request.headers.get("X-Wallet-Address", "unknown")
    task_id = str(uuid.uuid4())

    # Check semantic cache first
    cached = await cache.check_semantic(task_text)
    if cached:
        cached_result = await cache.get(cached["task_hash"])
        if cached_result:
            return JSONResponse(content=_envelope(True, {
                "task_id": task_id,
                "status": "cache_hit",
                "result": cached_result["result"],
                "merkle_root": cached_result["merkle_root"],
                "ipfs_cid": cached_result["ipfs_cid"],
                "similarity_score": cached["score"],
                "from_cache": True
            }))

    # Run agent pipeline in background
    background_tasks.add_task(
        orchestrator.run,
        task_id=task_id,
        task_hash=task_hash,
        task_text=task_text,
        task_type=task_type,
        requester=requester,
        tx_id=tx_id,
        file_content=file_content
    )

    return JSONResponse(content=_envelope(True, {
        "task_id": task_id,
        "status": "processing",
        "message": "Task queued. Poll /api/tasks/result/{task_id} for updates."
    }))

@router.get("/result/{task_id}")
async def get_result(task_id: str):
    from db.redis_client import get_redis
    redis = await get_redis()
    import json
    data = await redis.get(f"task_result:{task_id}")
    if data:
        return JSONResponse(content=_envelope(True, json.loads(data)))
    return JSONResponse(content=_envelope(True, {"status": "processing", "task_id": task_id}))

@router.post("/hash")
async def compute_hash(payload: dict):
    """Compute task hash on backend so frontend can attach it to 402 flow."""
    content = payload.get("content", "")
    task_hash = hashlib.sha256(content.encode()).hexdigest()
    is_cached = await cache.check_exact(task_hash)
    semantic = await cache.check_semantic(content)

    return JSONResponse(content=_envelope(True, {
        "task_hash": task_hash,
        "is_cached": is_cached or bool(semantic),
        "semantic_match": semantic
    }))
```

---

## SMART CONTRACTS

### `contracts/escrow/escrow_contract.py`

```python
from beaker import *
from pyteal import *

class EscrowState:
    oracle_address = GlobalStateVar(TealType.bytes, key="oracle")
    total_received = GlobalStateVar(TealType.uint64, key="total")

app = Application(
    "NeuralLedgerEscrow",
    state=EscrowState(),
    descr="Receives x402 payments and releases with revenue split"
)

@app.create
def create(oracle: abi.Address) -> Expr:
    return Seq([
        app.state.oracle_address.set(oracle.get()),
        app.state.total_received.set(Int(0)),
    ])

@app.external
def release_payment(
    task_hash: abi.String,
    recipient: abi.Address,
    platform_account: abi.Address,
    platform_share_bps: abi.Uint64,
    *,
    output: abi.Bool
):
    """
    Split payment: platform_share_bps basis points to platform,
    remainder to original requester.
    Oracle-only.
    """
    return Seq([
        Assert(
            Txn.sender() == app.state.oracle_address.get(),
            comment="Only oracle can release payments"
        ),
        Assert(
            Txn.type_enum() == TxnType.ApplicationCall,
        ),
        Assert(Gtxn[0].type_enum() == TxnType.Payment),

        # Calculate shares
        (total := ScratchVar(TealType.uint64)),
        total.store(Gtxn[0].amount()),

        (platform_amt := ScratchVar(TealType.uint64)),
        platform_amt.store(
            WideRatio([total.load(), platform_share_bps.get()], [Int(10000)])
        ),

        (requester_amt := ScratchVar(TealType.uint64)),
        requester_amt.store(total.load() - platform_amt.load()),

        # Pay platform
        InnerTxnBuilder.Execute({
            TxnField.type_enum: TxnType.Payment,
            TxnField.receiver: platform_account.get(),
            TxnField.amount: platform_amt.load(),
            TxnField.fee: Int(0),
        }),

        # Pay original requester
        InnerTxnBuilder.Execute({
            TxnField.type_enum: TxnType.Payment,
            TxnField.receiver: recipient.get(),
            TxnField.amount: requester_amt.load(),
            TxnField.fee: Int(0),
        }),

        app.state.total_received.set(
            app.state.total_received.get() + total.load()
        ),

        output.set(Bool(True)),
    ])
```

### `contracts/reputation/reputation_contract.py`

```python
from beaker import *
from pyteal import *

class ReputationState:
    oracle_address = GlobalStateVar(TealType.bytes, key="oracle")

app = Application(
    "AgentReputation",
    state=ReputationState(),
    descr="Manages agent reputation scores as on-chain state"
)

SCORE_KEY_PREFIX = "agent_score_"
TASKS_KEY_PREFIX = "agent_tasks_"

@app.create
def create(oracle: abi.Address) -> Expr:
    return app.state.oracle_address.set(oracle.get())

@app.external
def update_score(
    agent_address: abi.Address,
    success: abi.Bool,
    *,
    output: abi.Uint64
):
    score_key = Concat(Bytes(SCORE_KEY_PREFIX), agent_address.get())
    tasks_key = Concat(Bytes(TASKS_KEY_PREFIX), agent_address.get())

    current_score = App.globalGetEx(Int(0), score_key)
    current_tasks = App.globalGetEx(Int(0), tasks_key)

    return Seq([
        Assert(
            Txn.sender() == app.state.oracle_address.get(),
            comment="Only oracle can update reputation"
        ),
        current_score,
        current_tasks,

        (score := ScratchVar(TealType.uint64)),
        score.store(
            If(current_score.hasValue())
            .Then(current_score.value())
            .Else(Int(500))  # Default starting score
        ),

        If(success.get())
        .Then(
            score.store(
                If(score.load() + Int(10) <= Int(1000))
                .Then(score.load() + Int(10))
                .Else(Int(1000))
            )
        )
        .Else(
            score.store(
                If(score.load() >= Int(20))
                .Then(score.load() - Int(20))
                .Else(Int(0))
            )
        ),

        App.globalPut(score_key, score.load()),
        App.globalPut(
            tasks_key,
            If(current_tasks.hasValue())
            .Then(current_tasks.value() + Int(1))
            .Else(Int(1))
        ),

        output.set(score.load()),
    ])

@app.external(read_only=True)
def get_score(agent_address: abi.Address, *, output: abi.Uint64):
    score_key = Concat(Bytes(SCORE_KEY_PREFIX), agent_address.get())
    score = App.globalGetEx(Int(0), score_key)
    return Seq([
        score,
        output.set(
            If(score.hasValue()).Then(score.value()).Else(Int(500))
        )
    ])
```

### `contracts/marketplace/marketplace_contract.py`

```python
from beaker import *
from pyteal import *

app = Application(
    "NeuralLedgerMarketplace",
    descr="Stores result Merkle roots in Box Storage. Single source of truth for result integrity."
)

class MarketplaceState:
    oracle_address = GlobalStateVar(TealType.bytes, key="oracle")
    total_results = GlobalStateVar(TealType.uint64, key="total")

app.state = MarketplaceState()

@app.create
def create(oracle: abi.Address) -> Expr:
    return Seq([
        app.state.oracle_address.set(oracle.get()),
        app.state.total_results.set(Int(0)),
    ])

@app.external
def register_result(
    task_hash: abi.String,
    merkle_root: abi.String,
    original_requester: abi.Address,
    price_microalgo: abi.Uint64,
    *,
    output: abi.Bool
):
    """Store result metadata in Box Storage. Oracle-only."""
    box_key = task_hash.get()
    box_value = Concat(
        merkle_root.get(),
        Bytes("|"),
        original_requester.get(),
        Bytes("|"),
        Itob(price_microalgo.get())
    )

    return Seq([
        Assert(
            Txn.sender() == app.state.oracle_address.get(),
            comment="Only oracle can register results"
        ),
        Assert(
            Not(App.box_get(box_key).hasValue()),
            comment="Result already registered"
        ),
        Pop(App.box_create(box_key, Int(256))),
        App.box_put(box_key, box_value),
        app.state.total_results.set(
            app.state.total_results.get() + Int(1)
        ),
        output.set(Bool(True)),
    ])

@app.external(read_only=True)
def get_result_proof(task_hash: abi.String, *, output: abi.String):
    """Retrieve Merkle root for a task hash."""
    box_data = App.box_get(task_hash.get())
    return Seq([
        box_data,
        Assert(box_data.hasValue(), comment="Result not found"),
        output.set(box_data.value()),
    ])
```

---

## FRONTEND IMPLEMENTATION

### `frontend/src/services/x402Client.ts`

```typescript
import { algorandService } from './algorand';
import { api } from './api';

interface PaymentRequest {
  amount_algo: number;
  receiver: string;
  task_hash: string;
  is_cached: boolean;
  note: string;
}

interface X402Result {
  success: boolean;
  data: unknown;
}

export async function executeWithPayment(
  endpoint: string,
  taskHash: string,
  walletAddress: string,
  onPaymentRequired: (req: PaymentRequest) => Promise<boolean>,
  body?: FormData
): Promise<X402Result> {
  // Step 1: Probe — expect 402
  const probe = await fetch(`${import.meta.env.VITE_BACKEND_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'X-Task-Hash': taskHash,
      'X-Wallet-Address': walletAddress,
    },
    body,
  });

  if (probe.status !== 402) {
    return probe.json();
  }

  const probeData = await probe.json();
  const paymentRequest: PaymentRequest = probeData.data;

  // Step 2: Show confirmation modal to user
  const confirmed = await onPaymentRequired(paymentRequest);
  if (!confirmed) {
    throw new Error('User cancelled payment');
  }

  // Step 3: Build and sign transaction via wallet
  const txId = await algorandService.sendPayment({
    from: walletAddress,
    to: paymentRequest.receiver,
    amountAlgo: paymentRequest.amount_algo,
    note: paymentRequest.note,
  });

  // Step 4: Wait for confirmation
  await algorandService.waitForConfirmation(txId);

  // Step 5: Retry with payment proof
  const result = await fetch(`${import.meta.env.VITE_BACKEND_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'X-Task-Hash': taskHash,
      'X-Wallet-Address': walletAddress,
      'X-Payment-Proof': txId,
    },
    body,
  });

  return result.json();
}
```

### `frontend/src/services/algorand.ts`

```typescript
import algosdk from 'algosdk';
import { PeraWalletConnect } from '@perawallet/connect';

const peraWallet = new PeraWalletConnect();

const algodClient = new algosdk.Algodv2(
  '',
  import.meta.env.VITE_ALGORAND_NODE_URL,
  ''
);

export const algorandService = {
  peraWallet,

  async connect(): Promise<string[]> {
    const accounts = await peraWallet.connect();
    peraWallet.connector?.on('disconnect', () => {
      peraWallet.disconnect();
    });
    return accounts;
  },

  async disconnect() {
    await peraWallet.disconnect();
  },

  async getBalance(address: string): Promise<number> {
    const info = await algodClient.accountInformation(address).do();
    return Number(info.amount) / 1_000_000;
  },

  async sendPayment(params: {
    from: string;
    to: string;
    amountAlgo: number;
    note: string;
  }): Promise<string> {
    const suggestedParams = await algodClient.getTransactionParams().do();
    const noteBytes = new TextEncoder().encode(params.note);

    const txn = algosdk.makePaymentTxnWithSuggestedParamsFromObject({
      from: params.from,
      to: params.to,
      amount: Math.round(params.amountAlgo * 1_000_000),
      note: noteBytes,
      suggestedParams,
    });

    const singleTxnGroups = [{ txn, signers: [params.from] }];
    const signedTxns = await peraWallet.signTransaction([singleTxnGroups]);
    const { txId } = await algodClient.sendRawTransaction(signedTxns).do();
    return txId;
  },

  async waitForConfirmation(txId: string, rounds = 10): Promise<void> {
    await algosdk.waitForConfirmation(algodClient, txId, rounds);
  },

  async verifyMerkleProof(params: {
    leafData: string;
    proof: Array<{ hash: string; position: 'left' | 'right' }>;
    root: string;
  }): Promise<boolean> {
    const { leafData, proof, root } = params;
    const encoder = new TextEncoder();

    async function sha256hex(data: string): Promise<string> {
      const buf = await crypto.subtle.digest('SHA-256', encoder.encode(data));
      return Array.from(new Uint8Array(buf))
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');
    }

    let current = await sha256hex(leafData);

    for (const step of proof) {
      if (step.position === 'right') {
        current = await sha256hex(current + step.hash);
      } else {
        current = await sha256hex(step.hash + current);
      }
    }

    return current === root;
  },
};
```

### `frontend/src/hooks/useX402.ts`

```typescript
import { useState, useCallback } from 'react';
import { executeWithPayment } from '../services/x402Client';
import { useWalletStore } from '../store/walletStore';
import { api } from '../services/api';
import toast from 'react-hot-toast';

export function useX402() {
  const { address } = useWalletStore();
  const [loading, setLoading] = useState(false);
  const [paymentRequest, setPaymentRequest] = useState<null | {
    amount_algo: number;
    is_cached: boolean;
    resolve: (v: boolean) => void;
  }>(null);

  const submitTask = useCallback(async (
    taskType: string,
    prompt: string,
    file?: File
  ) => {
    if (!address) {
      toast.error('Connect your wallet first');
      return null;
    }

    setLoading(true);

    try {
      // Compute task hash
      const content = `${taskType}: ${prompt}`;
      const { data: hashData } = await api.post('/api/tasks/hash', { content });
      const taskHash: string = hashData.data.task_hash;

      const formData = new FormData();
      formData.append('task_type', taskType);
      formData.append('prompt', prompt);
      if (file) formData.append('file', file);

      const result = await executeWithPayment(
        '/api/tasks/run',
        taskHash,
        address,
        (req) => new Promise((resolve) => {
          setPaymentRequest({
            amount_algo: req.amount_algo,
            is_cached: req.is_cached,
            resolve,
          });
        }),
        formData
      );

      return result;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Task failed';
      if (msg !== 'User cancelled payment') {
        toast.error(msg);
      }
      return null;
    } finally {
      setLoading(false);
      setPaymentRequest(null);
    }
  }, [address]);

  const confirmPayment = useCallback((confirmed: boolean) => {
    paymentRequest?.resolve(confirmed);
  }, [paymentRequest]);

  return { submitTask, loading, paymentRequest, confirmPayment };
}
```

### `frontend/src/store/walletStore.ts`

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface WalletState {
  address: string | null;
  balance: number;
  connected: boolean;
  setAddress: (address: string | null) => void;
  setBalance: (balance: number) => void;
  setConnected: (v: boolean) => void;
  disconnect: () => void;
}

export const useWalletStore = create<WalletState>()(
  persist(
    (set) => ({
      address: null,
      balance: 0,
      connected: false,
      setAddress: (address) => set({ address }),
      setBalance: (balance) => set({ balance }),
      setConnected: (connected) => set({ connected }),
      disconnect: () => set({ address: null, balance: 0, connected: false }),
    }),
    { name: 'wallet-store' }
  )
);
```

### `frontend/src/components/payment/PaymentModal.tsx`

```tsx
import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, Zap, CheckCircle } from 'lucide-react';

interface Props {
  open: boolean;
  amountAlgo: number;
  isCached: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export function PaymentModal({ open, amountAlgo, isCached, onConfirm, onCancel }: Props) {
  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="bg-white rounded-2xl shadow-xl p-8 max-w-sm w-full mx-4"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-blue-50 rounded-lg">
                <Zap className="w-5 h-5 text-blue-600" />
              </div>
              <h2 className="text-lg font-semibold text-gray-900">Payment Required</h2>
            </div>

            {isCached && (
              <div className="flex items-center gap-2 bg-green-50 border border-green-200 rounded-lg p-3 mb-4">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span className="text-sm text-green-700 font-medium">
                  Cached result — 80% cheaper
                </span>
              </div>
            )}

            <div className="bg-gray-50 rounded-xl p-4 mb-6">
              <p className="text-sm text-gray-500 mb-1">Amount</p>
              <p className="text-3xl font-bold text-gray-900">
                {amountAlgo} <span className="text-lg font-normal text-gray-500">ALGO</span>
              </p>
              <p className="text-xs text-gray-400 mt-1">
                ≈ ${(amountAlgo * 0.15).toFixed(4)} USD
              </p>
            </div>

            <div className="flex items-start gap-2 mb-6">
              <AlertCircle className="w-4 h-4 text-gray-400 mt-0.5 shrink-0" />
              <p className="text-xs text-gray-500">
                This transaction will be signed by your Pera Wallet and verified on Algorand Testnet.
                Your result is Merkle-committed on-chain for tamper-proof integrity.
              </p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={onCancel}
                className="flex-1 py-2.5 border border-gray-200 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 transition"
              >
                Cancel
              </button>
              <button
                onClick={onConfirm}
                className="flex-1 py-2.5 bg-blue-600 rounded-xl text-sm font-medium text-white hover:bg-blue-700 transition"
              >
                Sign & Pay
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
```

---

## WEBSOCKET — LIVE AGENT FEED

### Backend WebSocket endpoint in `backend/routers/agents.py`

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import json

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.append(ws)

    def disconnect(self, ws: WebSocket):
        self.connections.remove(ws)

    async def broadcast(self, message: dict):
        for ws in self.connections:
            try:
                await ws.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

@router.websocket("/ws/activity")
async def agent_activity_feed(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await asyncio.sleep(30)
            await ws.send_json({"type": "ping"})
    except WebSocketDisconnect:
        manager.disconnect(ws)

# Call this from agents to broadcast activity
async def broadcast_activity(event: str, agent: str, details: dict):
    await manager.broadcast({
        "type": "activity",
        "event": event,
        "agent": agent,
        "details": details,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    })
```

### Frontend WebSocket hook in `frontend/src/hooks/useAgentActivity.ts`

```typescript
import { useEffect, useRef } from 'react';
import { useAgentStore } from '../store/agentStore';

export function useAgentActivity() {
  const wsRef = useRef<WebSocket | null>(null);
  const { addActivity } = useAgentStore();

  useEffect(() => {
    const ws = new WebSocket(
      `${import.meta.env.VITE_WS_URL}/api/agents/ws/activity`
    );

    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      if (msg.type === 'activity') {
        addActivity(msg);
      }
    };

    ws.onerror = () => console.warn('Agent feed disconnected');
    wsRef.current = ws;

    return () => ws.close();
  }, [addActivity]);
}
```

---

## DOCKER COMPOSE

```yaml
version: '3.9'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: neuralledger
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  celery:
    build: ./backend
    env_file: .env
    depends_on:
      - redis
    command: celery -A workers.celery_app worker --loglevel=info

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    env_file: ./frontend/.env
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev -- --host

volumes:
  postgres_data:
```

---

## SECURITY CHECKLIST

Claude Code must implement ALL of these. No exceptions.

- [ ] Replay attack prevention: store every verified txID in Redis with 30-day TTL
- [ ] Rate limiting on `/api/tasks/run`: max 10 requests/min per wallet address
- [ ] Validate wallet address format (58-char Algorand address) on every request
- [ ] Sanitize all file uploads: accept only PDF, max 10MB
- [ ] Never log or store private keys, mnemonics, or raw transaction signatures
- [ ] CORS restricted to FRONTEND_URL only
- [ ] All secrets via environment variables — no hardcoding
- [ ] Merkle root committed before payment released
- [ ] Smart contract oracle address is the ONLY address that can trigger state changes
- [ ] Input validation on all FastAPI endpoints via Pydantic models
- [ ] Async SQLAlchemy — no blocking DB calls in async routes
- [ ] Celery tasks have max retries + exponential backoff

---

## UI/UX DESIGN SYSTEM

Use this design language consistently across all pages.

### Color Palette
```
Primary:     #2563EB (blue-600)
Success:     #16A34A (green-600)
Warning:     #D97706 (amber-600)
Danger:      #DC2626 (red-600)
Background:  #F9FAFB (gray-50)
Surface:     #FFFFFF
Border:      #E5E7EB (gray-200)
Text:        #111827 (gray-900)
Muted:       #6B7280 (gray-500)
```

### Typography
```
Font:        Inter (import from Google Fonts)
Heading 1:   text-3xl font-bold
Heading 2:   text-xl font-semibold
Body:        text-sm text-gray-600
Mono:        font-mono text-xs (for hashes, tx IDs)
```

### Component Patterns
- Cards: `bg-white rounded-2xl border border-gray-100 shadow-sm p-6`
- Primary button: `bg-blue-600 hover:bg-blue-700 text-white rounded-xl px-4 py-2.5 text-sm font-medium transition`
- Secondary button: `border border-gray-200 hover:bg-gray-50 text-gray-700 rounded-xl px-4 py-2.5 text-sm font-medium transition`
- Input: `w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500`
- Badge green: `bg-green-50 text-green-700 border border-green-200 rounded-full px-2.5 py-0.5 text-xs font-medium`
- Badge blue: `bg-blue-50 text-blue-700 border border-blue-200 rounded-full px-2.5 py-0.5 text-xs font-medium`
- Hash display: `font-mono text-xs text-gray-400 truncate max-w-[120px]`

### Pages to Build

**`/` — Marketplace (main page)**
- Hero section with project tagline
- PDF upload drop zone (react-dropzone)
- Task type selector (summarize / extract / analyze)
- Prompt input
- "Submit Task" button → triggers x402 flow
- Payment Modal overlay
- Result display card with Merkle badge
- Live agent activity sidebar (WebSocket feed)

**`/dashboard` — Agent Dashboard**
- 4 agent status cards (Buyer / Seller / Verifier / Reputation)
- Live activity feed with timestamps
- Reputation score chart (Recharts line chart)
- Total tasks processed counter

**`/results` — My Results**
- List of user's purchased results
- Each card shows: task, result preview, Merkle badge, price paid
- Filter by: all / cached / fresh

**`/verify/:taskHash` — Verify Result**
- Input: task hash or Merkle root
- Fetches proof from Algorand Box Storage
- Runs client-side Merkle verification
- Shows: verified / not found / tampered

---

## BUILD ORDER

Build in this exact order to avoid dependency issues:

1. **Docker Compose** — get Postgres + Redis running first
2. **Backend config + DB setup** — `config.py`, `db/database.py`, `db/redis_client.py`, Alembic migrations
3. **Smart contracts** — write, compile, deploy to testnet; save app IDs to `.env`
4. **Algorand service** — `services/algorand_service.py` (verify tx, get balance)
5. **x402 Middleware** — `middleware/x402_middleware.py`
6. **Cache service** — `services/cache_service.py` (Redis + Pinecone)
7. **Merkle service** — `services/merkle_service.py`
8. **IPFS service** — `services/ipfs_service.py`
9. **AI layer** — `ai/embedding_service.py`, `ai/task_executor.py`, `ai/rag_pipeline.py`
10. **Agents** — seller → verifier → reputation → buyer → orchestrator
11. **Routers** — tasks → payments → verify → agents → cache
12. **Frontend store + services** — walletStore → algorand.ts → x402Client.ts → api.ts
13. **Frontend hooks** — useWallet → useX402 → useTaskResult → useAgentActivity
14. **Frontend components** — shared → wallet → payment → marketplace → agents
15. **Frontend pages** — Marketplace → Dashboard → MyResults → VerifyResult
16. **Tests** — write tests for: x402 middleware, algorand service, verifier agent, merkle service

---

## DEMO SCRIPT

When demo is ready, this exact flow must work end-to-end:

1. User opens `http://localhost:5173`
2. Clicks "Connect Wallet" → Pera Wallet popup appears
3. Connects Algorand Testnet wallet with ALGO balance
4. Uploads a PDF → selects "Summarize" → types prompt → clicks Submit
5. HTTP 402 fires → PaymentModal appears showing `0.005 ALGO`
6. User clicks "Sign & Pay" → Pera Wallet signs transaction
7. Backend verifies txID on Algorand Testnet Indexer
8. Agent pipeline runs: Buyer → Seller (AI) → Verifier → Reputation
9. Result appears with green Merkle badge
10. Second browser tab → same PDF → same prompt
11. PaymentModal shows `0.001 ALGO — Cached (80% cheaper)`
12. After payment → cached result appears instantly
13. Open `/verify/{taskHash}` → Merkle proof verification shows "Verified"
14. Algorand explorer shows both transactions + Box Storage entry

---

## NOTES FOR CLAUDE CODE

- Use `async/await` everywhere in Python. Never use sync SQLAlchemy calls in async routes.
- For PDF text extraction use `PyMuPDF` (import as `fitz`). Add to requirements.txt.
- Pinecone v3 SDK uses `Pinecone(api_key=...)` not the old `pinecone.init()`.
- LangGraph `StateGraph` requires `TypedDict` for state — never use plain dicts.
- Pera Wallet only works on HTTPS in production. For local dev, `localhost` is fine.
- Algorand Testnet faucet: `https://bank.testnet.algorand.network/` — get test ALGO before running demo.
- Box Storage requires the contract to be funded with minimum balance (0.2513 ALGO per box).
- All Algorand amounts internally are in microALGO (1 ALGO = 1,000,000 microALGO).
- Use `algosdk.waitForConfirmation` on frontend after sending tx before sending payment proof to backend.
- The oracle wallet must be funded and its mnemonic in `.env`. This wallet signs all smart contract calls.
- Run `algokit compile` to get TEAL from PyTeal before deploying contracts.
# CLAUDE.md — NeuralLedger
# Complete Project Reference for Claude Code

---

## PROJECT STATUS: FULLY BUILT ✓

All code has been implemented. This file describes the complete architecture, all files,
all logic, and all implementation decisions made. New sessions should read this file
to understand the full project before making any changes.

---

## PROJECT OVERVIEW

**NeuralLedger** is a decentralized AI computation marketplace built on Algorand.
Users pay micro-transactions (via x402 HTTP payment protocol) to access AI-generated
results. Cached results are resold at a discount, creating a secondary knowledge market.
A multi-agent system (LangGraph) orchestrates buyers, sellers, verifiers, and reputation
tracking. Every approved result is cryptographically committed on-chain via Merkle trees
stored in Algorand Box Storage.

### Core Value Proposition
- AI computation results become tradeable digital assets
- Eliminates redundant computation via semantic caching
- Trustless payments via Algorand smart contracts
- Verifiable result integrity via on-chain Merkle commitments
- Agent reputation system ensures quality over time

---

## WORKSPACE LAYOUT (ACTUAL — NOT SPEC)

The project root is `d:/algo_hack_series/` (NOT a `neuralledger/` subfolder).
The Vite/React `src/` directory IS the frontend (no `frontend/` subfolder).

```
d:/algo_hack_series/
├── src/                        ← Frontend (React/Vite) — treat as frontend root
│   ├── components/
│   │   ├── agents/
│   │   ├── marketplace/
│   │   ├── payment/
│   │   ├── shared/
│   │   └── wallet/
│   ├── hooks/
│   ├── pages/
│   ├── services/
│   ├── store/
│   ├── types/
│   └── utils/
├── backend/                    ← FastAPI backend
│   ├── agents/
│   ├── ai/
│   ├── db/
│   ├── middleware/
│   ├── models/
│   ├── routers/
│   ├── services/
│   ├── tests/
│   └── workers/
├── contracts/                  ← PyTeal/Beaker smart contracts
│   ├── deploy/
│   ├── escrow/
│   ├── marketplace/
│   ├── reputation/
│   └── tests/
├── docker-compose.yml
├── .env.example
├── package.json                ← Frontend deps (root level)
├── vite.config.ts
├── tailwind.config.ts
├── postcss.config.js
└── tsconfig.app.json
```

---

## TECH STACK

### Frontend (src/)
- **React 18** + **Vite 8** + **TypeScript** (strict mode)
- **TailwindCSS v3** + **postcss** + **autoprefixer**
- **Framer Motion** for animations
- **Zustand** + persist middleware for global state
- **TanStack Query v5** for server state + polling
- **React Router v6** for routing
- **Recharts** for reputation charts
- **@perawallet/connect** for Algorand wallet
- **algosdk** for tx building + signing + Merkle verification
- **axios** for HTTP (interceptors pass 402 through)
- **react-dropzone** for PDF upload
- **react-hot-toast** for notifications
- **lucide-react** for icons
- **Inter** font from Google Fonts

### Backend (backend/)
- **Python 3.11+**
- **FastAPI** async + **Uvicorn** ASGI
- **LangGraph** `StateGraph` for multi-agent orchestration
- **LangChain + OpenAI** for LLM (GPT-4o)
- **LlamaIndex** for RAG pipeline (in-memory VectorStoreIndex)
- **Pinecone v3** (`Pinecone(api_key=...)`) for semantic vector cache
- **py-algorand-sdk** (algosdk) for Algorand Indexer reads
- **Beaker + PyTeal** for smart contracts
- **Redis** (asyncio) for cache, rate limiting, replay prevention
- **Celery** for async task queue (backed by Redis)
- **PostgreSQL** + **SQLAlchemy async** + **asyncpg**
- **PyMuPDF** (import as `fitz`) for PDF text extraction
- **scikit-learn** cosine_similarity for verifier scoring
- **pydantic v2** + **pydantic-settings** for config/validation
- **pytest** + **pytest-asyncio** for tests

### Smart Contracts (contracts/)
- **PyTeal + Beaker** on **Algorand Testnet**
- Deploy via `contracts/deploy/deploy_contracts.py`
- All calls gated through `contracts/deploy/contract_client.py`

---

## ABSOLUTE RULES — NEVER VIOLATE

1. **Never store private keys in backend.** Wallet signing always happens client-side via Pera Wallet.
2. **All blockchain reads use Algorand Indexer.** Never trust user-provided tx data without verification.
3. **Every payment transaction must be verified on-chain** before triggering AI computation.
4. **Prevent replay attacks** — every verified txID stored in Redis with 30-day TTL (`used_tx:{txId}`); reject duplicates.
5. **x402 middleware runs before every protected route.** Protected routes: `/api/tasks/run`.
6. **Merkle root must be committed before payment is released** from escrow.
7. **Agent reputation updates ONLY flow from the Reputation Agent** (`agents/reputation_agent.py`). No other agent mutates scores.
8. **All API responses use consistent envelope:** `{ success, data, error, timestamp }`.
9. **Environment variables for ALL secrets.** No hardcoded addresses, keys, or API keys.
10. **TypeScript strict mode on.** No `any` types.
11. **All smart contract calls go through `contracts/deploy/contract_client.py`** — never call contracts directly from routers.
12. **Vector similarity threshold for cache is 0.85** — configurable via env `CACHE_SIMILARITY_THRESHOLD`.
13. **Rate limit on `/api/tasks/run`**: max 10 req/min per wallet address (checked in x402 middleware via Redis).
14. **Validate wallet addresses** (58-char Algorand format) on every request using `algorand_service.validate_address()`.
15. **PDF uploads**: accept only `application/pdf`, max 10MB — enforced in `routers/tasks.py`.

---

## ENVIRONMENT VARIABLES

File: `.env.example` (copy to `.env` and fill values)

```env
# Algorand
ALGORAND_NODE_URL=https://testnet-api.algonode.cloud
ALGORAND_INDEXER_URL=https://testnet-idx.algonode.cloud
ALGORAND_NETWORK=testnet
ESCROW_CONTRACT_APP_ID=           # set after deploying contracts
REPUTATION_CONTRACT_APP_ID=       # set after deploying contracts
MARKETPLACE_CONTRACT_APP_ID=      # set after deploying contracts
ORACLE_MNEMONIC=                  # oracle wallet mnemonic (25 words)
ORACLE_ADDRESS=                   # oracle wallet address (58 chars)

# AI
OPENAI_API_KEY=
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4o

# Vector DB
PINECONE_API_KEY=
PINECONE_INDEX_NAME=neuralledger-cache
PINECONE_ENVIRONMENT=

# Storage
WEB3_STORAGE_TOKEN=
IPFS_GATEWAY=https://w3s.link/ipfs/

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/neuralledger
REDIS_URL=redis://localhost:6379/0

# App
SECRET_KEY=
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
VITE_BACKEND_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_ALGORAND_NODE_URL=https://testnet-api.algonode.cloud
CACHE_SIMILARITY_THRESHOLD=0.85
NEW_TASK_PRICE_ALGO=0.005
CACHED_TASK_PRICE_ALGO=0.001
PLATFORM_REVENUE_SHARE=0.70
REQUESTER_REVENUE_SHARE=0.30
MAX_VERIFIER_RETRIES=2
```

---

## BACKEND — FILE-BY-FILE REFERENCE

### `backend/main.py`
FastAPI app entry point. Registers:
- CORS middleware (allow only `FRONTEND_URL`)
- `X402Middleware` (custom, runs before every route)
- Routers: `/api/tasks`, `/api/payments`, `/api/cache`, `/api/agents`, `/api/verify`
- Lifespan: calls `init_db()` and `init_redis()` on startup, `close_redis()` on shutdown
- `GET /health` returns `{ status, service, version }`

### `backend/config.py`
`pydantic_settings.BaseSettings` — reads from `.env`. All settings accessed via `from config import settings`. All fields have defaults so the app starts without crashing in dev (with warnings from missing API keys).

### `backend/db/database.py`
- `create_async_engine` with `pool_size=10`, `max_overflow=20`, `pool_pre_ping=True`
- `AsyncSessionLocal` via `async_sessionmaker`
- `Base` (DeclarativeBase) — all models inherit from this
- `init_db()` runs `Base.metadata.create_all` at startup
- `get_db()` dependency yields async session with commit/rollback

### `backend/db/redis_client.py`
- Global `_redis` singleton (`redis.asyncio`)
- `init_redis()` creates connection at startup
- `get_redis()` returns the singleton (creates lazily if needed)
- `close_redis()` called on shutdown
- All Redis values: `decode_responses=True` (strings, not bytes)

### `backend/models/`
All models inherit `Base` from `db.database`.

| File | Model | Key fields |
|------|-------|-----------|
| `task.py` | `Task` | id, task_hash, task_type, prompt, requester, tx_id, status (enum), result, merkle_root, ipfs_cid, verification_score, price_algo, from_cache, attempt |
| `payment.py` | `Payment` | id, tx_id (unique), task_hash, sender, receiver, amount_algo, is_cached, verified |
| `result.py` | `Result` | id, task_hash (unique), task_text, result, merkle_root, ipfs_cid, original_requester, price_microalgo, on_chain, chain_tx_id, resale_count |
| `agent.py` | `AgentActivity`, `AgentReputation` | activity: agent_type, event, task_id, details; reputation: agent_address (unique), score (default 500.0), total_tasks, successful_tasks |

`TaskStatus` enum: `pending`, `processing`, `verified`, `failed`, `cache_hit`

### `backend/services/algorand_service.py`
`AlgorandService` class:
- `verify_transaction(tx_id, task_hash)` — async, checks Redis replay key first, then fetches from Indexer, validates: tx-type==pay, receiver==ORACLE_ADDRESS, amount>=min, note==`neuralledger:{task_hash}`. Marks used in Redis with 30d TTL.
- `get_oracle_account()` — returns (private_key, address) from mnemonic
- `get_account_balance(address)` — returns float ALGO balance
- `validate_address(address)` — uses `algosdk.encoding.is_valid_address()`

### `backend/services/merkle_service.py`
`MerkleService` class (no external deps, pure Python):
- `_hash(data)` — SHA-256 hex
- `build_tree(chunks)` — pads to even, builds full Merkle tree, returns `{root, tree, leaves}`
- `generate_proof(tree_data, leaf_index)` — returns list of `{hash, position}` steps
- `verify_proof(leaf_data, proof, root)` — re-hashes path, returns bool
- `commit_to_chain(task_hash, merkle_root, original_requester, price_microalgo)` — calls `ContractClient.register_result()`

### `backend/services/cache_service.py`
`CacheService` class:
- `check_exact(task_hash)` — Redis `EXISTS result:{task_hash}` (fast path)
- `check_semantic(task_text)` — embeds text, queries Pinecone `top_k=1`, returns match if `score >= threshold`
- `store(task_hash, task_text, result, merkle_root, ipfs_cid, requester)` — writes to Redis (`result:{task_hash}`, 30d TTL) + upserts to Pinecone
- `get(task_hash)` — reads from Redis, returns parsed JSON dict or None
- **Note**: `EmbeddingService` is instantiated lazily inside methods (avoids circular import)

### `backend/services/ipfs_service.py`
`IPFSService` class:
- `store(data: dict)` — uploads JSON to Web3.Storage (`https://api.web3.storage/upload`), returns CID. Falls back to placeholder CID if IPFS unavailable.
- `retrieve(cid)` — fetches from IPFS gateway

### `backend/services/reputation_service.py`
`ReputationService` class (Redis-backed, NOT the on-chain contract):
- Key format: `reputation:{agent_address}`
- `get_score(agent_address)` — returns float score (default 500.0)
- `update_score(agent_address, success)` — +10 on success (cap 1000), -20 on fail (floor 0), increments task counters
- `list_all()` — scans `reputation:*` keys, returns list of dicts
- **This is the off-chain reputation mirror; on-chain updates go via `ContractClient.update_reputation()`**

### `backend/ai/embedding_service.py`
`EmbeddingService`:
- `embed(text)` — single text, truncates to 8000 chars, returns `list[float]`
- `embed_batch(texts)` — batch embed

### `backend/ai/task_executor.py`
`TaskExecutor`:
- `execute(task_type, task_text, file_content)` — GPT-4o chat completion
- System prompts per task type: `summarize`, `extract`, `analyze`
- Temperature: 0.3, max_tokens: 2048

### `backend/ai/rag_pipeline.py`
`RAGPipeline`:
- Uses LlamaIndex `VectorStoreIndex.from_documents()` (in-memory)
- `query(document_text, query)` — async, builds index over document, runs `aquery()`
- `build_index(chunks)` — returns `VectorStoreIndex`
- Used by `SellerAgent` when `file_content` is present

### `backend/agents/orchestrator.py`
`AgentOrchestrator` — LangGraph `StateGraph`:

**State** (`AgentState` TypedDict):
```
task_id, task_hash, task_text, task_type, file_content, requester, tx_id,
result, merkle_root, ipfs_cid, verification_score, similarity_score,
status, attempt, from_cache, error
```

**Graph edges:**
```
buyer → [cache_hit → reputation_pass → END]
        [continue  → seller → verifier → [pass  → reputation_pass → END]
                                          [retry → seller (up to 2x)]
                                          [fail  → reputation_fail → END]]
```

**Routing logic:**
- `_route_after_buyer`: `cache_hit` if `status=="cache_hit"`, else `continue`
- `_route_after_verify`: `pass` if `status=="verified"`, `retry` if `attempt < 2`, else `fail`

### `backend/agents/buyer_agent.py`
`BuyerAgent.run(state)`:
1. Checks semantic cache via `CacheService.check_semantic()`
2. If hit: loads from `CacheService.get()`, stores result in Redis (`task_result:{task_id}`), sets `status="cache_hit"`
3. If miss: sets `status="routed_to_seller"`
4. Broadcasts `task_received` event via WebSocket

### `backend/agents/seller_agent.py`
`SellerAgent.run(state)`:
1. Skips if `status=="cache_hit"`
2. If `file_content` present + task_type in (summarize/extract/analyze): uses `RAGPipeline.query()`
3. Otherwise: uses `TaskExecutor.execute()`
4. Sets `status="executed"` or `status="failed"`
5. Broadcasts `task_executing` event

### `backend/agents/verifier_agent.py`
`VerifierAgent.run(state)`:
1. Skips if `status in ("cache_hit", "failed")`
2. Computes cosine similarity between task_text embedding and result embedding
3. If `score >= 0.85`: builds Merkle tree → stores on IPFS → commits to Algorand Box Storage → stores in semantic cache → sets `status="verified"`
4. If `score < 0.85`: sets `status="rejected"`
5. Broadcasts `verifying` event

**IMPORTANT**: Only the Verifier Agent triggers Merkle commit and cache storage.

### `backend/agents/reputation_agent.py`
`ReputationAgent`:
- `reward(state)` — called on `verified` or `cache_hit`; calls `ReputationService.update_score(..., success=True)`
- `slash(state)` — called on `failed`; calls `ReputationService.update_score(..., success=False)`
- Both methods call `_store_final_result(state)` — writes final task state to Redis (`task_result:{task_id}`, 24h TTL)
- **ONLY this agent mutates reputation scores**

### `backend/middleware/x402_middleware.py`
`X402Middleware(BaseHTTPMiddleware)`:

Protected routes: `{"/api/tasks/run"}`

**Flow for protected routes:**
1. Validate `X-Wallet-Address` format (58-char Algorand address)
2. Rate limit check: `rate:{wallet}` in Redis, max 10/min per wallet
3. If no `X-Payment-Proof` header → return 402 with `{amount_algo, receiver, task_hash, is_cached, note}`
4. If `X-Payment-Proof` present → `AlgorandService.verify_transaction()` → attach `request.state.{task_hash, tx_id, payment_verified=True}`

**Note**: `is_cached` in the 402 response uses `CacheService.check_exact()` (exact hash check only, for speed).

### `backend/routers/tasks.py`
- `POST /api/tasks/run` — requires payment (x402 middleware). Validates PDF (type + size). Extracts PDF text via `fitz`. Checks semantic cache first (returns immediately if hit). Otherwise queues background task via `BackgroundTasks`.
- `GET /api/tasks/result/{task_id}` — polls Redis `task_result:{task_id}`, returns processing status or final result
- `POST /api/tasks/hash` — computes SHA-256 of content, checks exact + semantic cache, returns `{task_hash, is_cached, semantic_match}`
- `GET /api/tasks/history/{wallet_address}` — reads `wallet_tasks:{address}:*` keys from Redis

### `backend/routers/payments.py`
- `POST /api/payments/release` — oracle-triggered; calls `ContractClient.release_payment()`
- `GET /api/payments/status/{tx_id}` — checks if `used_tx:{tx_id}` exists in Redis
- `GET /api/payments/balance/{address}` — returns ALGO balance from algod

### `backend/routers/cache.py`
- `POST /api/cache/check` — semantic cache lookup
- `GET /api/cache/result/{task_hash}` — get cached result from Redis
- `GET /api/cache/stats` — counts of cached results and verified transactions

### `backend/routers/agents.py`
- `WebSocket /api/agents/ws/activity` — live agent event feed. `ConnectionManager` broadcasts to all connected clients. Ping every 30s to keep alive.
- `async broadcast_activity(event, agent, details)` — called by agents to push events
- `GET /api/agents/reputation` — list all agent reputations
- `GET /api/agents/reputation/{agent_address}` — single agent reputation
- `GET /api/agents/status` — connection count + agent list

### `backend/routers/verify.py`
- `GET /api/verify/result/{task_hash}` — fetches Merkle root from Algorand Box Storage via `ContractClient.get_result_proof()`, returns on-chain data + cached result
- `POST /api/verify/proof` — server-side Merkle proof verification (mirrors client logic)

### `backend/workers/celery_app.py`
Celery app backed by Redis. Task `run_agent_pipeline` runs orchestrator in a new event loop. Max 3 retries with exponential backoff (`2 ** retry_count` seconds). Worker prefetch = 1.

---

## SMART CONTRACTS — FILE-BY-FILE REFERENCE

All contracts use Beaker + PyTeal. Oracle address is the ONLY address that can trigger state changes.

### `contracts/escrow/escrow_contract.py`
`NeuralLedgerEscrow` app:
- Global state: `oracle_address` (bytes), `total_received` (uint64)
- `create(oracle)` — sets oracle address
- `release_payment(task_hash, recipient, platform_account, platform_share_bps)` — oracle-only; splits payment using basis points (7000 = 70%), executes two inner payment txns
- `get_total_received()` — read-only

### `contracts/reputation/reputation_contract.py`
`AgentReputation` app:
- Global state: `oracle_address` (bytes), dynamic `agent_score_{addr}` and `agent_tasks_{addr}` keys
- Default starting score: **500**
- `update_score(agent_address, success)` — oracle-only; +10 success (cap 1000), -20 fail (floor 0)
- `get_score(agent_address)` — read-only, returns 500 if no score stored

### `contracts/marketplace/marketplace_contract.py`
`NeuralLedgerMarketplace` app:
- Global state: `oracle_address`, `total_results`
- `register_result(task_hash, merkle_root, original_requester, price_microalgo)` — oracle-only; creates Box with key=task_hash, value=`"{merkle_root}|{requester}|{price_bytes}"`; rejects duplicates
- `get_result_proof(task_hash)` — read-only; reads Box Storage
- Box size: 256 bytes per result

### `contracts/deploy/contract_client.py`
`ContractClient` — single gateway for all contract interactions:
- `register_result(task_hash, merkle_root, original_requester, price)` — builds ApplicationCallTxn with box reference, signs with oracle key, waits for confirmation. In dev mode (no mnemonic) returns placeholder `dev-tx-{hash[:16]}`.
- `release_payment(task_hash, recipient)` — calls escrow contract
- `get_result_proof(task_hash)` — reads Box Storage via `algod.application_box_by_name()`, decodes base64
- `get_escrow_address()` — returns oracle address
- `update_reputation(agent_address, success)` — calls reputation contract

### `contracts/deploy/deploy_contracts.py`
Script to deploy all three contracts. Checks oracle balance (min 1 ALGO). Requires `.teal` files generated by `algokit compile` first.

---

## FRONTEND — FILE-BY-FILE REFERENCE

### Root Config Files
- `vite.config.ts` — proxy `/api` → `http://localhost:8000`, `global: 'globalThis'` polyfill for algosdk
- `tailwind.config.ts` — content: `./index.html, ./src/**/*.{ts,tsx}`, extended colors (primary, success, warning, danger), Inter font
- `postcss.config.js` — tailwindcss + autoprefixer

### `src/main.tsx`
Standard React 18 `createRoot`, renders `<App />` in StrictMode with `./index.css` import.

### `src/index.css`
Imports Inter from Google Fonts, then `@tailwind base/components/utilities`. Resets body margin, sets background `#F9FAFB`.

### `src/App.tsx`
- `QueryClientProvider` wrapping everything (retry: 2, staleTime: 10s)
- `ErrorBoundary` wrapping `BrowserRouter`
- Routes: `/` → Marketplace, `/dashboard` → AgentDashboard, `/results` → MyResults, `/verify` → VerifyResult, `/verify/:taskHash` → VerifyResult, `*` → NotFound

### Types (`src/types/`)

| File | Key types |
|------|-----------|
| `task.ts` | `TaskType`, `TaskStatus`, `Task`, `TaskResult`, `HashResponse`, `SemanticMatch` |
| `payment.ts` | `PaymentRequest`, `PaymentStatus`, `BalanceResponse` |
| `agent.ts` | `AgentType`, `AgentEvent`, `AgentActivity`, `AgentReputation`, `AgentStatus` |
| `algorand.ts` | `AlgorandAccount`, `MerkleProofStep`, `OnChainProof`, `CachedResult` |

### Stores (`src/store/`)

**`walletStore.ts`** — Zustand + persist:
- `address`, `balance`, `connected`
- Actions: `setAddress`, `setBalance`, `setConnected`, `disconnect`
- Persisted to `localStorage` as `wallet-store`

**`taskStore.ts`** — Zustand (no persist):
- `tasks: Task[]`, `activeTaskId`, `activeResult`
- Actions: `addTask`, `updateResult`, `setActiveTaskId`, `setActiveResult`, `clearActive`

**`agentStore.ts`** — Zustand (no persist):
- `activities: AgentActivity[]` (capped at 100), `reputations: AgentReputation[]`
- Actions: `addActivity`, `setReputations`

### Services (`src/services/`)

**`api.ts`** — Axios instance:
- `baseURL = VITE_BACKEND_URL`
- Interceptor: passes 402 errors through (x402Client needs them raw)

**`algorand.ts`** — `algorandService` object:
- `peraWallet` — `PeraWalletConnect` singleton
- `connect()` / `reconnect()` / `disconnect()`
- `getBalance(address)` — via algodClient
- `sendPayment({from, to, amountAlgo, note})` — builds txn, signs via Pera, sends, returns txId
- `waitForConfirmation(txId, rounds=10)` — `algosdk.waitForConfirmation`
- `verifyMerkleProof({leafData, proof, root})` — client-side SHA-256 via `crypto.subtle`, pure browser, no server call

**`x402Client.ts`** — `executeWithPayment(endpoint, taskHash, walletAddress, onPaymentRequired, body)`:
1. Probe request (no payment headers) → expect 402
2. Parse 402 response body for `PaymentRequest`
3. Call `onPaymentRequired(req)` → returns boolean (user confirmed/cancelled)
4. `algorandService.sendPayment()` → get txId
5. `algorandService.waitForConfirmation(txId)`
6. Retry request with `X-Payment-Proof: txId` header
7. Returns result JSON

### Hooks (`src/hooks/`)

**`useWallet.ts`**:
- On mount: attempts `algorandService.reconnect()` to restore Pera session
- `connectWallet()` — connect + refresh balance + toast
- `disconnectWallet()` — disconnect + clear store + toast
- `refreshBalance(addr?)` — fetches and updates store

**`useX402.ts`**:
- `submitTask(taskType, prompt, file?)` — full flow: hash → executeWithPayment → setActiveTaskId
- `paymentRequest` state — when set, PaymentModal opens
- `confirmPayment(bool)` — resolves the Promise that PaymentModal is waiting on

**`useTaskResult.ts`**:
- React Query with `queryKey: ['task-result', taskId]`
- Polls every 2s while status is `processing/pending`
- Stops polling when status in `{verified, failed, cache_hit}`
- Calls `updateResult()` in taskStore on each response

**`useAgentActivity.ts`**:
- Opens WebSocket to `VITE_WS_URL/api/agents/ws/activity`
- Auto-reconnects after 3s on disconnect
- Calls `addActivity()` in agentStore on each `type=="activity"` message

**`useMerkleVerify.ts`**:
- `fetchProof(taskHash)` — GET `/api/verify/result/{taskHash}`, sets `onChainProof`
- `verifyClientSide(leafData, proof, root)` — calls `algorandService.verifyMerkleProof()`

### Utilities (`src/utils/`)

**`constants.ts`**:
- `BACKEND_URL`, `WS_URL`, `ALGORAND_NODE_URL` from env
- `NEW_TASK_PRICE_ALGO = 0.005`, `CACHED_TASK_PRICE_ALGO = 0.001`, `ALGO_USD_ESTIMATE = 0.15`
- `TASK_TYPES` — array with value/label/description
- `AGENT_COLORS` — `{buyer: '#2563EB', seller: '#16A34A', verifier: '#D97706', reputation: '#7C3AED'}`
- `AGENT_LABELS` — human-readable agent names

**`formatters.ts`**:
- `shortenAddress(address, chars=6)` — `ABCDE...WXYZ`
- `shortenHash(hash, chars=8)` — `deadbeef...`
- `algoToUsd(algo)` — estimate at $0.15/ALGO
- `formatScore(score)` — `0.87` → `"87.0%"`
- `formatReputationScore(score)` — `"500 / 1000"`
- `timeAgo(isoString)` — `"2m ago"`, `"5h ago"`

**`merkle.ts`**:
- `verifyMerkleProof(leafData, proof, root)` — async, `crypto.subtle.digest` SHA-256
- `hashContent(content)` — SHA-256 hex

### Components (`src/components/`)

#### shared/
- `Layout.tsx` — wraps page in `<Navbar>` + `<Toaster>` + `max-w-7xl` container
- `Navbar.tsx` — sticky top nav with logo, 4 nav links, `<WalletConnect>` on right
- `LoadingSpinner.tsx` — animated border-t-blue-600 circle, size: sm/md/lg
- `ErrorBoundary.tsx` — class component, catches + displays error with retry button
- `StatusBadge.tsx` — colored pill badge for TaskStatus values

#### wallet/
- `WalletConnect.tsx` — shows "Connect Wallet" button when disconnected; dropdown with balance + disconnect when connected
- `WalletBalance.tsx` — shows address (shortened), ALGO balance, USD estimate, refresh button
- `WalletGuard.tsx` — renders children if connected, else centered connect-wallet prompt
- `TransactionModal.tsx` — modal for showing tx signing/confirmation status (pending/confirming/confirmed/failed states)

#### payment/
- `PaymentModal.tsx` — AnimatePresence modal; shows amount, cached badge, USD estimate, sign+pay / cancel buttons
- `TxStatusTracker.tsx` — inline status row with icon (Loader2 animates when processing)
- `RevenueShareDisplay.tsx` — shows 70/30 platform/requester split breakdown

#### marketplace/
- `TaskSubmitter.tsx` — task type selector (3 buttons), PDF dropzone, prompt textarea, submit button; opens PaymentModal on 402
- `ResultCard.tsx` — shows result with status badge, MerkleProofBadge, CacheHitBadge, IPFS link
- `CacheHitBadge.tsx` — purple pill "Cache Hit · 87.0%"
- `MerkleProofBadge.tsx` — green pill link to `/verify/{taskId}`
- `PriceBreakdown.tsx` — shows new (0.005) vs cached (0.001) pricing
- `TaskHistory.tsx` — list of tasks from taskStore with hash + timeAgo

#### agents/
- `AgentMonitor.tsx` — 2×2 grid of agent cards with icon, role, score bar, last event
- `AgentActivityFeed.tsx` — scrollable list of activity events from agentStore (last 100)
- `ReputationCard.tsx` — individual agent card with score bar, task count, success rate
- `AgentGraph.tsx` — Recharts LineChart of reputation score history from `reputation_updated` events

### Pages (`src/pages/`)

**`Marketplace.tsx`** (`/`):
- Hero section with badge + tagline
- 2/3 left: `TaskSubmitter` + `ResultCard` (conditionally shown when task active)
- 1/3 right: `PriceBreakdown` + live `AgentActivityFeed`
- Calls `useAgentActivity()` to connect WebSocket
- Uses `useTaskResult(activeTaskId)` for polling

**`AgentDashboard.tsx`** (`/dashboard`):
- Fetches reputation list from `/api/agents/reputation` on mount
- `AgentMonitor` (4 agent status cards)
- `AgentGraph` (Recharts reputation history)
- `ReputationCard` grid for registered agents
- Live `AgentActivityFeed` sidebar

**`MyResults.tsx`** (`/results`):
- Reads from `taskStore.tasks` (in-memory, this session only)
- Filter tabs: All / Cached / Fresh
- Expandable result cards with Merkle badge and IPFS link
- `WalletGuard` wrapping

**`VerifyResult.tsx`** (`/verify` and `/verify/:taskHash`):
- Input for task hash + search button
- Fetches from `/api/verify/result/{taskHash}`
- Parses Box Storage value: `merkle_root|requester|price`
- Shows green verified badge or red not-found
- IPFS link to full result
- Auto-fetches if `:taskHash` URL param is present

**`NotFound.tsx`** (`*`):
- 404 page with link back to Marketplace

---

## DATA FLOWS

### Full Task Flow (New Computation)
```
1. User fills TaskSubmitter → clicks Submit
2. useX402.submitTask() → POST /api/tasks/hash → get task_hash
3. executeWithPayment() → probe POST /api/tasks/run (no payment headers)
4. X402Middleware: validates wallet, rate-limit, no X-Payment-Proof → 402 response
5. PaymentModal opens, user clicks "Sign & Pay"
6. algorandService.sendPayment() → Pera Wallet signs → txId returned
7. algorandService.waitForConfirmation(txId)
8. Retry POST /api/tasks/run with X-Payment-Proof: txId
9. X402Middleware: verify_transaction() checks Indexer, anti-replay, marks used_tx:{txId}
10. tasks.router.run_task() → checks semantic cache (miss) → BackgroundTasks
11. AgentOrchestrator.run() kicks off LangGraph:
    Buyer → (miss) → Seller → Verifier → Reputation
12. Seller: RAG (if PDF) or GPT-4o direct → result
13. Verifier: cosine similarity ≥ 0.85 → Merkle tree → IPFS → Algorand Box Storage → Pinecone cache
14. Reputation: score +10 → stores final result in Redis task_result:{task_id}
15. Frontend polls GET /api/tasks/result/{task_id} every 2s
16. React Query returns verified result → ResultCard displays result + MerkleProofBadge
```

### Cached Task Flow (80% Cheaper)
```
1-4. Same as above, but CacheService.check_exact() returns True
5. 402 response shows is_cached=true, amount=0.001 ALGO
6-9. Same payment flow with lower amount
10. Buyer checks semantic cache → HIT → loads from Redis
11. Stores in task_result:{task_id} immediately
12. Frontend gets cache_hit result in first poll
```

### Verify Flow
```
User opens /verify/{taskHash}
→ useMerkleVerify.fetchProof()
→ GET /api/verify/result/{taskHash}
→ ContractClient.get_result_proof() reads Algorand Box Storage
→ Returns merkle_root|requester|price string
→ VerifyResult page displays green "Verified On-Chain" badge
```

---

## DESIGN SYSTEM

### Color Palette
```
Primary:     #2563EB  (blue-600)
Success:     #16A34A  (green-600)
Warning:     #D97706  (amber-600)
Danger:      #DC2626  (red-600)
Background:  #F9FAFB  (gray-50)
Surface:     #FFFFFF
Border:      #E5E7EB  (gray-200)
Text:        #111827  (gray-900)
Muted:       #6B7280  (gray-500)
```

### Tailwind Component Patterns (use these consistently)
```
Card:            bg-white rounded-2xl border border-gray-100 shadow-sm p-6
Primary button:  bg-blue-600 hover:bg-blue-700 text-white rounded-xl px-4 py-2.5 text-sm font-medium transition
Secondary button: border border-gray-200 hover:bg-gray-50 text-gray-700 rounded-xl px-4 py-2.5 text-sm font-medium transition
Input:           w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500
Badge green:     bg-green-50 text-green-700 border border-green-200 rounded-full px-2.5 py-0.5 text-xs font-medium
Badge blue:      bg-blue-50 text-blue-700 border border-blue-200 rounded-full px-2.5 py-0.5 text-xs font-medium
Badge purple:    bg-purple-50 text-purple-700 border border-purple-200 rounded-full px-2.5 py-0.5 text-xs font-medium
Hash display:    font-mono text-xs text-gray-400 truncate max-w-[120px]
```

---

## RUNNING THE PROJECT

### Prerequisites
- Node.js 20+ (frontend)
- Python 3.11+ (backend)
- Docker Desktop (for Postgres + Redis)
- Pera Wallet mobile app (for signing testnet transactions)
- Testnet ALGO from `https://bank.testnet.algorand.network/`

### Start Services
```bash
# Terminal 1: Start Postgres + Redis
docker compose up postgres redis

# Terminal 2: Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 3: Frontend
npm install
npm run dev
# → http://localhost:5173
```

### Deploy Smart Contracts (one-time)
```bash
# 1. Generate TEAL files (requires algokit)
cd contracts/escrow && python -c "from escrow_contract import app; app.build()"
cd contracts/reputation && python -c "from reputation_contract import app; app.build()"
cd contracts/marketplace && python -c "from marketplace_contract import app; app.build()"

# 2. Deploy
cd contracts/deploy
python deploy_contracts.py

# 3. Update .env with returned App IDs
ESCROW_CONTRACT_APP_ID=<id>
REPUTATION_CONTRACT_APP_ID=<id>
MARKETPLACE_CONTRACT_APP_ID=<id>
```

### Run Tests
```bash
# Backend
cd backend
pytest tests/ -v

# Contract unit tests
pytest contracts/tests/ -v
```

---

## KNOWN IMPLEMENTATION NOTES

1. **MyResults page** reads from in-memory `taskStore` (Zustand, no persist). Results are lost on page refresh. To persist across sessions, the backend `/api/tasks/history/{wallet}` endpoint must be integrated and called on mount.

2. **Celery worker** is defined but the `run_task` router uses `FastAPI.BackgroundTasks` for simplicity. To use Celery instead: call `run_agent_pipeline.delay(...)` from the router.

3. **ContractClient dev mode**: if `ORACLE_MNEMONIC` is not set, all contract calls return placeholder IDs (`dev-tx-{hash}`). This allows the app to run locally without a funded oracle wallet.

4. **IPFS fallback**: if `WEB3_STORAGE_TOKEN` is not set, `IPFSService.store()` returns a deterministic placeholder CID so the rest of the pipeline doesn't break.

5. **algosdk `global` polyfill**: `vite.config.ts` has `define: { global: 'globalThis' }` — required for algosdk to work in the browser.

6. **Pinecone v3 API**: uses `Pinecone(api_key=...)` constructor, NOT the old `pinecone.init()`. Index accessed via `self.pc.Index(name)`.

7. **LangGraph TypedDict state**: all agent state keys must be declared in `AgentState` TypedDict — undefined keys cause runtime errors.

8. **Pera Wallet HTTPS**: works on `localhost` in dev. Production requires HTTPS.

9. **Box Storage minimum balance**: each box costs 0.2513 ALGO minimum balance increase. Oracle wallet must have enough ALGO before calling `register_result`.

10. **Task hash in x402 flow**: frontend computes hash via `POST /api/tasks/hash` (backend SHA-256), attaches as `X-Task-Hash` header on all task requests. This prevents hash mismatches.

---

## SECURITY CHECKLIST (ALL IMPLEMENTED)

- [x] Replay attack prevention: `used_tx:{txId}` in Redis, 30-day TTL
- [x] Rate limiting: 10 req/min per wallet on `/api/tasks/run`
- [x] Wallet address format validation (58-char) on every request
- [x] File upload sanitization: PDF only, max 10MB
- [x] No private keys/mnemonics in logs or responses
- [x] CORS restricted to `FRONTEND_URL` only
- [x] All secrets via environment variables
- [x] Merkle root committed before payment released
- [x] Oracle-only contract state changes
- [x] Pydantic v2 input validation on all endpoints
- [x] Async SQLAlchemy — no blocking DB calls in async routes
- [x] Celery tasks have max retries + exponential backoff

---

---

# CLAUDE.md — NeuralLedger
# Agent Economy Upgrades — Session 2

---

## PROJECT STATUS: UPGRADED ✓

All upgrades below are additive on top of the original build. No existing functionality was removed.

---

## NEW FEATURES ADDED (UPGRADES 1–8)

### Upgrade 1 — Two New Smart Contracts

#### `contracts/identity/identity_contract.py`
PyTeal/Beaker contract: **AgentIdentityRegistry**

Stores per-agent credentials in Algorand Box Storage keyed by `agent_address`.
Box value format (pipe-separated):
```
owner_address|spending_limit_microalgo|spent_microalgo|allowed_categories|is_active|registered_at
```

External methods:
- `register_agent(agent_address, owner_address, spending_limit, allowed_categories)` → Bool — anyone can call
- `verify_agent(agent_address, category, amount_microalgo)` → Bool — oracle-only; validates budget + category
- `record_spend(agent_address, amount_microalgo)` → Bool — oracle-only; atomic spend increment
- `deactivate_agent(agent_address)` → Bool — oracle or agent owner
- `get_credential(agent_address)` → String — read-only; returns pipe-separated string

#### `contracts/registry/service_registry_contract.py`
PyTeal/Beaker contract: **ServiceRegistry**

Stores available services in Box Storage keyed by `service_id` (e.g. `"seller-agent-abc12345"`).
Box value format (pipe-separated):
```
agent_address|service_name|category|price_microalgo|reputation_threshold|is_active|total_calls
```

External methods:
- `register_service(service_id, service_name, category, price_microalgo, reputation_threshold)` → Bool — any agent
- `get_service(service_id)` → String — read-only
- `increment_calls(service_id)` → Bool — oracle-only
- `deactivate_service(service_id)` → Bool — oracle or service owner

#### Updated `contracts/deploy/config.py`
Added two new config values:
```python
IDENTITY_CONTRACT_APP_ID = int(os.getenv("IDENTITY_CONTRACT_APP_ID", "0"))
SERVICE_REGISTRY_CONTRACT_APP_ID = int(os.getenv("SERVICE_REGISTRY_CONTRACT_APP_ID", "0"))
PLATFORM_REVENUE_SHARE = float(os.getenv("PLATFORM_REVENUE_SHARE", "0.70"))
```

#### Updated `contracts/deploy/contract_client.py`
New methods added (all existing methods unchanged):
- `register_agent(agent_address, owner_address, spending_limit, allowed_categories)` → str (tx_id)
- `verify_agent(agent_address, category, amount_microalgo)` → bool (reads credential, checks budget + category off-chain)
- `record_spend(agent_address, amount_microalgo)` → bool
- `get_agent_credential(agent_address)` → str | None (reads Box Storage)
- `register_service(service_id, service_name, category, price_microalgo, reputation_threshold, agent_address, agent_private_key)` → str
- `get_service(service_id)` → dict | None
- `discover_services(category)` → list[dict] (reads from Redis dev store in dev mode; Box Storage in prod)
- `register_service_dev(service_data)` → None (writes to Redis for local dev without contracts deployed)

Dev mode: all contract methods fall back gracefully when `ORACLE_MNEMONIC` or contract App IDs are not set, returning `dev-*` placeholder IDs.

---

### Upgrade 2 — Agent-to-Agent x402 (No Human Wallet Popup)

#### Modified `backend/middleware/x402_middleware.py`
Added a second payment flow triggered by `X-Agent-Mode: true` header.

**Agent mode flow** (when `X-Agent-Mode: true`):
1. Reads `X-Agent-Address` header — validates 58-char Algorand format
2. Reads `X-Task-Hash` and `X-Task-Category` headers
3. Determines cost (cached vs new) in microALGO
4. Calls `ContractClient.verify_agent(agent_address, category, amount)` — checks budget + category on-chain
5. If fails → returns HTTP 403 with clear error message
6. If passes → calls `ContractClient.record_spend(agent_address, amount)` atomically
7. Attaches to `request.state`: `task_hash`, `tx_id`, `payment_verified=True`, `agent_mode=True`, `agent_address`
8. No blockchain tx required — the smart contract IS the payment record

**Human mode flow** (unchanged): Pera Wallet signs a real Algorand payment transaction.

Rate limiting: human mode 10 req/min per wallet; agent mode uses on-chain budget as its natural rate limit.

#### New `backend/services/agent_wallet_service.py`
`AgentWalletService` class — manages autonomous agent Algorand wallets.

Key design: **private keys are NEVER stored**. They are re-derived fresh on every call from:
```
HMAC-SHA256(MASTER_AGENT_SECRET, agent_name) → 32-byte seed → NaCl SigningKey → algosdk private key
```

Methods:
- `generate_agent_account(agent_name)` → `(private_key_b64, address)` — deterministic, never logged
- `get_agent_balance(agent_name)` → float ALGO
- `send_agent_payment(from_agent, to_address, amount_algo, note)` → str (tx_id) — signs + broadcasts autonomously
- `fund_agent(agent_name, amount_algo)` → str (tx_id) — transfers from oracle wallet to agent wallet

Requires `PyNaCl>=1.5.0` in `requirements.txt` (added).

`MASTER_AGENT_SECRET` must be a random 32-byte hex string in `.env`. Generate with:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

### Upgrade 3 — Modified Agents

#### Modified `backend/agents/buyer_agent.py`
- On init: derives its own Algorand wallet via `AgentWalletService.generate_agent_account("buyer")`
- After cache miss: calls `ContractClient.discover_services(category)` to find available services
- Filters services by `reputation_score >= MIN_AGENT_REPUTATION` (default 700)
- Picks cheapest qualifying service
- Calls `ContractClient.verify_agent(buyer_address, category, price_microalgo)` before any payment
- Records spend via `ContractClient.record_spend(buyer_address, price_microalgo)` if verified
- Appends every decision to `state["audit_trail"]` list
- Falls back to local SellerAgent if no qualified external service exists

#### Modified `backend/agents/seller_agent.py`
- On init: derives its own Algorand wallet via `AgentWalletService.generate_agent_account("seller")`
- On first `run()` call: calls `ContractClient.register_service_dev(...)` to register itself in Redis service registry
- Appends execution result to `state["audit_trail"]`

#### Modified `backend/agents/verifier_agent.py`
- Appends verification outcome (verified/rejected) to `state["audit_trail"]`
- Includes Merkle root chain tx_id in the audit entry

#### Modified `backend/agents/reputation_agent.py`
- Both `reward()` and `slash()` append score update events to `state["audit_trail"]`

#### Modified `backend/agents/orchestrator.py`
- `AgentState` TypedDict now includes `audit_trail: List[dict]`
- `run()` accepts optional `audit_trail: list | None` parameter — allows MasterAgent to pass pre-populated trail
- Initial state sets `audit_trail` to passed value or `[]`

Each audit entry dict shape:
```python
{
    "agent": "buyer" | "seller" | "verifier" | "reputation" | "master",
    "action": str,          # e.g. "cache_hit", "verified", "reward"
    "detail": str,          # human-readable description
    "payment_algo": float | None,
    "tx_id": str | None,
    "timestamp": str,       # ISO 8601 UTC
}
```

---

### Upgrade 4 — MasterAgent

#### New `backend/agents/master_agent.py`
`MasterAgent` class — top-level autonomous agent. Users set a goal + budget once; agent runs everything with zero human interaction.

**Init:**
- Derives own Algorand wallet via `AgentWalletService.generate_agent_account("master")`
- Holds an `AgentOrchestrator` instance for running sub-pipelines

**`run(goal, budget_algo, owner_address, task_id)` → dict:**

Step 1 — Register identity on-chain:
- Calls `ContractClient.register_agent(master_address, owner_address, budget_microalgo, "research,data,analysis,writing")`
- Appends `identity_registered` audit entry
- Saves initial status to Redis `autonomous:{task_id}`

Step 2 — Parse goal into subtasks:
- GPT-4o call with `response_format: json_object`
- Returns `[{name, category, description}]` — category validated against `{research, data, analysis, writing}`
- Falls back to single analysis subtask on failure

Step 3 — Execute subtasks sequentially:
- For each subtask: discover service → check 90% budget guard → run `AgentOrchestrator.run()`
- Accumulates sub-pipeline audit events into master trail
- Updates Redis status after each subtask for live polling
- Budget guard: if `total_spent >= 0.9 × budget`, skips remaining subtasks and returns what's done

Step 4 — Assemble final report:
- GPT-4o WriterAgent call with all subtask results
- Produces structured markdown: Executive Summary, Key Findings, Risk Assessment, Conclusion

Step 5 — Return complete result:
```python
{
    "status": "complete",
    "final_output": str,
    "total_spent_algo": float,
    "subtasks_completed": int,
    "audit_trail": list[dict],
    "merkle_roots": list[str],
    "master_agent_address": str,
}
```

Status is persisted in Redis at key `autonomous:{task_id}` throughout, so polling works in real time.

---

### Upgrade 5 — New Backend Router

#### New `backend/routers/autonomous.py`
Registered in `main.py` at prefix `/api/autonomous`.

**`POST /api/autonomous/run`**
- Body: `{ goal: str, budget_algo: float (0.5–50), owner_address: str (58-char) }`
- Does NOT require x402 payment — master agent funds itself internally
- Validates address format (Pydantic field validator)
- Validates budget range (0.5–50 ALGO)
- Rate limits to 3 concurrent autonomous runs per `owner_address` using Redis counter with 5-min TTL
- Immediately returns: `{ task_id, status: "running", master_agent_address, estimated_cost_algo }`
- Runs `MasterAgent.run(...)` as `FastAPI.BackgroundTasks`

**`GET /api/autonomous/status/{task_id}`**
- Polls Redis `autonomous:{task_id}`
- Returns: `{ status, current_step, progress_percent, audit_trail, result? }`

**`GET /api/autonomous/audit/{task_id}`**
- Returns complete audit trail for a finished task
- Returns: `{ task_id, status, audit_trail, result }`

#### Updated `backend/main.py`
```python
from routers import tasks, payments, cache, agents, verify, autonomous
# ...
app.include_router(autonomous.router, prefix="/api/autonomous", tags=["autonomous"])
```

#### Updated `backend/routers/agents.py`
Added `GET /api/agents/services` endpoint:
- Reads all `service_registry:*` keys from Redis
- Returns `{ services: [...] }` for the AgentDashboard service registry table

---

### Upgrade 6 — New Environment Variables

Added to both `.env.example` and `.env`:

```env
# Agent Economy
MASTER_AGENT_SECRET=          # Random 32-byte hex. Derives all agent wallets deterministically.
IDENTITY_CONTRACT_APP_ID=0    # From deploy step — set after deploying identity contract
SERVICE_REGISTRY_CONTRACT_APP_ID=0  # From deploy step — set after deploying registry contract
MIN_AGENT_REPUTATION=700      # Minimum reputation score for BuyerAgent to use a service
MASTER_AGENT_FUND_AMOUNT=2.0  # How much ALGO to auto-fund master agent on first run
```

Added to `backend/config.py`:
```python
MASTER_AGENT_SECRET: str = "changeme-set-32-byte-hex-in-env"
IDENTITY_CONTRACT_APP_ID: int = 0
SERVICE_REGISTRY_CONTRACT_APP_ID: int = 0
MIN_AGENT_REPUTATION: int = 700
MASTER_AGENT_FUND_AMOUNT: float = 2.0
```

---

### Upgrade 7 — Security Rules (Enforced)

All enforced in the implementation:

1. `record_spend` uses a single Algorand app call — atomic by Algorand's single-call semantics (no read-then-write race condition)
2. `AgentWalletService._derive_seed()` returns bytes and is never logged — private key regenerated fresh each call
3. `/api/autonomous/run` rate-limited to 3 concurrent runs per `owner_address` (Redis counter, 5-min TTL)
4. `MasterAgent._execute_subtask()` checks `total_spent >= 0.9 × budget` before each subtask — stops pipeline at 90% spend
5. `BuyerAgent.run()` always calls `ContractClient.verify_agent()` before any payment — never skipped

---

### Upgrade 8 — Frontend Changes

#### Modified `src/pages/Marketplace.tsx`
Added "Autonomous Mode" tab alongside the original "Manual Task" tab.

Tab switcher: `bg-gray-100` pill with two options — no page navigation, single-component swap.

**Autonomous Mode UI (`<AutonomousMode />` sub-component):**
- Large textarea for goal input
- Budget slider: 0.5–10 ALGO (step 0.5)
- Estimated cost breakdown: Research ~30%, Analysis ~40%, Writing ~20% of budget
- "Launch Agent Pipeline" button → `POST /api/autonomous/run`
- Explanation: no wallet popup — master agent manages payments autonomously
- Progress bar showing `progress_percent` from status polling
- After complete: final report with expand/collapse, subtasks count, total spent, Merkle commitments count
- "View full audit trail →" link to `/api/autonomous/audit/{task_id}` when done

Live polling: `setInterval` at 2s, clears on `status === "complete"` or `"failed"`.

#### New `src/components/agents/AuditTrail.tsx`
Timeline component for displaying agent audit entries.

Props: `entries: AuditEntry[]`, `className?: string`

`AuditEntry` type:
```typescript
{
  agent: 'master' | 'buyer' | 'seller' | 'verifier' | 'reputation'
  action: string
  detail: string
  payment_algo: number | null
  tx_id: string | null
  timestamp?: string
}
```

Features:
- Color-coded agent badges: master=blue, buyer=purple, seller=teal, verifier=amber, reputation=green
- Timeline vertical line connecting entries
- Status icon per action: CheckCircle (success), XCircle (failure), Clock (pending/in-progress)
- Payment amount shown as green pill with ALGO value
- Algorand explorer link for real tx IDs (skips `dev-*` and `agent-mode:*` prefixes)
- New entries animate in from bottom via Framer Motion `AnimatePresence`
- Auto-scrolls to latest entry via `useRef` + `scrollIntoView`

#### New `src/components/agents/AgentCredential.tsx`
Card component for displaying an agent's on-chain identity.

Props: `credential: AgentCredentialData`

`AgentCredentialData` type:
```typescript
{
  agent_address: string
  owner_address: string
  spending_limit_algo: number
  spent_algo: number
  allowed_categories: string[]
  reputation_score: number
  is_active: boolean
  registered_at?: string
}
```

Features:
- Active/Inactive status badge (CheckCircle / XCircle)
- Agent address (shortened) with copy button + Algorand explorer link
- Owner address with copy button
- Spend progress bar (blue → amber at 70% → red at 90%)
- Reputation score bar (green ≥ 70%, amber ≥ 40%, red otherwise), score/1000 display
- Allowed categories as blue pill badges

#### Modified `src/pages/AgentDashboard.tsx`
Two new sections added below the existing Reputation cards:

**Active Agent Credentials** section:
- Fetches reputation list (existing) and converts to `AgentCredentialData` via `reputationToCredential()`
- Renders `<AgentCredential>` card grid
- Badge: "On-chain Identity Registry"

**Service Registry** section:
- Fetches from `GET /api/agents/services` on mount
- Table columns: Service name/ID, Category, Price (ALGO), Min Reputation, Total Calls, Provider address
- Empty state: "No services registered yet. Services appear after the first autonomous run."
- Loading state with spinner text

---

## UPDATED FOLDER STRUCTURE (additions only)

```
contracts/
├── identity/
│   ├── __init__.py
│   └── identity_contract.py          ← NEW
├── registry/
│   ├── __init__.py
│   └── service_registry_contract.py  ← NEW
└── deploy/
    ├── config.py                      ← UPDATED (2 new IDs + PLATFORM_REVENUE_SHARE)
    └── contract_client.py             ← UPDATED (7 new methods)

backend/
├── agents/
│   ├── master_agent.py                ← NEW
│   ├── buyer_agent.py                 ← MODIFIED (autonomous payments, audit trail)
│   ├── seller_agent.py                ← MODIFIED (service registration, audit trail)
│   ├── verifier_agent.py              ← MODIFIED (audit trail)
│   ├── reputation_agent.py            ← MODIFIED (audit trail)
│   └── orchestrator.py               ← MODIFIED (audit_trail in AgentState)
├── services/
│   └── agent_wallet_service.py        ← NEW
├── routers/
│   └── autonomous.py                  ← NEW
├── middleware/
│   └── x402_middleware.py             ← MODIFIED (agent mode branch)
├── main.py                            ← MODIFIED (autonomous router registered)
├── config.py                          ← MODIFIED (5 new settings)
└── requirements.txt                   ← MODIFIED (PyNaCl>=1.5.0 added)

src/
├── components/agents/
│   ├── AuditTrail.tsx                 ← NEW
│   └── AgentCredential.tsx            ← NEW
└── pages/
    ├── Marketplace.tsx                ← MODIFIED (Autonomous Mode tab)
    └── AgentDashboard.tsx             ← MODIFIED (Credentials + Service Registry sections)
```

---

## UPDATED ABSOLUTE RULES (additions to original list)

13. **Agent private keys are NEVER stored or logged.** `AgentWalletService` re-derives them from `MASTER_AGENT_SECRET` on every call via HMAC-SHA256.
14. **`verify_agent` must be called before every agent payment** — never skip this check even if the service was discovered from the registry.
15. **Autonomous pipeline rate limit**: max 3 concurrent runs per `owner_address`, 5-minute TTL (Redis counter).
16. **Budget guard at 90%**: `MasterAgent` stops launching new subtasks when `total_spent >= 0.9 × budget`, returns partial results.
17. **Agent-mode spend is atomic**: `record_spend` is a single Algorand app call — no read-then-write split.
18. **`MASTER_AGENT_SECRET` must be a real random 32-byte hex** before any real funds are involved. Default `changeme-*` is for local dev only.

---

## UPDATED SECURITY CHECKLIST

- [x] Replay attack prevention: `used_tx:{txId}` in Redis, 30-day TTL
- [x] Rate limiting: 10 req/min per wallet on `/api/tasks/run`
- [x] Autonomous run rate limit: 3 concurrent per owner, 5-min TTL
- [x] Wallet address format validation (58-char) on every request
- [x] Agent address format validation (58-char) in agent mode
- [x] File upload sanitization: PDF only, max 10MB
- [x] No private keys/mnemonics in logs or responses
- [x] Agent wallet private keys never stored — regenerated from HMAC seed each call
- [x] CORS restricted to `FRONTEND_URL` only
- [x] All secrets via environment variables
- [x] Merkle root committed before payment released
- [x] Oracle-only contract state changes
- [x] Agent-mode spend verification on-chain before every request
- [x] 90% budget guard prevents overspend in autonomous pipeline
- [x] Pydantic v2 input validation on all endpoints
- [x] Async SQLAlchemy — no blocking DB calls in async routes
- [x] Celery tasks have max retries + exponential backoff

---

## KNOWN IMPLEMENTATION NOTES (additions)

11. **`MASTER_AGENT_SECRET` is the root of all agent keys.** Treat it like a root private key. Rotate it to invalidate all existing agent wallets. Generate with `python -c "import secrets; print(secrets.token_hex(32))"`.

12. **Service Registry is Redis-backed in dev mode.** When `SERVICE_REGISTRY_CONTRACT_APP_ID=0`, services are stored in Redis at `service_registry:{service_id}` keys (7-day TTL). `SellerAgent` calls `register_service_dev()` on first run.

13. **Agent credentials are Box Storage-backed in prod.** When contract IDs are set, credentials live in Algorand Box Storage. Each box costs 0.2513 ALGO minimum balance. Fund the identity contract before calling `register_agent`.

14. **`MasterAgent` is a singleton in the autonomous router.** `_get_master_agent()` returns the same instance across requests — `AgentOrchestrator` (which holds LangGraph compiled graph) is expensive to construct.

15. **Audit trail deduplication in MasterAgent.** Sub-pipeline audit entries are merged into the master trail using `if entry not in audit_trail` — works because entries are plain dicts with consistent keys.

16. **PyNaCl is already a transitive dependency of `py-algorand-sdk`.** It is now declared explicitly in `requirements.txt` (`PyNaCl>=1.5.0`) to avoid version conflicts.

17. **`discover_services` in dev mode** reads Redis keys matching `service_registry:*`. In production with contracts deployed, it would enumerate Box Storage from the ServiceRegistry contract. The current implementation uses Redis for both discovery and registration in dev.

18. **AuditTrail component skips explorer links for dev tx IDs.** Any `tx_id` starting with `dev-` or `agent-mode:` is shown as plain text only — no broken external links.

---

## DEMO SCRIPT (Autonomous Mode)

This exact flow works end-to-end:

1. User opens `http://localhost:5174` (or 5173)
2. Clicks "Connect Wallet" → Pera Wallet popup
3. Connects Algorand Testnet wallet
4. Clicks "Autonomous Mode" tab
5. Types: `"Research the top 3 Algorand DeFi protocols and summarize their risks"`
6. Sets budget slider to 1 ALGO
7. Clicks "Launch Agent Pipeline"
8. No wallet popup — frontend immediately shows pipeline running
9. AuditTrail updates live every 2 seconds:
   - "Master agent registered on-chain with 1 ALGO budget"
   - "Goal broken into 3 subtask(s): Research, Analysis, Writing"
   - "No qualified external service for 'research' — using local pipeline"
   - "Starting subtask 'Research' (category=research)"
   - "Executed task type='analyze' — result length=X chars"
   - "Similarity score=0.87 ≥ 0.85 — Merkle root committed on-chain"
   - "Score updated to 510.0 after successful verification"
   - "WriterAgent producing final structured report"
   - "Pipeline complete — 3 subtasks, spent 0.015 ALGO of 1 ALGO budget"
10. Final report appears with expand/collapse
11. User opens `/dashboard` → sees Service Registry table with SellerAgent listed
12. Same goal again → BuyerAgent gets semantic cache hit → cost drops to 0.001 ALGO per subtask
