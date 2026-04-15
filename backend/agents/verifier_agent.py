from openai import AsyncOpenAI
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from services.merkle_service import MerkleService
from services.ipfs_service import IPFSService
from services.cache_service import CacheService
from config import settings
import logging

logger = logging.getLogger(__name__)


class VerifierAgent:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
        self.merkle = MerkleService()
        self.ipfs = IPFSService()
        self.cache = CacheService()
        self.threshold = 0.85

    async def run(self, state: dict) -> dict:
        # Skip if already resolved from cache or failed
        if state.get("status") in ("cache_hit", "failed"):
            return state

        task_text = state["task_text"]
        result = state.get("result")
        task_hash = state["task_hash"]
        requester = state["requester"]
        task_id = state["task_id"]

        if not result:
            state["status"] = "failed"
            state["error"] = "No result to verify"
            return state

        try:
            from routers.agents import broadcast_activity
            await broadcast_activity(
                event="verifying",
                agent="verifier",
                details={"task_id": task_id},
            )
        except Exception:
            pass

        audit_trail: list = state.get("audit_trail", [])

        try:
            score = await self._compute_similarity(task_text, result)
            state["verification_score"] = score
            logger.info(f"[VerifierAgent] Score: {score:.3f} (threshold: {self.threshold})")

            if score >= self.threshold:
                chunks = self._chunk_result(result)
                tree_data = self.merkle.build_tree(chunks)
                merkle_root = tree_data["root"]

                ipfs_cid = await self.ipfs.store({
                    "result": result,
                    "task_hash": task_hash,
                    "merkle_root": merkle_root,
                    "tree": tree_data["tree"],
                })

                price_microalgo = int(settings.NEW_TASK_PRICE_ALGO * 1_000_000)
                chain_tx_id = await self.merkle.commit_to_chain(
                    task_hash=task_hash,
                    merkle_root=merkle_root,
                    original_requester=requester,
                    price_microalgo=price_microalgo,
                )

                await self.cache.store(
                    task_hash=task_hash,
                    task_text=task_text,
                    result=result,
                    merkle_root=merkle_root,
                    ipfs_cid=ipfs_cid,
                    requester=requester,
                )

                audit_trail.append({
                    "agent": "verifier",
                    "action": "verified",
                    "detail": f"Similarity score={score:.3f} ≥ {self.threshold} — Merkle root committed on-chain",
                    "payment_algo": None,
                    "tx_id": chain_tx_id,
                })

                state["merkle_root"] = merkle_root
                state["ipfs_cid"] = ipfs_cid
                state["status"] = "verified"

                logger.info(f"[VerifierAgent] Task {task_id} verified and committed")

            else:
                audit_trail.append({
                    "agent": "verifier",
                    "action": "rejected",
                    "detail": f"Similarity score={score:.3f} < {self.threshold} — result rejected",
                    "payment_algo": None,
                    "tx_id": None,
                })
                state["status"] = "rejected"
                state["error"] = f"Quality below threshold: {score:.3f}"
                logger.warning(f"[VerifierAgent] Task {task_id} rejected: score={score:.3f}")

        except Exception as e:
            logger.error(f"[VerifierAgent] Error: {e}")
            state["status"] = "error"
            state["error"] = str(e)

        state["audit_trail"] = audit_trail
        return state

    async def _compute_similarity(self, task: str, result: str) -> float:
        response = await self.client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=[task[:8000], result[:8000]],
        )
        task_vec = np.array(response.data[0].embedding).reshape(1, -1)
        result_vec = np.array(response.data[1].embedding).reshape(1, -1)
        return float(cosine_similarity(task_vec, result_vec)[0][0])

    def _chunk_result(self, result: str, chunk_size: int = 500) -> list:
        words = result.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunks.append(" ".join(words[i:i + chunk_size]))
        return chunks if chunks else [result]
