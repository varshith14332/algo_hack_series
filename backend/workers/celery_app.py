from celery import Celery
from config import settings
import logging

logger = logging.getLogger(__name__)

celery_app = Celery(
    "neuralledger",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_max_retries=3,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "workers.celery_app.run_agent_pipeline": {"queue": "tasks"},
    },
)


@celery_app.task(
    name="workers.celery_app.run_agent_pipeline",
    bind=True,
    max_retries=3,
    default_retry_delay=5,
)
def run_agent_pipeline(self, task_id: str, task_hash: str, task_text: str,
                       task_type: str, requester: str, tx_id: str,
                       file_content: str | None = None):
    import asyncio
    from agents.orchestrator import AgentOrchestrator

    try:
        orchestrator = AgentOrchestrator()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            orchestrator.run(
                task_id=task_id,
                task_hash=task_hash,
                task_text=task_text,
                task_type=task_type,
                requester=requester,
                tx_id=tx_id,
                file_content=file_content,
            )
        )
        return result
    except Exception as exc:
        logger.error(f"Celery task {task_id} failed: {exc}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
