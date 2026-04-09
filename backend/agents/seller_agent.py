from ai.task_executor import TaskExecutor
from ai.rag_pipeline import RAGPipeline
from services.agent_wallet_service import AgentWalletService
import logging

logger = logging.getLogger(__name__)

agent_wallet_service = AgentWalletService()


class SellerAgent:
    def __init__(self):
        self.executor = TaskExecutor()
        self.rag = RAGPipeline()
        # This agent's own Algorand wallet
        self._private_key, self.address = agent_wallet_service.generate_agent_account("seller")
        logger.info(f"[SellerAgent] Wallet: {self.address[:16]}...")
        self._registered = False

    async def _ensure_registered(self):
        """Register this agent in the ServiceRegistry on first use."""
        if self._registered:
            return
        try:
            from contracts.deploy.contract_client import ContractClient
            client = ContractClient()
            service_data = {
                "service_id": f"seller-agent-{self.address[:8]}",
                "service_name": "NeuralLedger SellerAgent",
                "category": "analysis",
                "price_microalgo": 1000,  # 0.001 ALGO
                "reputation_threshold": 0,
                "reputation_score": 750,
                "is_active": True,
                "total_calls": 0,
                "agent_address": self.address,
            }
            await client.register_service_dev(service_data)
            logger.info(f"[SellerAgent] Registered in ServiceRegistry as {service_data['service_id']}")
            self._registered = True
        except Exception as e:
            logger.warning(f"[SellerAgent] Service registration failed: {e}")
            self._registered = True  # Prevent repeated failures

    async def run(self, state: dict) -> dict:
        # Skip if already resolved from cache
        if state.get("status") == "cache_hit":
            return state

        task_text = state["task_text"]
        task_type = state["task_type"]
        file_content = state.get("file_content")
        task_id = state["task_id"]
        audit_trail: list = state.get("audit_trail", [])

        logger.info(f"[SellerAgent] Executing task {task_id} type={task_type}")

        # Register in service registry on first use
        await self._ensure_registered()

        try:
            from routers.agents import broadcast_activity
            await broadcast_activity(
                event="task_executing",
                agent="seller",
                details={"task_id": task_id, "task_type": task_type},
            )
        except Exception:
            pass

        try:
            if file_content and task_type in ("summarize", "extract", "analyze"):
                result = await self.rag.query(
                    document_text=file_content,
                    query=task_text,
                )
            else:
                result = await self.executor.execute(
                    task_type=task_type,
                    task_text=task_text,
                    file_content=file_content,
                )

            audit_trail.append({
                "agent": "seller",
                "action": "result_produced",
                "detail": f"Executed task type='{task_type}' — result length={len(result)} chars",
                "payment_algo": None,
                "tx_id": None,
            })

            state["result"] = result
            state["status"] = "executed"
            state["audit_trail"] = audit_trail
            logger.info(f"[SellerAgent] Task {task_id} executed successfully")

        except Exception as e:
            logger.error(f"[SellerAgent] Task {task_id} failed: {e}")
            audit_trail.append({
                "agent": "seller",
                "action": "execution_failed",
                "detail": str(e),
                "payment_algo": None,
                "tx_id": None,
            })
            state["error"] = str(e)
            state["status"] = "failed"
            state["audit_trail"] = audit_trail

        return state
