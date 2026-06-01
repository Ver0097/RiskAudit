from redis.asyncio import Redis, from_url
from app.config import get_settings

# JWT 黑名单使用的 Redis Key 前缀，便于查找与清理
_BL_PREFIX = "jwt:blacklist:"
_redis: Redis | None = None


def get_redis() -> Redis:
    """惰性构造单例 Redis 客户端，连接信息从配置读取。"""
    global _redis
    if _redis is None:
        settings = get_settings()
        _redis = from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    return _redis


def _key(jti: str) -> str:
    """根据 jti 构造黑名单 Redis Key。"""
    return f"{_BL_PREFIX}{jti}"


async def add_to_blacklist(jti: str, ttl_seconds: int) -> None:
    """将指定 jti 写入黑名单，并按 ttl_seconds 自动过期。"""
    client = get_redis()
    await client.set(_key(jti), "1", ex=ttl_seconds)


async def is_blacklisted(jti: str) -> bool:
    """判断指定 jti 是否已被吊销。"""
    client = get_redis()
    return await client.exists(_key(jti)) == 1
