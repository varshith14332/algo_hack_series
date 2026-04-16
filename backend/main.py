from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routers import tasks, payments, cache, agents, verify, autonomous
from middleware.x402_middleware import X402Middleware
from db.database import init_db
from db.redis_client import init_redis, close_redis
from config import settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# Build allowed origins list for CORS (bulletproof for local dev)
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

# Also add whatever is in .env
if settings.FRONTEND_URL not in allowed_origins:
    allowed_origins.append(settings.FRONTEND_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting NeuralLedger API...")
    await init_db()
    await init_redis()
    
    # Register seller agent on startup
    try:
        from agents.seller_agent import SellerAgent
        seller = SellerAgent()
        await seller.register_on_chain()
        logger.info("SellerAgent registered on startup")
    except Exception as e:
        logger.warning(f"SellerAgent registration failed: {e}")
    
    yield
    await close_redis()
    logger.info("NeuralLedger API shutdown complete")


app = FastAPI(
    title="NeuralLedger API",
    version="1.0.0",
    description="Decentralized AI computation marketplace on Algorand",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.add_middleware(X402Middleware)

app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
app.include_router(cache.router, prefix="/api/cache", tags=["cache"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(verify.router, prefix="/api/verify", tags=["verify"])
app.include_router(autonomous.router, prefix="/api/autonomous", tags=["autonomous"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "neuralledger", "version": "1.0.0"}
