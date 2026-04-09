from db.redis_client import get_redis
from config import settings
import json
import logging

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self):
        self._index = None
        self.threshold = settings.CACHE_SIMILARITY_THRESHOLD

    def _get_index(self):
        """Lazy Pinecone init — only fails if actually called without a key."""
        if self._index is None:
            if not settings.PINECONE_API_KEY:
                raise RuntimeError("PINECONE_API_KEY not set — semantic cache unavailable")
            from pinecone import Pinecone
            pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            self._index = pc.Index(settings.PINECONE_INDEX_NAME)
        return self._index

    def _get_embedder(self):
        from ai.embedding_service import EmbeddingService
        return EmbeddingService()

    async def check_exact(self, task_hash: str) -> bool:
        redis = await get_redis()
        return await redis.exists(f"result:{task_hash}") > 0

    async def check_semantic(self, task_text: str) -> dict | None:
        try:
            index = self._get_index()
            embedder = self._get_embedder()
            embedding = await embedder.embed(task_text)
            results = index.query(
                vector=embedding,
                top_k=1,
                include_metadata=True,
            )

            if not results.matches:
                return None

            top = results.matches[0]
            if top.score >= self.threshold:
                logger.info(f"Semantic cache hit: score={top.score:.3f}")
                return {
                    "task_hash": top.id,
                    "score": top.score,
                    "metadata": top.metadata,
                }

            return None

        except Exception as e:
            logger.warning(f"Semantic cache unavailable: {e}")
            return None

    async def store(
        self, task_hash: str, task_text: str, result: str,
        merkle_root: str, ipfs_cid: str, requester: str
    ):
        redis = await get_redis()

        cache_data = {
            "result": result,
            "merkle_root": merkle_root,
            "ipfs_cid": ipfs_cid,
            "requester": requester,
            "task_hash": task_hash,
        }

        await redis.setex(
            f"result:{task_hash}",
            86400 * 30,
            json.dumps(cache_data),
        )

        # Only upsert to Pinecone if key is configured
        try:
            index = self._get_index()
            embedder = self._get_embedder()
            embedding = await embedder.embed(task_text)
            index.upsert(vectors=[{
                "id": task_hash,
                "values": embedding,
                "metadata": {
                    "task_hash": task_hash,
                    "merkle_root": merkle_root,
                    "ipfs_cid": ipfs_cid,
                    "requester": requester,
                },
            }])
        except Exception as e:
            logger.warning(f"Pinecone upsert skipped: {e}")

    async def get(self, task_hash: str) -> dict | None:
        redis = await get_redis()
        data = await redis.get(f"result:{task_hash}")
        if data:
            return json.loads(data)
        return None
