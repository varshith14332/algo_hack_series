from openai import AsyncOpenAI
from config import settings
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_EMBEDDING_MODEL

    async def embed(self, text: str) -> list[float]:
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text[:8000],  # Truncate to model limit
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            raise

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=[t[:8000] for t in texts],
            )
            return [d.embedding for d in response.data]
        except Exception as e:
            logger.error(f"Batch embedding error: {e}")
            raise
