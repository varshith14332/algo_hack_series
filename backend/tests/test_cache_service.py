import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch


class TestCacheService:
    @pytest.mark.asyncio
    async def test_check_exact_hit(self):
        """check_exact returns True when Redis key exists."""
        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=1)

        with patch("services.cache_service.get_redis", return_value=mock_redis):
            with patch("services.cache_service.Pinecone"):
                from services.cache_service import CacheService
                svc = CacheService()
                result = await svc.check_exact("known_hash")
                assert result is True

    @pytest.mark.asyncio
    async def test_check_exact_miss(self):
        """check_exact returns False when Redis key does not exist."""
        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=0)

        with patch("services.cache_service.get_redis", return_value=mock_redis):
            with patch("services.cache_service.Pinecone"):
                from services.cache_service import CacheService
                svc = CacheService()
                result = await svc.check_exact("unknown_hash")
                assert result is False

    @pytest.mark.asyncio
    async def test_get_returns_cached_data(self):
        data = {"result": "test result", "merkle_root": "abc", "ipfs_cid": "cid", "requester": "addr", "task_hash": "hash"}
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=json.dumps(data))

        with patch("services.cache_service.get_redis", return_value=mock_redis):
            with patch("services.cache_service.Pinecone"):
                from services.cache_service import CacheService
                svc = CacheService()
                result = await svc.get("some_hash")
                assert result is not None
                assert result["result"] == "test result"

    @pytest.mark.asyncio
    async def test_get_returns_none_on_miss(self):
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)

        with patch("services.cache_service.get_redis", return_value=mock_redis):
            with patch("services.cache_service.Pinecone"):
                from services.cache_service import CacheService
                svc = CacheService()
                result = await svc.get("missing_hash")
                assert result is None
