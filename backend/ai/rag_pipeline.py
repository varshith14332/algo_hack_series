from llama_index.core import VectorStoreIndex, Document, Settings as LlamaSettings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from config import settings
import logging

logger = logging.getLogger(__name__)


class RAGPipeline:
    def __init__(self):
        LlamaSettings.embed_model = OpenAIEmbedding(
            model=settings.OPENAI_EMBEDDING_MODEL,
            api_key=settings.OPENAI_API_KEY,
        )
        LlamaSettings.llm = OpenAI(
            model=settings.OPENAI_CHAT_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.2,
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
