import pytest
from app.core import redis_client


@pytest.mark.asyncio
async def test_blacklist_roundtrip():
    """黑名单写入后应能查询命中，写入前不应命中。"""
    jti = "test-jti-roundtrip"
    assert await redis_client.is_blacklisted(jti) is False
    await redis_client.add_to_blacklist(jti, ttl_seconds=60)
    assert await redis_client.is_blacklisted(jti) is True
    # 清理
    client = redis_client.get_redis()
    await client.delete(redis_client._key(jti))
