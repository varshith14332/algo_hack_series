from openai import AsyncOpenAI
from config import settings
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPTS = {
    "summarize": (
        "You are an expert document summarizer. Produce a clear, concise, and accurate "
        "summary of the provided content. Include key points, findings, and conclusions."
    ),
    "extract": (
        "You are an expert data extractor. Extract and structure the key information, "
        "entities, facts, and data points from the provided content in a well-organized format."
    ),
    "analyze": (
        "You are an expert analyst. Provide a deep, insightful analysis of the provided "
        "content. Identify patterns, implications, strengths, weaknesses, and recommendations."
    ),
}

DEFAULT_SYSTEM = (
    "You are a helpful AI assistant. Respond accurately and thoroughly to the user's request."
)


class TaskExecutor:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
        self.model = settings.OPENAI_CHAT_MODEL

    async def execute(self, task_type: str, task_text: str, file_content: str | None = None) -> str:
        system_prompt = SYSTEM_PROMPTS.get(task_type, DEFAULT_SYSTEM)

        user_content = task_text
        if file_content:
            user_content += f"\n\n--- Document Content ---\n{file_content[:6000]}"

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.3,
                max_tokens=2048,
            )
            result = response.choices[0].message.content
            logger.info(f"Task executed [{task_type}]: {len(result)} chars")
            return result
        except Exception as e:
            logger.error(f"Task execution error: {e}")
            raise
