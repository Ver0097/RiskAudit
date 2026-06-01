import uuid
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError as _JWTInvalidTokenError
from app.config import get_settings

# 对外暴露统一的非法 token 异常类型，便于上层捕获
InvalidTokenError = _JWTInvalidTokenError


def hash_password(plain: str) -> str:
    """使用 bcrypt 对明文密码进行加盐哈希。"""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """校验明文密码与存储哈希是否匹配；任何异常视为校验失败。"""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str, ttl_minutes: int | None = None) -> str:
    """签发包含 sub/type/iat/exp/jti 的 access token。"""
    settings = get_settings()
    ttl = ttl_minutes if ttl_minutes is not None else settings.jwt_access_ttl_minutes
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ttl)).timestamp()),
        "jti": uuid.uuid4().hex,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    """解析并校验 token，签名失败或过期均抛 InvalidTokenError。"""
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
