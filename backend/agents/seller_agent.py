from ai.task_executor import TaskExecutor
from ai.rag_pipeline import RAGPipeline
from services.agent_wallet_service import AgentWalletService
from config import settings
import logging

logger = logging.getLogger(__name__)


class SellerAgent:
    def __init__(self):
        self.executor = TaskExecutor()
        self.rag = RAGPipeline()
        self.wallet_service = AgentWalletService()
        self.contract_client = None
        # This agent's own Algorand wallet
        self._private_key, self.address = self.wallet_service.generate_agent_account("seller")
        logger.info(f"[SellerAgent] Wallet: {self.address[:16]}...")
        self._registered = False

    async def register_on_chain(self):
        """Register this agent in the ServiceRegistry on first use."""
        if self._registered:
            return
        
        if self.contract_client is None:
            from contracts.deploy.contract_client import ContractClient
            self.contract_client = ContractClient()
        
        try:
            service_data = {
                "service_id": f"neuralledger-seller-v1",
                "service_name": "AI Task Execution",
                "category": "research,data,analysis,writing",
                "price_microalgo": int(settings.NEW_TASK_PRICE_ALGO * 1_000_000),
                "reputation_threshold": 0,
                "reputation_score": 750,
                "is_active": True,
                "total_calls": 0,
                "agent_address": self.address,
            }
            await self.contract_client.register_service_dev(service_data)
            logger.info(f"[SellerAgent] Registered in ServiceRegistry as {service_data['service_id']}")
            self._registered = True
        except Exception as e:
            logger.warning(f"[SellerAgent] Service registration failed: {e}")
            self._registered = True  # Prevent repeated failures

    async def receive_payment(self, from_agent: str, amount_algo: float) -> str:
        """
        Accept payment from another agent after successful delivery.
        
        from_agent sends amount_algo to seller's wallet address.
        Returns txID.
        
        NOTE: In the current agent-mode flow, payment is recorded via
        smart contract mandate (not a direct transfer). This method
        is used only when a direct wallet-to-wallet transfer is needed.
        """
        seller_address = await self.wallet_service.get_address("seller")
        txid = await self.wallet_service.send_agent_payment(
            from_agent=from_agent,
            to_address=seller_address,
            amount_algo=amount_algo,
            note=f"payment:neuralledger-seller-v1",
        )
        return txid

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
        await self.register_on_chain()

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
