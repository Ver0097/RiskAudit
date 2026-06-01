from datetime import datetime
from pydantic import BaseModel


class TokenResponse(BaseModel):
    """登录成功后返回的访问令牌响应。"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # 秒


class UserOut(BaseModel):
    """对外暴露的用户信息（不含敏感字段）。"""

    id: int
    username: str
    display_name: str
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}
