import hashlib
from typing import List
import logging

logger = logging.getLogger(__name__)


class MerkleService:
    def _hash(self, data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()

    def build_tree(self, chunks: List[str]) -> dict:
        if not chunks:
            raise ValueError("Cannot build Merkle tree from empty list")

        if len(chunks) % 2 != 0:
            chunks = chunks + [chunks[-1]]

        leaves = [self._hash(c) for c in chunks]
        tree = [leaves]

        current = leaves[:]
        while len(current) > 1:
            if len(current) % 2 != 0:
                current.append(current[-1])
            next_level = []
            for i in range(0, len(current), 2):
                combined = self._hash(current[i] + current[i + 1])
                next_level.append(combined)
            tree.append(next_level)
            current = next_level

        root = current[0]
        return {"root": root, "tree": tree, "leaves": leaves}

    def generate_proof(self, tree_data: dict, leaf_index: int) -> List[dict]:
        tree = tree_data["tree"]
        proof = []
        idx = leaf_index

        for level in tree[:-1]:
            if idx % 2 == 0:
                sibling_idx = idx + 1
                position = "right"
            else:
                sibling_idx = idx - 1
                position = "left"

            if sibling_idx < len(level):
                proof.append({"hash": level[sibling_idx], "position": position})

            idx //= 2

        return proof

    def verify_proof(self, leaf_data: str, proof: List[dict], root: str) -> bool:
        current = self._hash(leaf_data)

        for step in proof:
            sibling = step["hash"]
            if step["position"] == "right":
                current = self._hash(current + sibling)
            else:
                current = self._hash(sibling + current)

        return current == root

    async def commit_to_chain(
        self, task_hash: str, merkle_root: str,
        original_requester: str, price_microalgo: int
    ) -> str:
        try:
            import sys, os
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            from contracts.deploy.contract_client import ContractClient
            client = ContractClient()
            tx_id = await client.register_result(
                task_hash=task_hash,
                merkle_root=merkle_root,
                original_requester=original_requester,
                price=price_microalgo,
            )
            logger.info(f"Merkle root committed on-chain: {merkle_root[:16]}... txID: {tx_id}")
            return tx_id
        except Exception as e:
            logger.warning(f"On-chain commit skipped (dev mode or contracts not deployed): {e}")
            return f"dev-tx-{task_hash[:16]}"
