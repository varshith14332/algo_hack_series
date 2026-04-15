"""
Tests for agent-to-agent communication system.
"""
import pytest
from services.agent_wallet_service import AgentWalletService
from algosdk import encoding


class TestAgentWallet:
    """Test deterministic wallet generation."""
    
    def test_agent_wallet_deterministic(self):
        """Call generate_agent_account("buyer") twice — assert both calls return identical address."""
        service = AgentWalletService()
        
        private_key1, address1 = service.generate_agent_account("buyer")
        private_key2, address2 = service.generate_agent_account("buyer")
        
        assert address1 == address2, "Addresses should be deterministic"
        assert private_key1 == private_key2, "Private keys should be deterministic"
        assert encoding.is_valid_address(address1), "Address should be valid Algorand address"
    
    def test_agent_wallet_different_names(self):
        """Generate accounts for "buyer" and "seller" — assert their addresses are different."""
        service = AgentWalletService()
        
        _, buyer_address = service.generate_agent_account("buyer")
        _, seller_address = service.generate_agent_account("seller")
        
        assert buyer_address != seller_address, "Different agent names should produce different addresses"
        assert encoding.is_valid_address(buyer_address), "Buyer address should be valid"
        assert encoding.is_valid_address(seller_address), "Seller address should be valid"


@pytest.mark.asyncio
class TestX402AgentMode:
    """Test x402 middleware agent-mode handling."""
    
    async def test_x402_agent_mode_missing_address(self, client):
        """POST to /api/tasks/run with X-Agent-Mode=true but no X-Agent-Address — assert 400."""
        response = await client.post(
            "/api/tasks/run",
            headers={
                "X-Agent-Mode": "true",
                "X-Task-Hash": "test-hash-123",
            },
            data={
                "task_type": "research",
                "prompt": "test prompt",
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "X-Agent-Address" in data["error"]
    
    async def test_x402_human_mode_unchanged(self, client):
        """POST to /api/tasks/run with no X-Agent-Mode and no X-Payment-Proof — assert 402."""
        response = await client.post(
            "/api/tasks/run",
            headers={
                "X-Task-Hash": "test-hash-456",
            },
            data={
                "task_type": "research",
                "prompt": "test prompt",
            }
        )
        
        assert response.status_code == 402
        data = response.json()
        assert data["success"] is False
        assert data["data"]["payment_required"] is True


@pytest.mark.asyncio
class TestAutonomousRun:
    """Test autonomous pipeline endpoints."""
    
    async def test_autonomous_run_invalid_address(self, client):
        """POST to /api/autonomous/run with invalid owner_address — assert 422."""
        response = await client.post(
            "/api/autonomous/run",
            json={
                "goal": "test goal here",
                "budget_algo": 1.0,
                "owner_address": "not-an-address",
            }
        )
        
        assert response.status_code == 422
    
    async def test_autonomous_run_goal_too_short(self, client):
        """POST to /api/autonomous/run with goal too short — assert 422."""
        # Use a valid Algorand address format (58 chars)
        valid_address = "A" * 58
        
        response = await client.post(
            "/api/autonomous/run",
            json={
                "goal": "hi",
                "budget_algo": 1.0,
                "owner_address": valid_address,
            }
        )
        
        assert response.status_code == 422
    
    async def test_autonomous_status_not_found(self, client):
        """GET /api/autonomous/status/nonexistent-task-id — assert 404."""
        response = await client.get("/api/autonomous/status/nonexistent-task-id")
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False


# Fixtures for testing
@pytest.fixture
async def client():
    """Create test client."""
    from httpx import AsyncClient
    from main import app
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
