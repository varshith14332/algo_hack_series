from llama_index.core import VectorStoreIndex, Document, Settings as LlamaSettings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from config import settings
import logging

logger = logging.getLogger(__name__)


class RAGPipeline:
    def __init__(self):
        ollama_base = settings.OPENAI_BASE_URL.replace("/v1", "")
        LlamaSettings.embed_model = OllamaEmbedding(
            model_name=settings.OPENAI_EMBEDDING_MODEL,
            base_url=ollama_base,
        )
        LlamaSettings.llm = Ollama(
            model=settings.OPENAI_CHAT_MODEL,
            base_url=ollama_base,
            temperature=0.2,
            request_timeout=120.0
        )

    async def query(self, document_text: str, query: str) -> str:
        """Run RAG over a document, return answer to query."""
        try:
            doc = Document(text=document_text)
            index = VectorStoreIndex.from_documents([doc])
            query_engine = index.as_query_engine(similarity_top_k=3)
            response = await query_engine.aquery(query)
            return str(response)
        except Exception as e:
            logger.error(f"RAG pipeline error: {e}")
            raise

    async def build_index(self, chunks: list[str]) -> VectorStoreIndex:
        """Build a vector index from text chunks."""
        docs = [Document(text=chunk) for chunk in chunks]
        return VectorStoreIndex.from_documents(docs)
