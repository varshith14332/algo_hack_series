"""
MasterAgent — top-level autonomous agent.

After the user sets a goal and funds the master wallet, this agent runs
everything with zero human interaction. It parses the goal into subtasks,
discovers services, executes via the existing LangGraph sub-pipeline,
assembles a final report, and returns a complete audit trail.
"""
from openai import AsyncOpenAI
from services.agent_wallet_service import AgentWalletService
from agents.orchestrator import AgentOrchestrator
from config import settings
from datetime import datetime, timezone
import hashlib
import uuid
import json
import logging

logger = logging.getLogger(__name__)

agent_wallet_service = AgentWalletService()

VALID_CATEGORIES = {"research", "data", "analysis", "writing"}

WRITER_SYSTEM_PROMPT = """You are a professional report writer.
Given multiple research findings, produce a single coherent, well-structured report.
Include: Executive Summary, Key Findings per section, Risk Assessment (if applicable), Conclusion.
Use markdown formatting."""


class MasterAgent:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.orchestrator = AgentOrchestrator()
        # Master agent's own Algorand wallet
        self._private_key, self.address = agent_wallet_service.generate_agent_account("master")
        logger.info(f"[MasterAgent] Wallet: {self.address[:16]}...")

    async def _register_identity(self, owner_address: str, spending_limit_microalgo: int, allowed_categories: str) -> str:
        """Register master agent in IdentityRegistry on first run."""
        try:
            from contracts.deploy.contract_client import ContractClient
            client = ContractClient()
            tx_id = await client.register_agent(
                agent_address=self.address,
                owner_address=owner_address,
                spending_limit=spending_limit_microalgo,
                allowed_categories=allowed_categories,
            )
            logger.info(f"[MasterAgent] Registered on-chain: {tx_id}")
            return tx_id
        except Exception as e:
            logger.warning(f"[MasterAgent] Identity registration failed (dev mode ok): {e}")
            return f"dev-master-{self.address[:16]}"

    async def _parse_goal(self, goal: str) -> list[dict]:
        """Use GPT-4o to break a goal into typed subtasks."""
        try:
            resp = await self.client.chat.completions.create(
                model=settings.OPENAI_CHAT_MODEL,
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Break the user's goal into subtasks. "
                            "Each subtask needs: name (string), category (one of: research, data, analysis, writing), "
                            "description (string, 1-2 sentences). "
                            "Return JSON: {\"subtasks\": [{\"name\": ..., \"category\": ..., \"description\": ...}]}"
                        ),
                    },
                    {"role": "user", "content": goal},
                ],
            )
            data = json.loads(resp.choices[0].message.content)
            subtasks = data.get("subtasks", [])
            # Validate categories
            for st in subtasks:
                if st.get("category") not in VALID_CATEGORIES:
                    st["category"] = "analysis"
            return subtasks
        except Exception as e:
            logger.error(f"[MasterAgent] Goal parsing failed: {e}")
            # Fallback: single analysis subtask
            return [{"name": "Main Task", "category": "analysis", "description": goal}]

    async def _discover_service(self, category: str, audit_trail: list) -> dict | None:
        """Find the cheapest service with reputation >= MIN_AGENT_REPUTATION."""
        try:
            from contracts.deploy.contract_client import ContractClient
            client = ContractClient()
            services = await client.discover_services(category)
            min_rep = settings.MIN_AGENT_REPUTATION
            qualified = [s for s in services if s.get("reputation_score", 0) >= min_rep]
            if qualified:
                chosen = min(qualified, key=lambda s: s.get("price_microalgo", 999_999_999))
                audit_trail.append({
                    "agent": "master",
                    "action": "service_selected",
                    "detail": (
                        f"Discovered {len(services)} services for '{category}', "
                        f"selected '{chosen.get('service_name')}' "
                        f"(reputation={chosen.get('reputation_score', 0)}, "
                        f"price={chosen.get('price_microalgo', 0) / 1_000_000} ALGO)"
                    ),
                    "payment_algo": None,
                    "tx_id": None,
                    "timestamp": _now(),
                })
                return chosen
        except Exception as e:
            logger.warning(f"[MasterAgent] Service discovery failed for {category}: {e}")

        audit_trail.append({
            "agent": "master",
            "action": "no_service_found",
            "detail": f"No qualified external service for '{category}' — using local pipeline",
            "payment_algo": None,
            "tx_id": None,
            "timestamp": _now(),
        })
        return None

    async def _execute_subtask(
        self,
        subtask: dict,
        audit_trail: list,
        owner_address: str,
        total_spent_microalgo: int,
        budget_microalgo: int,
    ) -> tuple[dict, int]:
        """Run a single subtask through the agent pipeline. Returns (result_state, new_spent)."""
        name = subtask["name"]
        category = subtask["category"]
        description = subtask["description"]

        task_id = str(uuid.uuid4())
        task_hash = hashlib.sha256(f"{name}:{description}".encode()).hexdigest()

        audit_trail.append({
            "agent": "master",
            "action": "subtask_start",
            "detail": f"Starting subtask '{name}' (category={category})",
            "payment_algo": None,
            "tx_id": None,
            "timestamp": _now(),
        })

        # Budget guard: stop if >90% spent
        if total_spent_microalgo >= int(budget_microalgo * 0.9):
            audit_trail.append({
                "agent": "master",
                "action": "budget_guard",
                "detail": f"Skipping '{name}': 90% budget threshold reached",
                "payment_algo": None,
                "tx_id": None,
                "timestamp": _now(),
            })
            return {"status": "skipped", "result": None, "task_id": task_id}, total_spent_microalgo

        final_state = await self.orchestrator.run(
            task_id=task_id,
            task_hash=task_hash,
            task_text=description,
            task_type=category if category in ("summarize", "extract", "analyze") else "analyze",
            requester=owner_address,
            tx_id=f"master:{self.address[:16]}",
            audit_trail=list(audit_trail),
        )

        # Accumulate audit events from sub-pipeline
        for entry in final_state.get("audit_trail", []):
            if entry not in audit_trail:
                entry["timestamp"] = entry.get("timestamp", _now())
                audit_trail.append(entry)

        subtask_cost = int(settings.NEW_TASK_PRICE_ALGO * 1_000_000)
        if final_state.get("from_cache"):
            subtask_cost = int(settings.CACHED_TASK_PRICE_ALGO * 1_000_000)

        total_spent_microalgo += subtask_cost

        audit_trail.append({
            "agent": "master",
            "action": "subtask_complete",
            "detail": (
                f"Subtask '{name}' complete — status={final_state.get('status')}, "
                f"cost={subtask_cost/1_000_000} ALGO"
            ),
            "payment_algo": subtask_cost / 1_000_000,
            "tx_id": final_state.get("merkle_root", "")[:16] or None,
            "timestamp": _now(),
        })

        return final_state, total_spent_microalgo

    async def _write_final_report(self, goal: str, subtask_results: list[dict]) -> str:
        """Use WriterAgent (GPT-4o) to assemble subtask results into a final report."""
        findings = "\n\n".join(
            f"### {r.get('name', f'Subtask {i+1}')}\n{r.get('result', 'No result')}"
            for i, r in enumerate(subtask_results)
            if r.get("result")
        )

        if not findings:
            return "No results were produced. Please check agent logs."

        try:
            resp = await self.client.chat.completions.create(
                model=settings.OPENAI_CHAT_MODEL,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": WRITER_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Goal: {goal}\n\nFindings:\n{findings}",
                    },
                ],
            )
            return resp.choices[0].message.content
        except Exception as e:
            logger.error(f"[MasterAgent] WriterAgent failed: {e}")
            return findings

    async def run(
        self,
        goal: str,
        budget_algo: float,
        owner_address: str,
        task_id: str,
    ) -> dict:
        """
        Entry point. Runs the full autonomous pipeline.
        Returns complete result with audit trail.
        """
        audit_trail: list = []
        budget_microalgo = int(budget_algo * 1_000_000)
        total_spent_microalgo = 0

        # ── Step 1: Register identity on-chain ───────────────────
        reg_tx = await self._register_identity(
            owner_address=owner_address,
            spending_limit_microalgo=budget_microalgo,
            allowed_categories=",".join(VALID_CATEGORIES),
        )
        audit_trail.append({
            "agent": "master",
            "action": "identity_registered",
            "detail": f"Master agent registered on-chain with {budget_algo} ALGO budget",
            "payment_algo": None,
            "tx_id": reg_tx,
            "timestamp": _now(),
        })

        # Persist initial status for polling
        await _save_status(task_id, {
            "status": "running",
            "current_step": "Parsing goal into subtasks",
            "progress_percent": 5,
            "audit_trail": audit_trail,
        })

        # ── Step 2: Parse goal into subtasks ─────────────────────
        subtasks = await self._parse_goal(goal)
        audit_trail.append({
            "agent": "master",
            "action": "goal_parsed",
            "detail": f"Goal broken into {len(subtasks)} subtask(s): {', '.join(s['name'] for s in subtasks)}",
            "payment_algo": None,
            "tx_id": None,
            "timestamp": _now(),
        })

        await _save_status(task_id, {
            "status": "running",
            "current_step": f"Executing {len(subtasks)} subtasks",
            "progress_percent": 15,
            "audit_trail": audit_trail,
        })

        # ── Step 3: Execute subtasks sequentially ────────────────
        subtask_results = []
        merkle_roots = []

        for i, subtask in enumerate(subtasks):
            progress = 15 + int(60 * (i / max(len(subtasks), 1)))
            await _save_status(task_id, {
                "status": "running",
                "current_step": f"Executing subtask {i+1}/{len(subtasks)}: {subtask['name']}",
                "progress_percent": progress,
                "audit_trail": audit_trail,
            })

            # Discover service for this subtask category
            await self._discover_service(subtask["category"], audit_trail)

            final_state, total_spent_microalgo = await self._execute_subtask(
                subtask=subtask,
                audit_trail=audit_trail,
                owner_address=owner_address,
                total_spent_microalgo=total_spent_microalgo,
                budget_microalgo=budget_microalgo,
            )

            subtask_results.append({
                "name": subtask["name"],
                "category": subtask["category"],
                "result": final_state.get("result"),
                "status": final_state.get("status"),
                "merkle_root": final_state.get("merkle_root"),
                "ipfs_cid": final_state.get("ipfs_cid"),
            })

            if final_state.get("merkle_root"):
                merkle_roots.append(final_state["merkle_root"])

        # ── Step 4: Assemble final report ────────────────────────
        await _save_status(task_id, {
            "status": "running",
            "current_step": "WriterAgent producing final report",
            "progress_percent": 85,
            "audit_trail": audit_trail,
        })

        audit_trail.append({
            "agent": "master",
            "action": "writing_report",
            "detail": "WriterAgent producing final structured report from all subtask results",
            "payment_algo": None,
            "tx_id": None,
            "timestamp": _now(),
        })

        final_output = await self._write_final_report(goal, subtask_results)

        total_spent_algo = total_spent_microalgo / 1_000_000
        audit_trail.append({
            "agent": "master",
            "action": "pipeline_complete",
            "detail": (
                f"Pipeline complete — {len(subtasks)} subtasks, "
                f"spent {total_spent_algo:.4f} ALGO of {budget_algo} ALGO budget"
            ),
            "payment_algo": total_spent_algo,
            "tx_id": None,
            "timestamp": _now(),
        })

        result = {
            "status": "complete",
            "final_output": final_output,
            "total_spent_algo": total_spent_algo,
            "subtasks_completed": len([r for r in subtask_results if r.get("result")]),
            "audit_trail": audit_trail,
            "merkle_roots": merkle_roots,
            "master_agent_address": self.address,
        }

        await _save_status(task_id, {
            "status": "complete",
            "current_step": "Done",
            "progress_percent": 100,
            "audit_trail": audit_trail,
            "result": result,
        })

        return result


async def _save_status(task_id: str, data: dict):
    """Persist task status in Redis for polling."""
    try:
        from db.redis_client import get_redis
        redis = await get_redis()
        await redis.setex(
            f"autonomous:{task_id}",
            3600 * 24,
            json.dumps(data, default=str),
        )
    except Exception as e:
        logger.error(f"_save_status failed: {e}")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
