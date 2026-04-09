from langgraph.graph import StateGraph, END
from agents.buyer_agent import BuyerAgent
from agents.seller_agent import SellerAgent
from agents.verifier_agent import VerifierAgent
from agents.reputation_agent import ReputationAgent
from typing import TypedDict, Optional, List
import logging

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    task_id: str
    task_hash: str
    task_text: str
    task_type: str
    file_content: Optional[str]
    requester: str
    tx_id: str
    result: Optional[str]
    merkle_root: Optional[str]
    ipfs_cid: Optional[str]
    verification_score: Optional[float]
    similarity_score: Optional[float]
    status: str
    attempt: int
    from_cache: bool
    error: Optional[str]
    audit_trail: List[dict]


class AgentOrchestrator:
    def __init__(self):
        self.buyer = BuyerAgent()
        self.seller = SellerAgent()
        self.verifier = VerifierAgent()
        self.reputation = ReputationAgent()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("buyer", self.buyer.run)
        workflow.add_node("seller", self.seller.run)
        workflow.add_node("verifier", self.verifier.run)
        workflow.add_node("reputation_pass", self.reputation.reward)
        workflow.add_node("reputation_fail", self.reputation.slash)

        workflow.set_entry_point("buyer")

        # Buyer routes: cache hit ends early, else goes to seller
        workflow.add_conditional_edges(
            "buyer",
            self._route_after_buyer,
            {
                "cache_hit": "reputation_pass",
                "continue": "seller",
            },
        )

        workflow.add_edge("seller", "verifier")

        workflow.add_conditional_edges(
            "verifier",
            self._route_after_verify,
            {
                "pass": "reputation_pass",
                "retry": "seller",
                "fail": "reputation_fail",
            },
        )

        workflow.add_edge("reputation_pass", END)
        workflow.add_edge("reputation_fail", END)

        return workflow.compile()

    def _route_after_buyer(self, state: AgentState) -> str:
        if state.get("status") == "cache_hit":
            return "cache_hit"
        return "continue"

    def _route_after_verify(self, state: AgentState) -> str:
        if state["status"] == "verified":
            return "pass"
        elif state.get("attempt", 0) < 2:
            state["attempt"] = state.get("attempt", 0) + 1
            return "retry"
        else:
            return "fail"

    async def run(
        self, task_id: str, task_hash: str, task_text: str,
        task_type: str, requester: str, tx_id: str,
        file_content: str | None = None,
        audit_trail: list | None = None,
    ) -> AgentState:
        initial_state: AgentState = {
            "task_id": task_id,
            "task_hash": task_hash,
            "task_text": task_text,
            "task_type": task_type,
            "file_content": file_content,
            "requester": requester,
            "tx_id": tx_id,
            "result": None,
            "merkle_root": None,
            "ipfs_cid": None,
            "verification_score": None,
            "similarity_score": None,
            "status": "started",
            "attempt": 0,
            "from_cache": False,
            "error": None,
            "audit_trail": audit_trail or [],
        }

        logger.info(f"[Orchestrator] Starting pipeline for task {task_id}")
        final_state = await self.graph.ainvoke(initial_state)
        logger.info(f"[Orchestrator] Pipeline complete for task {task_id}: {final_state['status']}")
        return final_state
