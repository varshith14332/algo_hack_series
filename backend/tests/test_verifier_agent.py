import pytest
from agents.verifier_agent import VerifierAgent


class TestVerifierAgent:
    def setup_method(self):
        self.agent = VerifierAgent()

    def test_chunk_result_single_chunk(self):
        text = "short text"
        chunks = self.agent._chunk_result(text)
        assert len(chunks) >= 1
        assert chunks[0] == text

    def test_chunk_result_long_text(self):
        # 1500 words
        text = " ".join(["word"] * 1500)
        chunks = self.agent._chunk_result(text, chunk_size=500)
        assert len(chunks) == 3

    def test_chunk_result_empty_returns_single(self):
        chunks = self.agent._chunk_result("")
        assert len(chunks) == 1

    def test_chunk_result_exact_boundary(self):
        text = " ".join(["word"] * 1000)
        chunks = self.agent._chunk_result(text, chunk_size=500)
        assert len(chunks) == 2

    @pytest.mark.asyncio
    async def test_run_skips_cache_hit(self):
        """Verifier must skip state that's already a cache hit."""
        state = {
            "status": "cache_hit",
            "task_text": "test",
            "result": "result",
            "task_hash": "hash",
            "requester": "addr",
            "task_id": "id",
        }
        result = await self.agent.run(state)
        assert result["status"] == "cache_hit"

    @pytest.mark.asyncio
    async def test_run_no_result_fails(self):
        """Verifier must fail gracefully when no result is present."""
        state = {
            "status": "executed",
            "task_text": "test",
            "result": None,
            "task_hash": "hash",
            "requester": "addr",
            "task_id": "id",
        }
        result = await self.agent.run(state)
        assert result["status"] == "failed"
        assert result["error"] == "No result to verify"
