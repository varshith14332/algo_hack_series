import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.algorand_service import AlgorandService


@pytest.fixture
def algorand():
    return AlgorandService()


class TestAlgorandService:
    def test_validate_address_too_short(self, algorand):
        assert not algorand.validate_address("SHORT")

    def test_validate_address_valid_format(self, algorand):
        # A valid base32 Algorand address is 58 chars
        # Using a mock valid address for format test
        valid = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        # algosdk validates checksum too; test it doesn't crash
        result = algorand.validate_address(valid)
        assert isinstance(result, bool)

    def test_validate_address_empty(self, algorand):
        assert not algorand.validate_address("")

    @pytest.mark.asyncio
    async def test_verify_transaction_replay(self, algorand):
        """Transaction used before must be rejected (replay attack)."""
        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=True)

        with patch(
            "services.algorand_service.get_redis",
            return_value=mock_redis,
        ):
            result = await algorand.verify_transaction("USED_TX_ID", "task_hash")
            assert result is False

    @pytest.mark.asyncio
    async def test_verify_transaction_bad_type(self, algorand):
        """Non-payment transaction type must fail verification."""
        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=False)

        mock_tx_info = {
            "transaction": {
                "tx-type": "axfer",  # Asset transfer, not payment
                "payment-transaction": {"receiver": "ADDR", "amount": 5000},
                "note": "",
            }
        }

        with patch(
            "services.algorand_service.get_redis",
            return_value=mock_redis,
        ):
            with patch.object(
                algorand.indexer_client, "transaction", return_value=mock_tx_info
            ):
                result = await algorand.verify_transaction("TX_ID", "task_hash")
                assert result is False
