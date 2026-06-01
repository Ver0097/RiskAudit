from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.redis_client import is_blacklisted
from app.db.session import get_db
from app.models.user import User
from app.services import user_service

# OAuth2 Bearer 方案，tokenUrl 指向登录接口
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# 通用 401 异常，供下文复用
CREDENTIALS_EXC = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="无效或过期的凭证",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """解析 JWT、校验黑名单与用户激活态后返回当前用户。"""
    try:
        payload = security.decode_token(token)
    except security.InvalidTokenError:
        raise CREDENTIALS_EXC

    jti = payload.get("jti")
    sub = payload.get("sub")
    if not jti or not sub:
        raise CREDENTIALS_EXC

    # JTI 在登出黑名单中视为失效
    if await is_blacklisted(jti):
        raise CREDENTIALS_EXC

    user = await user_service.get_by_username(db, sub)
    if user is None or not user.is_active:
        raise CREDENTIALS_EXC

    return user
