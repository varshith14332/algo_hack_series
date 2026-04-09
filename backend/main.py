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


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting NeuralLedger API...")
    await init_db()
    await init_redis()
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
app.include_router(autonomous.router, prefix="/api/autonomous", tags=["autonomous"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "neuralledger", "version": "1.0.0"}
