"""
Master Agent — Autonomous multi-agent orchestrator with on-chain identity.

Decomposes user goals into subtasks, discovers services, executes via agent-to-agent
payments, and assembles final reports.
"""
import asyncio
import json
import uuid
import logging
import hashlib
from datetime import datetime, timezone
from services.agent_wallet_service import AgentWalletService
from agents.orchestrator import AgentOrchestrator
from openai import AsyncOpenAI
from config import settings

logger = logging.getLogger(__name__)


class MasterAgent:
    KNOWN_CATEGORIES = ["research", "data", "analysis", "writing"]
    BUDGET_WARNING_THRESHOLD = 0.90  # stop at 90% spent

    def __init__(self, user_wallet_address: str, budget_algo: float):
        self.user_wallet_address = user_wallet_address
        self.budget_algo = budget_algo
        self.budget_microalgo = int(budget_algo * 1_000_000)
        self.spent_microalgo = 0
        self.audit_trail = []
        self.wallet_service = AgentWalletService()
        self.contract_client = None  # Lazy load to avoid import issues
        self.orchestrator = AgentOrchestrator()
        self.openai = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL if settings.OPENAI_BASE_URL else None,
        )
        self.agent_address = None
        self.task_id = str(uuid.uuid4())
    
    def _get_contract_client(self):
        """Lazy load contract client to avoid circular imports."""
        if self.contract_client is None:
            import sys
            import os
            # Add parent directory to path to access contracts module
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            try:
                from contracts.deploy.contract_client import ContractClient
                self.contract_client = ContractClient()
            except ImportError:
                logger.warning("ContractClient not available - running in dev mode")
                # Create a mock client for dev mode
                class MockContractClient:
                    async def register_agent(self, *args, **kwargs):
                        logger.info("MockContractClient: register_agent called")
                        return "dev-tx-register"
                    async def discover_services(self, category):
                        logger.info(f"MockContractClient: discover_services({category})")
                        return []
                    async def get_agent_score(self, address):
                        return 750
                self.contract_client = MockContractClient()
        return self.contract_client

    async def initialize(self):
        """
        Register master agent on-chain and fund its wallet.
        Call this before run().
        
        Steps:
        1. Get agent address via wallet_service.get_address("master")
        2. Fund agent wallet
        3. Register on IdentityRegistry
        4. Append to audit_trail
        """
        # Get agent address
        self.agent_address = await self.wallet_service.get_address("master")
        logger.info(f"[MasterAgent] Address: {self.agent_address}")
        
        # Fund agent wallet
        try:
            tx_id = await self.wallet_service.fund_agent("master", self.budget_algo)
            logger.info(f"[MasterAgent] Funded with {self.budget_algo} ALGO, txID={tx_id}")
        except Exception as e:
            logger.warning(f"[MasterAgent] Funding failed: {e} (continuing anyway)")
        
        # Register on IdentityRegistry
        try:
            client = self._get_contract_client()
            await client.register_agent(
                agent_address=self.agent_address,
                owner_address=self.user_wallet_address,
                spending_limit=self.budget_microalgo,
                allowed_categories=",".join(self.KNOWN_CATEGORIES),
            )
            logger.info(f"[MasterAgent] Registered on IdentityRegistry")
        except Exception as e:
            logger.warning(f"[MasterAgent] Registration failed: {e} (continuing anyway)")
        
        # Audit trail
        self.audit_trail.append({
            "event": "master_agent_initialized",
            "agent_address": self.agent_address,
            "budget_algo": self.budget_algo,
            "owner": self.user_wallet_address,
            "timestamp": self._utc_now(),
        })

    async def run(self, goal: str) -> dict:
        """
        Main entry point. Runs entire pipeline autonomously.
        
        Returns final result dict with:
        - task_id
        - status
        - goal
        - final_output
        - subtasks_completed
        - subtasks_total
        - total_spent_algo
        - budget_remaining_algo
        - audit_trail
        - agent_address
        """
        logger.info(f"[MasterAgent] Starting pipeline for goal: {goal[:100]}...")
        
        # Parse goal into subtasks
        subtasks = await self._parse_goal(goal)
        results = []
        
        for i, subtask in enumerate(subtasks):
            # Check budget
            if self.spent_microalgo >= self.BUDGET_WARNING_THRESHOLD * self.budget_microalgo:
                logger.warning(f"[MasterAgent] Budget threshold reached ({self.BUDGET_WARNING_THRESHOLD*100}%)")
                self.audit_trail.append({
                    "event": "budget_threshold_reached",
                    "spent_microalgo": self.spent_microalgo,
                    "budget_microalgo": self.budget_microalgo,
                    "timestamp": self._utc_now(),
                })
                break
            
            logger.info(f"[MasterAgent] Processing subtask {i+1}/{len(subtasks)}: {subtask['name']}")
            
            # Discover service
            best_service = await self._discover_service(subtask["category"])
            if not best_service:
                logger.warning(f"[MasterAgent] No service found for category '{subtask['category']}'")
                continue
            
            # Execute subtask
            result = await self._execute_subtask(subtask, best_service)
            if result:
                results.append(result)
        
        # Assemble final report
        final_output = await self._assemble_report(goal, results)
        
        return {
            "task_id": self.task_id,
            "status": "completed",
            "goal": goal,
            "final_output": final_output,
            "subtasks_completed": len(results),
            "subtasks_total": len(subtasks),
            "total_spent_algo": self.spent_microalgo / 1_000_000,
            "budget_remaining_algo": (self.budget_microalgo - self.spent_microalgo) / 1_000_000,
            "audit_trail": self.audit_trail,
            "agent_address": self.agent_address,
        }

    async def _parse_goal(self, goal: str) -> list[dict]:
        """
        Use GPT-4o to parse goal into subtasks.
        
        Returns list of dicts with: name, category, description, estimated_complexity
        """
        system_prompt = (
            "You are a task decomposition engine. Break the user goal into 2-4 concrete subtasks. "
            f"Each subtask must have a category from: {', '.join(self.KNOWN_CATEGORIES)}. "
            "Return ONLY a valid JSON array. No markdown. No explanation. "
            "Each item: {\"name\": str, \"category\": str, \"description\": str, \"estimated_complexity\": str}"
        )
        
        try:
            response = await self.openai.chat.completions.create(
                model=settings.OPENAI_CHAT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": goal},
                ],
                temperature=0.3,
                max_tokens=1000,
            )
            
            content = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            subtasks = json.loads(content)
            
            self.audit_trail.append({
                "event": "goal_parsed",
                "subtasks": subtasks,
                "timestamp": self._utc_now(),
            })
            
            logger.info(f"[MasterAgent] Parsed {len(subtasks)} subtasks")
            return subtasks
            
        except Exception as e:
            logger.error(f"[MasterAgent] Goal parsing failed: {e}")
            # Fallback: single subtask
            return [{
                "name": "complete_task",
                "category": "research",
                "description": goal,
                "estimated_complexity": "medium",
            }]

    async def _discover_service(self, category: str) -> dict | None:
        """
        Find best available service for a category.
        
        Returns service dict or None if no qualified service found.
        """
        try:
            client = self._get_contract_client()
            services = await client.discover_services(category)
            
            if not services:
                logger.warning(f"[MasterAgent] No services found for category '{category}'")
                return None
            
            # Get reputation scores
            qualified = []
            client = self._get_contract_client()
            for service in services:
                try:
                    score = await client.get_agent_score(service["agent_address"])
                    if score >= settings.MIN_AGENT_REPUTATION:
                        service["reputation_score"] = score
                        qualified.append(service)
                except Exception:
                    pass
            
            if not qualified:
                logger.warning(f"[MasterAgent] No qualified services for category '{category}'")
                return None
            
            # Sort by price ascending, pick cheapest
            qualified.sort(key=lambda s: s.get("price_microalgo", 999999))
            selected = qualified[0]
            
            self.audit_trail.append({
                "event": "service_discovered",
                "category": category,
                "selected_agent": selected["agent_address"],
                "price_algo": selected["price_microalgo"] / 1_000_000,
                "reputation_score": selected.get("reputation_score", 0),
                "candidates_found": len(services),
                "candidates_qualified": len(qualified),
                "timestamp": self._utc_now(),
            })
            
            return selected
            
        except Exception as e:
            logger.error(f"[MasterAgent] Service discovery failed: {e}")
            return None

    async def _execute_subtask(self, subtask: dict, service: dict) -> str | None:
        """
        Execute a single subtask using a discovered service.
        
        Makes HTTP request to backend task endpoint AS AN AGENT.
        Returns result string or None on failure.
        """
        task_hash = hashlib.sha256(subtask["description"].encode()).hexdigest()
        
        # Check semantic cache first
        try:
            from services.cache_service import CacheService
            cache = CacheService()
            cached = await cache.check_semantic(subtask["description"])
            if cached:
                cached_result = await cache.get(cached["task_hash"])
                if cached_result:
                    cost_microalgo = int(settings.CACHED_TASK_PRICE_ALGO * 1_000_000)
                    self.spent_microalgo += cost_microalgo
                    
                    self.audit_trail.append({
                        "event": "cache_hit",
                        "subtask": subtask["name"],
                        "cost_algo": settings.CACHED_TASK_PRICE_ALGO,
                        "similarity_score": cached["score"],
                        "timestamp": self._utc_now(),
                    })
                    
                    logger.info(f"[MasterAgent] Cache hit for subtask '{subtask['name']}'")
                    return cached_result["result"]
        except Exception as e:
            logger.warning(f"[MasterAgent] Cache check failed: {e}")
        
        # Make HTTP request as agent
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.BACKEND_URL}/api/tasks/run",
                    headers={
                        "X-Agent-Mode": "true",
                        "X-Agent-Address": self.agent_address,
                        "X-Task-Hash": task_hash,
                        "X-Category": subtask["category"],
                    },
                    data={
                        "task_type": subtask["category"],
                        "prompt": subtask["description"],
                    },
                    timeout=60.0,
                )
                
                if response.status_code == 403:
                    self.audit_trail.append({
                        "event": "authorization_failed",
                        "subtask": subtask["name"],
                        "reason": "Agent verification failed",
                        "timestamp": self._utc_now(),
                    })
                    logger.error(f"[MasterAgent] Authorization failed for subtask '{subtask['name']}'")
                    return None
                
                if response.status_code == 200:
                    data = response.json()["data"]
                    cost_microalgo = int(settings.NEW_TASK_PRICE_ALGO * 1_000_000)
                    self.spent_microalgo += cost_microalgo
                    
                    self.audit_trail.append({
                        "event": "subtask_completed",
                        "subtask": subtask["name"],
                        "agent_used": service["agent_address"],
                        "cost_algo": settings.NEW_TASK_PRICE_ALGO,
                        "from_cache": data.get("from_cache", False),
                        "merkle_root": data.get("merkle_root"),
                        "verification_score": data.get("verification_score"),
                        "timestamp": self._utc_now(),
                    })
                    
                    logger.info(f"[MasterAgent] Subtask '{subtask['name']}' completed")
                    return data.get("result")
                
                logger.error(f"[MasterAgent] Subtask request failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"[MasterAgent] Subtask execution failed: {e}")
            self.audit_trail.append({
                "event": "subtask_error",
                "subtask": subtask["name"],
                "error": str(e),
                "timestamp": self._utc_now(),
            })
            return None

    async def _assemble_report(self, goal: str, results: list[str]) -> str:
        """
        Use GPT-4o to assemble subtask results into a final coherent report.
        
        Returns assembled report string.
        """
        if not results:
            return "No results were produced. The agent pipeline encountered errors or budget constraints."
        
        prompt = (
            f"You are a report writer. The user's original goal was: {goal}\n\n"
            f"Here are the research findings from multiple specialist agents:\n"
            + "\n".join(f"Finding {i+1}: {r}" for i, r in enumerate(results))
            + "\n\nWrite a clear, structured, professional report that synthesizes all findings. "
            "Include: executive summary, key findings per topic, risks identified, and recommendations."
        )
        
        try:
            response = await self.openai.chat.completions.create(
                model=settings.OPENAI_CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional report writer."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=2048,
            )
            
            report = response.choices[0].message.content.strip()
            logger.info(f"[MasterAgent] Report assembled ({len(report)} chars)")
            return report
            
        except Exception as e:
            logger.error(f"[MasterAgent] Report assembly failed: {e}")
            # Fallback: simple concatenation
            return "\n\n".join(f"## Finding {i+1}\n{r}" for i, r in enumerate(results))

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat()
