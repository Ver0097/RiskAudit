from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core import security
from app.core.redis_client import add_to_blacklist
from app.db.session import get_db
from app.deps.auth import get_current_user, oauth2_scheme
from app.models.user import User
from app.schemas.auth import TokenResponse, UserOut
from app.services import user_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """用户名密码登录，成功后签发 JWT 访问令牌。"""
    user = await user_service.authenticate(db, form.username, form.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    settings = get_settings()
    token = security.create_access_token(subject=user.username)
    return TokenResponse(
        access_token=token,
        expires_in=settings.jwt_access_ttl_minutes * 60,
    )


@router.get("/me", response_model=UserOut)
async def me(current: User = Depends(get_current_user)) -> User:
    """返回当前已认证用户信息。"""
    return current


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(token: str = Depends(oauth2_scheme)) -> None:
    """登出：将令牌的 JTI 加入黑名单直至其原始过期时间。"""
    try:
        payload = security.decode_token(token)
    except security.InvalidTokenError:
        return
    jti = payload.get("jti")
    exp = payload.get("exp")
    if not jti or not exp:
        return
    now = int(datetime.now(timezone.utc).timestamp())
    ttl = max(int(exp) - now, 1)
    await add_to_blacklist(jti, ttl_seconds=ttl)
