# 灵工企业风控 Agent 系统 · 第一步实施计划：登录与对话外壳

> **致执行代理：** 必需子技能：使用 `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans` 按任务逐项实现本计划。所有步骤使用复选框（`- [ ]`）语法追踪。

**目标：** 从零搭建灵工企业风控 Agent 系统的项目骨架，完成「登录页 + 登录后对话页」最小闭环，对话接入真实 DeepSeek 模型并通过 SSE 流式输出。

**架构：** 单仓双目录（`backend/` + `frontend/`），后端 FastAPI 暴露 REST + SSE 接口；JWT 鉴权配合 Redis 黑名单实现安全登出；前端 Vue 3 + Naive UI + Pinia + Vue Router 构建 SPA；登录后通过 Pinia 持久化 token，对话页使用 fetch + ReadableStream 消费 SSE 流。本步骤仅集成 LangChain 的 `ChatDeepSeek` 单轮调用，**不引入 LangGraph、记忆、工具**——为后续步骤预留集成点。

**技术栈：**
- 后端：Python 3.12.13、FastAPI、SQLAlchemy 2.x（异步）、PostgreSQL 17、Redis、Alembic、LangChain + langchain-deepseek、sse-starlette、PyJWT、bcrypt、pydantic-settings、pytest + pytest-asyncio + httpx
- 前端：Vite、Vue 3、TypeScript、Naive UI、Vue Router 4、Pinia 2、Axios、Vitest

---

## 目录结构总览

```
RiskAudit2/
├── README.md                        # 项目总览 + 启动指南
├── .gitignore                       # 通用忽略：venv / node_modules / .env / __pycache__
├── docs/superpowers/plans/          # 本计划存放位置
├── backend/
│   ├── requirements.txt             # pip 依赖清单
│   ├── .env.example                 # 环境变量模板
│   ├── alembic.ini                  # Alembic 配置
│   ├── alembic/
│   │   ├── env.py                   # 异步迁移环境
│   │   ├── script.py.mako
│   │   └── versions/
│   │       ├── 0001_create_users_table.py
│   │       └── 0002_seed_admin_user.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI 实例、CORS、路由挂载
│   │   ├── config.py                # Settings（Pydantic Settings）
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # DeclarativeBase
│   │   │   └── session.py           # async_engine + AsyncSession 工厂 + 依赖
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── security.py          # bcrypt 哈希 + JWT 编解码
│   │   │   └── redis_client.py      # Redis 客户端 + JWT 黑名单
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── user.py              # User ORM 模型
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # LoginRequest / TokenResponse / UserOut
│   │   │   └── chat.py              # ChatRequest
│   │   ├── deps/
│   │   │   ├── __init__.py
│   │   │   └── auth.py              # get_current_user 依赖
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── user_service.py      # 用户校验
│   │   │   └── llm_service.py       # DeepSeek 流式封装
│   │   └── api/
│   │       ├── __init__.py
│   │       ├── auth.py              # /api/auth/login | logout | me
│   │       └── chat.py              # /api/chat/stream (SSE)
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py              # pytest 夹具：测试 DB、httpx 客户端
│       ├── test_security.py
│       ├── test_auth_api.py
│       └── test_chat_api.py
└── frontend/
    ├── package.json
    ├── tsconfig.json
    ├── tsconfig.node.json
    ├── vite.config.ts               # 含 /api 反向代理至后端
    ├── index.html
    ├── env.d.ts
    ├── .env.example
    └── src/
        ├── main.ts                  # 注册 Pinia / Router / Naive UI
        ├── App.vue                  # <RouterView /> 外壳
        ├── router/
        │   └── index.ts             # 路由表 + 守卫
        ├── stores/
        │   └── auth.ts              # 用户 / token / 持久化
        ├── api/
        │   ├── http.ts              # axios 实例 + 401 拦截
        │   ├── auth.ts              # login / logout / me
        │   └── chat.ts              # SSE fetch 工具
        ├── views/
        │   ├── LoginView.vue
        │   └── ChatView.vue
        └── components/
            ├── ChatMessage.vue
            └── ChatInput.vue
```

每个文件单一职责。后端按「数据库 / 配置 / 安全 / 模型 / Schema / 依赖 / 服务 / API」分层；前端按「视图 / 组件 / 状态 / API」分层。后续步骤新增功能时沿此结构扩展，例如对话记忆放入 `services/`，LangGraph 工作流放入 `app/graphs/`。

---

## Phase A · 项目骨架与基础设施

### Task 1: 单仓根骨架与共享文件

**Files:**
- Create: `RiskAudit2/.gitignore`
- Create: `RiskAudit2/README.md`
- Create: `RiskAudit2/backend/.gitkeep`
- Create: `RiskAudit2/frontend/.gitkeep`

- [ ] **Step 1: 写 `.gitignore`**

```gitignore
# Python
__pycache__/
*.py[cod]
.venv/
venv/
.env
*.egg-info/
.pytest_cache/
.coverage

# Node
node_modules/
dist/
.vite/
*.log

# IDE
.vscode/
.idea/
.DS_Store

# 项目专属
backend/alembic/versions/__pycache__/
```

- [ ] **Step 2: 写最小 README（启动说明后续补全）**

```markdown
# 灵工企业风控 Agent 系统

单仓 monorepo：
- `backend/` — FastAPI + LangChain 服务
- `frontend/` — Vue 3 + Naive UI SPA
- `docs/` — 文档与计划

启动方式见 `docs/`。
```

- [ ] **Step 3: 创建 backend / frontend 占位目录**

```bash
mkdir -p backend frontend
touch backend/.gitkeep frontend/.gitkeep
```

- [ ] **Step 4: 提交**

```bash
git init
git add .gitignore README.md backend/.gitkeep frontend/.gitkeep
git commit -m "chore: 初始化单仓骨架"
```

---

### Task 2: 后端依赖与配置层

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Test: `backend/tests/__init__.py`、`backend/tests/test_config.py`

- [ ] **Step 1: 写 `requirements.txt`**

```text
fastapi==0.118.2
uvicorn[standard]==0.32.0
pydantic==2.9.2
pydantic-settings==2.6.1
sqlalchemy[asyncio]==2.0.36
asyncpg==0.30.0
alembic==1.13.3
redis==5.2.0
PyJWT==2.10.0
bcrypt==4.2.0
langchain==0.3.7
langchain-deepseek==0.1.2
sse-starlette==2.1.3
httpx==0.27.2
pytest==8.3.3
pytest-asyncio==0.24.0
```

- [ ] **Step 2: 写 `.env.example`**

```dotenv
# 应用
APP_ENV=dev
APP_HOST=0.0.0.0
APP_PORT=8000
CORS_ORIGINS=http://localhost:5173

# 数据库（PostgreSQL 17，异步驱动 asyncpg）
DATABASE_URL=postgresql+asyncpg://risk:risk@localhost:5432/risk_audit

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET=change-me-32-bytes-min-please-generate-with-openssl-rand-hex-32
JWT_ALGORITHM=HS256
JWT_ACCESS_TTL_MINUTES=120

# 预置管理员
SEED_ADMIN_USERNAME=admin
SEED_ADMIN_PASSWORD=Admin@2026

# DeepSeek
DEEPSEEK_API_KEY=sk-xxxxx
DEEPSEEK_MODEL=deepseek-chat
```

- [ ] **Step 3: 创建虚拟环境并安装**

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

预期：依赖全部安装无报错。

- [ ] **Step 4: 写失败的配置测试 `backend/tests/test_config.py`**

```python
import os
import pytest
from app.config import Settings


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@h/db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/1")
    monkeypatch.setenv("JWT_SECRET", "x" * 32)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test")
    s = Settings()
    assert s.database_url.endswith("/db")
    assert s.jwt_access_ttl_minutes == 120
    assert s.cors_origins == ["http://localhost:5173"]
```

`tests/__init__.py` 留空。

- [ ] **Step 5: 运行测试，预期 ImportError 失败**

```bash
cd backend && pytest tests/test_config.py -v
```

预期：因 `app/config.py` 还没写而报 ImportError。

- [ ] **Step 6: 写 `app/__init__.py`（留空）与 `app/config.py`**

```python
from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_access_ttl_minutes: int = 120

    seed_admin_username: str = "admin"
    seed_admin_password: str = "Admin@2026"

    deepseek_api_key: str
    deepseek_model: str = "deepseek-chat"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, v):
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

- [ ] **Step 7: 再次运行测试，预期通过**

```bash
pytest tests/test_config.py -v
```

预期：1 passed。

- [ ] **Step 8: 提交**

```bash
git add backend/requirements.txt backend/.env.example backend/app/__init__.py backend/app/config.py backend/tests/__init__.py backend/tests/test_config.py
git commit -m "feat(backend): 引入依赖与 Pydantic Settings 配置层"
```

---

### Task 3: FastAPI 入口与健康检查

**Files:**
- Create: `backend/app/main.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_main.py`

- [ ] **Step 1: 写 `tests/conftest.py`（共享 httpx 客户端夹具）**

```python
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
```

- [ ] **Step 2: 写失败测试 `tests/test_main.py`**

```python
import pytest


@pytest.mark.asyncio
async def test_health_returns_ok(client):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
```

- [ ] **Step 3: 运行，预期 ImportError**

```bash
pytest tests/test_main.py -v
```

- [ ] **Step 4: 写 `app/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="灵工企业风控 Agent 系统", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
```

- [ ] **Step 5: 配置 `pytest.ini` 启用 asyncio 模式**

Create: `backend/pytest.ini`

```ini
[pytest]
asyncio_mode = auto
pythonpath = .
```

- [ ] **Step 6: 跑测试，预期通过**

```bash
pytest tests/test_main.py -v
```

预期：1 passed。

- [ ] **Step 7: 启动 dev 服务器手动验证**

```bash
uvicorn app.main:app --reload --port 8000
# 另一个终端：
curl http://localhost:8000/api/health
```

预期：`{"status":"ok"}`，Swagger 在 `http://localhost:8000/docs` 可访问。

- [ ] **Step 8: 提交**

```bash
git add backend/app/main.py backend/tests/conftest.py backend/tests/test_main.py backend/pytest.ini
git commit -m "feat(backend): FastAPI 应用入口与健康检查"
```

---

### Task 4: 数据库引擎与 Session 依赖

**Files:**
- Create: `backend/app/db/__init__.py`
- Create: `backend/app/db/base.py`
- Create: `backend/app/db/session.py`

- [ ] **Step 1: 创建 `backend/app/db/__init__.py`（留空）**

- [ ] **Step 2: 写 `app/db/base.py`**

```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """所有 ORM 模型的基类，统一元数据用于 Alembic 自动探测。"""
    pass
```

- [ ] **Step 3: 写 `app/db/session.py`**

```python
from collections.abc import AsyncIterator
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.config import get_settings


def build_engine() -> AsyncEngine:
    settings = get_settings()
    return create_async_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False,
    )


engine: AsyncEngine = build_engine()
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI 依赖：注入一个异步 Session，作用域为单次请求。"""
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
```

- [ ] **Step 4: 烟测——确保模块可导入**

```bash
python -c "from app.db.session import engine, SessionLocal; print(engine.url)"
```

预期：打印数据库 URL 不报错。

- [ ] **Step 5: 提交**

```bash
git add backend/app/db/__init__.py backend/app/db/base.py backend/app/db/session.py
git commit -m "feat(backend): SQLAlchemy 异步引擎与 Session 依赖"
```

---

## Phase B · 用户与认证

### Task 5: User 模型

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/user.py`

- [ ] **Step 1: 创建 `backend/app/models/__init__.py`**

```python
from app.models.user import User

__all__ = ["User"]
```

- [ ] **Step 2: 写 `app/models/user.py`**

```python
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
```

- [ ] **Step 3: 烟测**

```bash
python -c "from app.models import User; print(User.__tablename__, User.__table__.columns.keys())"
```

预期：`users ['id', 'username', 'password_hash', ...]`

- [ ] **Step 4: 提交**

```bash
git add backend/app/models/__init__.py backend/app/models/user.py
git commit -m "feat(backend): User ORM 模型"
```

---

### Task 6: Alembic 初始化与 users 表迁移

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/script.py.mako`
- Create: `backend/alembic/versions/0001_create_users_table.py`

- [ ] **Step 1: 初始化 Alembic**

```bash
cd backend
alembic init alembic
```

会生成 `alembic.ini`、`alembic/` 目录及 `env.py`。

- [ ] **Step 2: 修改 `alembic.ini`**

把 `sqlalchemy.url` 一行改为占位（真实值由 `env.py` 从 Settings 读取）：

```ini
sqlalchemy.url = driver://user:pass@localhost/dbname
```

并把 `script_location = alembic` 保留。

- [ ] **Step 3: 改写 `alembic/env.py` 为异步 + 读取 Settings**

```python
from logging.config import fileConfig
import asyncio
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from app.config import get_settings
from app.db.base import Base
from app import models  # noqa: F401  确保模型被加载

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

- [ ] **Step 4: 生成 users 表迁移**

```bash
alembic revision --autogenerate -m "create users table" --rev-id 0001
```

预期：生成 `alembic/versions/0001_create_users_table.py`，`upgrade()` 中包含 `op.create_table("users", ...)`。

如果 autogenerate 检测不到（例如本地 DB 未就绪），手动创建文件，内容如下：

```python
"""create users table

Revision ID: 0001
Revises:
Create Date: 2026-06-01

"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(128), nullable=False, server_default=""),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )
    op.create_index("ix_users_username", "users", ["username"])


def downgrade() -> None:
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
```

- [ ] **Step 5: 启动本地 PostgreSQL 17（已有则跳过），创建数据库**

```bash
# 假设本地已安装 Postgres 17
createuser -s risk || true
createdb -O risk risk_audit
```

- [ ] **Step 6: 执行迁移**

```bash
alembic upgrade head
```

预期：日志显示 `Running upgrade  -> 0001`。

- [ ] **Step 7: 验证表已创建**

```bash
psql -d risk_audit -c "\d users"
```

预期：列出 users 表全部字段。

- [ ] **Step 8: 提交**

```bash
git add backend/alembic.ini backend/alembic/env.py backend/alembic/script.py.mako backend/alembic/versions/0001_create_users_table.py
git commit -m "feat(backend): Alembic 异步迁移与 users 表"
```

---

### Task 7: 种子管理员账号

**Files:**
- Create: `backend/alembic/versions/0002_seed_admin_user.py`

- [ ] **Step 1: 写数据迁移**

```python
"""seed admin user

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-01

"""
import bcrypt
from alembic import op
import sqlalchemy as sa

from app.config import get_settings

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    settings = get_settings()
    password_hash = bcrypt.hashpw(
        settings.seed_admin_password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    users = sa.table(
        "users",
        sa.column("username", sa.String),
        sa.column("password_hash", sa.String),
        sa.column("display_name", sa.String),
        sa.column("is_admin", sa.Boolean),
        sa.column("is_active", sa.Boolean),
    )
    op.bulk_insert(
        users,
        [
            {
                "username": settings.seed_admin_username,
                "password_hash": password_hash,
                "display_name": "系统管理员",
                "is_admin": True,
                "is_active": True,
            }
        ],
    )


def downgrade() -> None:
    settings = get_settings()
    op.execute(
        sa.text("DELETE FROM users WHERE username = :u").bindparams(
            u=settings.seed_admin_username
        )
    )
```

- [ ] **Step 2: 执行迁移**

```bash
cd backend
cp .env.example .env  # 若尚未复制
# 编辑 .env 填入真实 DEEPSEEK_API_KEY、JWT_SECRET 等
alembic upgrade head
```

预期：日志显示 `Running upgrade 0001 -> 0002`。

- [ ] **Step 3: 验证 admin 已写入**

```bash
psql -d risk_audit -c "SELECT id, username, is_admin FROM users;"
```

预期：返回 1 行，username=admin，is_admin=t。

- [ ] **Step 4: 提交**

```bash
git add backend/alembic/versions/0002_seed_admin_user.py
git commit -m "feat(backend): 预置管理员账号种子迁移"
```

---

### Task 8: 密码哈希与 JWT 工具

**Files:**
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/security.py`
- Test: `backend/tests/test_security.py`

- [ ] **Step 1: 创建 `app/core/__init__.py`（留空）**

- [ ] **Step 2: 写失败测试 `tests/test_security.py`**

```python
import time
import pytest
from app.core import security


def test_hash_and_verify_password():
    h = security.hash_password("S3cret!")
    assert h != "S3cret!"
    assert security.verify_password("S3cret!", h) is True
    assert security.verify_password("wrong", h) is False


def test_create_and_decode_access_token():
    token = security.create_access_token(subject="alice", ttl_minutes=5)
    payload = security.decode_token(token)
    assert payload["sub"] == "alice"
    assert payload["type"] == "access"
    assert "jti" in payload
    assert "exp" in payload


def test_decode_invalid_token_raises():
    with pytest.raises(security.InvalidTokenError):
        security.decode_token("not.a.jwt")


def test_token_expiry_enforced(monkeypatch):
    token = security.create_access_token(subject="bob", ttl_minutes=-1)
    with pytest.raises(security.InvalidTokenError):
        security.decode_token(token)
```

- [ ] **Step 3: 运行，预期 ImportError**

```bash
pytest tests/test_security.py -v
```

- [ ] **Step 4: 实现 `app/core/security.py`**

```python
import uuid
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError as _JWTInvalidTokenError
from app.config import get_settings

InvalidTokenError = _JWTInvalidTokenError


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str, ttl_minutes: int | None = None) -> str:
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
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
```

- [ ] **Step 5: 跑测试，预期 4 个全部通过**

```bash
pytest tests/test_security.py -v
```

- [ ] **Step 6: 提交**

```bash
git add backend/app/core/__init__.py backend/app/core/security.py backend/tests/test_security.py
git commit -m "feat(backend): bcrypt 密码哈希与 JWT 工具"
```

---

### Task 9: Redis 客户端与 JWT 黑名单

**Files:**
- Create: `backend/app/core/redis_client.py`
- Test: `backend/tests/test_redis_client.py`

- [ ] **Step 1: 写失败测试 `tests/test_redis_client.py`**

```python
import pytest
from app.core import redis_client


@pytest.mark.asyncio
async def test_blacklist_roundtrip():
    jti = "test-jti-roundtrip"
    assert await redis_client.is_blacklisted(jti) is False
    await redis_client.add_to_blacklist(jti, ttl_seconds=60)
    assert await redis_client.is_blacklisted(jti) is True
    # 清理
    client = redis_client.get_redis()
    await client.delete(redis_client._key(jti))
```

- [ ] **Step 2: 跑测试，预期 ImportError**

```bash
pytest tests/test_redis_client.py -v
```

- [ ] **Step 3: 实现 `app/core/redis_client.py`**

```python
from redis.asyncio import Redis, from_url
from app.config import get_settings

_BL_PREFIX = "jwt:blacklist:"
_redis: Redis | None = None


def get_redis() -> Redis:
    global _redis
    if _redis is None:
        settings = get_settings()
        _redis = from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    return _redis


def _key(jti: str) -> str:
    return f"{_BL_PREFIX}{jti}"


async def add_to_blacklist(jti: str, ttl_seconds: int) -> None:
    client = get_redis()
    await client.set(_key(jti), "1", ex=ttl_seconds)


async def is_blacklisted(jti: str) -> bool:
    client = get_redis()
    return await client.exists(_key(jti)) == 1
```

- [ ] **Step 4: 启动本地 Redis 后运行测试**

```bash
# 已安装则启动；macOS: brew services start redis
pytest tests/test_redis_client.py -v
```

预期：1 passed。

- [ ] **Step 5: 提交**

```bash
git add backend/app/core/redis_client.py backend/tests/test_redis_client.py
git commit -m "feat(backend): Redis 客户端与 JWT 黑名单工具"
```

---

### Task 10: 认证依赖 get_current_user

**Files:**
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/user_service.py`
- Create: `backend/app/deps/__init__.py`
- Create: `backend/app/deps/auth.py`

- [ ] **Step 1: 创建空 `__init__.py`**

```bash
touch backend/app/schemas/__init__.py backend/app/services/__init__.py backend/app/deps/__init__.py
```

- [ ] **Step 2: 写 `app/schemas/auth.py`**

> 登录请求体复用 FastAPI 的 `OAuth2PasswordRequestForm`（form 编码 username/password），因此此处只定义响应 Schema。

```python
from datetime import datetime
from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # 秒


class UserOut(BaseModel):
    id: int
    username: str
    display_name: str
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 3: 写 `app/services/user_service.py`**

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.security import verify_password


async def get_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def authenticate(db: AsyncSession, username: str, password: str) -> User | None:
    user = await get_by_username(db, username)
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
```

- [ ] **Step 4: 写 `app/deps/auth.py`**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.redis_client import is_blacklisted
from app.db.session import get_db
from app.models.user import User
from app.services import user_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


CREDENTIALS_EXC = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="无效或过期的凭证",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = security.decode_token(token)
    except security.InvalidTokenError:
        raise CREDENTIALS_EXC

    jti = payload.get("jti")
    sub = payload.get("sub")
    if not jti or not sub:
        raise CREDENTIALS_EXC

    if await is_blacklisted(jti):
        raise CREDENTIALS_EXC

    user = await user_service.get_by_username(db, sub)
    if user is None or not user.is_active:
        raise CREDENTIALS_EXC

    return user
```

- [ ] **Step 5: 烟测——确认模块互相可导入**

```bash
python -c "from app.deps.auth import get_current_user; from app.schemas.auth import LoginRequest; print('ok')"
```

预期：`ok`。

- [ ] **Step 6: 提交**

```bash
git add backend/app/schemas/__init__.py backend/app/schemas/auth.py backend/app/services/__init__.py backend/app/services/user_service.py backend/app/deps/__init__.py backend/app/deps/auth.py
git commit -m "feat(backend): 认证 Schema、用户服务与 get_current_user 依赖"
```

---

### Task 11: 登录 / 登出 / Me 接口

**Files:**
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/auth.py`
- Modify: `backend/app/main.py`（挂载路由）
- Test: `backend/tests/test_auth_api.py`

- [ ] **Step 1: 创建空 `app/api/__init__.py`**

- [ ] **Step 2: 写失败测试 `tests/test_auth_api.py`**

```python
import pytest


@pytest.mark.asyncio
async def test_login_success(client):
    resp = await client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "Admin@2026"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["expires_in"] > 0


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    resp = await client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "wrong"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_token(client):
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_returns_current_user(client):
    login = await client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "Admin@2026"},
    )
    token = login.json()["access_token"]
    resp = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "admin"


@pytest.mark.asyncio
async def test_logout_blacklists_token(client):
    login = await client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "Admin@2026"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.post("/api/auth/logout", headers=headers)
    assert resp.status_code == 204
    # 再次调用 /me 应当失败
    resp2 = await client.get("/api/auth/me", headers=headers)
    assert resp2.status_code == 401
```

- [ ] **Step 3: 跑测试，预期 ImportError / 404**

```bash
pytest tests/test_auth_api.py -v
```

- [ ] **Step 4: 实现 `app/api/auth.py`**

```python
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
    return current


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(token: str = Depends(oauth2_scheme)) -> None:
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
```

- [ ] **Step 5: 修改 `app/main.py` 挂载路由**

把 `app/main.py` 的 `create_app()` 改写为：

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api import auth as auth_router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="灵工企业风控 Agent 系统", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(auth_router.router)
    return app


app = create_app()
```

- [ ] **Step 6: 跑测试，预期 5 个全部通过**

```bash
pytest tests/test_auth_api.py -v
```

提示：测试需要本地 Postgres + Redis + 已 `alembic upgrade head`（管理员已种入）。

- [ ] **Step 7: 跑全部测试**

```bash
pytest -v
```

预期：所有测试通过。

- [ ] **Step 8: 提交**

```bash
git add backend/app/api/__init__.py backend/app/api/auth.py backend/app/main.py backend/tests/test_auth_api.py
git commit -m "feat(backend): 登录 / 登出 / Me 接口"
```

---

## Phase C · 对话与 LLM

### Task 12: DeepSeek 流式服务

**Files:**
- Create: `backend/app/services/llm_service.py`
- Create: `backend/app/schemas/chat.py`
- Test: `backend/tests/test_llm_service.py`

- [ ] **Step 1: 写 `app/schemas/chat.py`**

```python
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
```

- [ ] **Step 2: 写失败测试 `tests/test_llm_service.py`**

```python
import pytest
from unittest.mock import AsyncMock, patch
from app.services import llm_service


class _Chunk:
    def __init__(self, content: str):
        self.content = content


@pytest.mark.asyncio
async def test_stream_chat_yields_text_chunks():
    async def fake_astream(messages):
        for c in [_Chunk("你"), _Chunk("好"), _Chunk("！")]:
            yield c

    with patch.object(llm_service, "_build_llm") as build:
        llm = build.return_value
        llm.astream = fake_astream
        chunks = [c async for c in llm_service.stream_chat("hi")]
    assert "".join(chunks) == "你好！"
```

- [ ] **Step 3: 跑测试，预期 ImportError**

```bash
pytest tests/test_llm_service.py -v
```

- [ ] **Step 4: 实现 `app/services/llm_service.py`**

```python
from collections.abc import AsyncIterator
from langchain_deepseek import ChatDeepSeek
from app.config import get_settings


def _build_llm() -> ChatDeepSeek:
    settings = get_settings()
    return ChatDeepSeek(
        model=settings.deepseek_model,
        api_key=settings.deepseek_api_key,
        temperature=0.3,
        max_retries=2,
        streaming=True,
    )


async def stream_chat(user_message: str) -> AsyncIterator[str]:
    """对外暴露：传入用户单轮文本，异步产出 LLM 文本片段。

    第一步仅做单轮无记忆调用，后续接入对话记忆 / LangGraph 时只需替换此函数。
    """
    llm = _build_llm()
    messages = [
        ("system", "你是灵工企业风控 Agent 系统的智能助手，回答专业且简洁。"),
        ("human", user_message),
    ]
    async for chunk in llm.astream(messages):
        text = getattr(chunk, "content", "")
        if text:
            yield text
```

- [ ] **Step 5: 跑测试，预期通过**

```bash
pytest tests/test_llm_service.py -v
```

- [ ] **Step 6: 提交**

```bash
git add backend/app/schemas/chat.py backend/app/services/llm_service.py backend/tests/test_llm_service.py
git commit -m "feat(backend): DeepSeek 流式封装与 ChatRequest schema"
```

---

### Task 13: 对话 SSE 接口

**Files:**
- Create: `backend/app/api/chat.py`
- Modify: `backend/app/main.py`（挂载 chat 路由）
- Test: `backend/tests/test_chat_api.py`

- [ ] **Step 1: 写失败测试 `tests/test_chat_api.py`**

```python
import pytest
from unittest.mock import patch


async def _fake_stream(_msg: str):
    for piece in ["你", "好", "，", "我是", "助手"]:
        yield piece


@pytest.mark.asyncio
async def test_chat_stream_requires_auth(client):
    resp = await client.post("/api/chat/stream", json={"message": "hi"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_chat_stream_sse_with_auth(client):
    login = await client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "Admin@2026"},
    )
    token = login.json()["access_token"]

    with patch("app.api.chat.stream_chat", side_effect=lambda m: _fake_stream(m)):
        resp = await client.post(
            "/api/chat/stream",
            json={"message": "你好"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/event-stream")
        body = resp.text
        # 应包含逐段 data: 行与最终 done 事件
        assert "data:" in body
        assert "你好" in body or "你" in body
        assert "event: done" in body
```

- [ ] **Step 2: 跑测试，预期 404 / ImportError**

```bash
pytest tests/test_chat_api.py -v
```

- [ ] **Step 3: 实现 `app/api/chat.py`**

```python
import json
from collections.abc import AsyncIterator
from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse

from app.deps.auth import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest
from app.services.llm_service import stream_chat

router = APIRouter(prefix="/api/chat", tags=["chat"])


async def _event_generator(message: str) -> AsyncIterator[dict]:
    try:
        async for piece in stream_chat(message):
            yield {"event": "message", "data": json.dumps({"delta": piece}, ensure_ascii=False)}
        yield {"event": "done", "data": json.dumps({"finish_reason": "stop"})}
    except Exception as exc:  # noqa: BLE001
        yield {"event": "error", "data": json.dumps({"message": str(exc)}, ensure_ascii=False)}


@router.post("/stream")
async def chat_stream(
    req: ChatRequest,
    current: User = Depends(get_current_user),
) -> EventSourceResponse:
    return EventSourceResponse(_event_generator(req.message))
```

- [ ] **Step 4: 在 `app/main.py` 挂载 chat 路由**

在 `create_app()` 内：

```python
from app.api import auth as auth_router, chat as chat_router
# ...
app.include_router(auth_router.router)
app.include_router(chat_router.router)
```

- [ ] **Step 5: 跑测试，预期通过**

```bash
pytest tests/test_chat_api.py -v
```

- [ ] **Step 6: 手动验证（需要真实 DEEPSEEK_API_KEY）**

```bash
uvicorn app.main:app --reload --port 8000
# 另一个终端
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -d 'username=admin&password=Admin@2026' | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
curl -N -X POST http://localhost:8000/api/chat/stream \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"message":"用一句话介绍你自己"}'
```

预期：终端逐段打印 `event: message\ndata: {"delta":"..."}` 直到 `event: done`。

- [ ] **Step 7: 跑全部后端测试**

```bash
pytest -v
```

预期：全部通过。

- [ ] **Step 8: 提交**

```bash
git add backend/app/api/chat.py backend/app/main.py backend/tests/test_chat_api.py
git commit -m "feat(backend): 对话 SSE 流式接口"
```

---

## Phase D · 前端骨架与认证页

### Task 14: 前端脚手架与依赖

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tsconfig.node.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/env.d.ts`
- Create: `frontend/.env.example`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`

- [ ] **Step 1: 用 Vite 模板初始化**

```bash
cd frontend
npm create vite@latest . -- --template vue-ts
# 选择不覆盖现有 .gitkeep，确认 vue-ts 模板
```

- [ ] **Step 2: 安装运行时依赖**

```bash
npm install vue-router@4 pinia naive-ui axios
npm install -D @types/node vitest @vue/test-utils jsdom
```

- [ ] **Step 3: 覆盖 `package.json` scripts 段，确保至少包含**

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc -b && vite build",
    "preview": "vite preview",
    "test": "vitest run"
  }
}
```

- [ ] **Step 4: 写 `vite.config.ts`，配置 `/api` 代理**

```ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 5: 写 `tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "jsx": "preserve",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "noEmit": true,
    "baseUrl": ".",
    "paths": { "@/*": ["src/*"] },
    "types": ["vite/client", "node"]
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.vue", "env.d.ts"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

`tsconfig.node.json`：

```json
{
  "compilerOptions": {
    "composite": true,
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "noEmit": true
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **Step 6: 写 `env.d.ts`**

```ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

- [ ] **Step 7: 写 `.env.example`**

```dotenv
VITE_API_BASE=/api
```

- [ ] **Step 8: 写 `index.html`**

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>灵工企业风控 Agent 系统</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

- [ ] **Step 9: 写 `src/App.vue`（Task 17 会替换为带 RouterView 的版本）**

```vue
<template>
  <n-config-provider :theme-overrides="{}">
    <n-message-provider>
      <n-h1 style="text-align:center;margin-top:40vh">脚手架就绪</n-h1>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { NConfigProvider, NMessageProvider, NH1 } from 'naive-ui'
</script>
```

- [ ] **Step 10: 写 `src/main.ts`（Task 17 会替换为带 router 的版本）**

```ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

const app = createApp(App)
app.use(createPinia())
app.mount('#app')
```

- [ ] **Step 11: 启动验证**

```bash
npm run dev
# 浏览器访问 http://localhost:5173 应当看到「脚手架就绪」标题
```

预期：页面正常渲染，无控制台报错。

- [ ] **Step 12: 提交**

```bash
git add frontend/package.json frontend/package-lock.json frontend/tsconfig.json frontend/tsconfig.node.json frontend/vite.config.ts frontend/index.html frontend/env.d.ts frontend/.env.example frontend/src/main.ts frontend/src/App.vue
git commit -m "feat(frontend): Vite + Vue3 + TS 脚手架与依赖"
```

---

### Task 15: HTTP 客户端

**Files:**
- Create: `frontend/src/api/http.ts`

- [ ] **Step 1: 写 `src/api/http.ts`**

```ts
import axios, { AxiosError, type AxiosInstance } from 'axios'

const BASE = import.meta.env.VITE_API_BASE ?? '/api'

export const http: AxiosInstance = axios.create({
  baseURL: BASE,
  timeout: 30000,
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.set('Authorization', `Bearer ${token}`)
  }
  return config
})

http.interceptors.response.use(
  (resp) => resp,
  (err: AxiosError) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token')
      // 避免循环：仅在非登录页时跳转
      if (location.pathname !== '/login') {
        location.replace('/login')
      }
    }
    return Promise.reject(err)
  },
)
```

- [ ] **Step 2: 烟测——`npm run build` 通过类型检查**

```bash
cd frontend && npm run build
```

预期：构建成功（即使内容很少）。

- [ ] **Step 3: 提交**

```bash
git add frontend/src/api/http.ts
git commit -m "feat(frontend): axios 客户端与 401 拦截"
```

---

### Task 16: Pinia 认证 Store

**Files:**
- Create: `frontend/src/api/auth.ts`
- Create: `frontend/src/stores/auth.ts`

- [ ] **Step 1: 写 `src/api/auth.ts`**

```ts
import { http } from './http'

export interface UserOut {
  id: number
  username: string
  display_name: string
  is_admin: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export async function login(username: string, password: string): Promise<TokenResponse> {
  // OAuth2 form 风格
  const body = new URLSearchParams()
  body.set('username', username)
  body.set('password', password)
  const { data } = await http.post<TokenResponse>('/auth/login', body, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return data
}

export async function logout(): Promise<void> {
  await http.post('/auth/logout')
}

export async function me(): Promise<UserOut> {
  const { data } = await http.get<UserOut>('/auth/me')
  return data
}
```

- [ ] **Step 2: 写 `src/stores/auth.ts`**

```ts
import { defineStore } from 'pinia'
import * as authApi from '@/api/auth'

interface State {
  token: string | null
  user: authApi.UserOut | null
}

export const useAuthStore = defineStore('auth', {
  state: (): State => ({
    token: localStorage.getItem('access_token'),
    user: null,
  }),
  getters: {
    isAuthenticated: (s) => !!s.token,
  },
  actions: {
    async login(username: string, password: string) {
      const tk = await authApi.login(username, password)
      this.token = tk.access_token
      localStorage.setItem('access_token', tk.access_token)
      await this.fetchMe()
    },
    async fetchMe() {
      this.user = await authApi.me()
    },
    async logout() {
      try {
        await authApi.logout()
      } catch (_) {
        // 即使后端报错也清本地
      }
      this.token = null
      this.user = null
      localStorage.removeItem('access_token')
    },
  },
})
```

- [ ] **Step 3: 烟测**

```bash
npm run build
```

预期：构建成功。

- [ ] **Step 4: 提交**

```bash
git add frontend/src/api/auth.ts frontend/src/stores/auth.ts
git commit -m "feat(frontend): 认证 API 与 Pinia store"
```

---

### Task 17: 路由与守卫

**Files:**
- Create: `frontend/src/router/index.ts`
- Modify: `frontend/src/main.ts`
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: 写 `src/router/index.ts`**

```ts
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/chat' },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/chat',
    name: 'chat',
    component: () => import('@/views/ChatView.vue'),
  },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  const isPublic = to.meta.public === true

  if (isPublic) {
    return true
  }
  if (!auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  // 首次进入受保护页时拉取用户信息
  if (!auth.user) {
    try {
      await auth.fetchMe()
    } catch {
      return { name: 'login' }
    }
  }
  return true
})
```

- [ ] **Step 2: 改写 `src/main.ts` 接入 router**

```ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import { router } from './router'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
```

- [ ] **Step 3: 改写 `src/App.vue` 渲染 RouterView**

```vue
<template>
  <n-config-provider :theme-overrides="{}">
    <n-message-provider>
      <RouterView />
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import { NConfigProvider, NMessageProvider } from 'naive-ui'
</script>
```

- [ ] **Step 4: 烟测**

```bash
npm run dev
# 浏览器访问 http://localhost:5173
# 应当被路由守卫重定向到 /login（LoginView 在 Task 18 实现，此时可能空白；下一任务补全）
```

- [ ] **Step 5: 提交**

```bash
git add frontend/src/router/index.ts frontend/src/main.ts frontend/src/App.vue
git commit -m "feat(frontend): 路由与登录守卫"
```

---

### Task 18: 登录页

**Files:**
- Create: `frontend/src/views/LoginView.vue`

- [ ] **Step 1: 写 `src/views/LoginView.vue`**

```vue
<template>
  <div class="login-wrap">
    <n-card class="login-card" title="灵工企业风控 Agent 系统">
      <n-form ref="formRef" :model="form" :rules="rules" label-placement="top" @submit.prevent>
        <n-form-item label="用户名" path="username">
          <n-input v-model:value="form.username" placeholder="请输入用户名" autofocus />
        </n-form-item>
        <n-form-item label="密码" path="password">
          <n-input
            v-model:value="form.password"
            type="password"
            show-password-on="click"
            placeholder="请输入密码"
            @keyup.enter="handleLogin"
          />
        </n-form-item>
        <n-button type="primary" block :loading="loading" @click="handleLogin">登 录</n-button>
      </n-form>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NCard,
  NForm,
  NFormItem,
  NInput,
  NButton,
  useMessage,
  type FormInst,
  type FormRules,
} from 'naive-ui'
import { useAuthStore } from '@/stores/auth'

const form = reactive({ username: '', password: '' })
const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}
const formRef = ref<FormInst | null>(null)
const loading = ref(false)
const message = useMessage()
const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

async function handleLogin() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }
  loading.value = true
  try {
    await auth.login(form.username.trim(), form.password)
    message.success('登录成功')
    const redirect = (route.query.redirect as string) || '/chat'
    router.replace(redirect)
  } catch (e: any) {
    const msg = e?.response?.data?.detail ?? '登录失败，请重试'
    message.error(typeof msg === 'string' ? msg : '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrap {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa, #e4ecf7);
}
.login-card {
  width: 380px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
}
</style>
```

- [ ] **Step 2: 手动验证**

```bash
npm run dev
# 浏览器访问 http://localhost:5173/login
# 1. 用错误密码 → 应显示错误提示
# 2. 用 admin / Admin@2026 → 成功后被路由到 /chat（此页尚未实现，会空白，下一任务补全）
# 3. 浏览器控制台检查 localStorage.access_token 已写入
```

需要后端在 `localhost:8000` 已启动。

- [ ] **Step 3: 提交**

```bash
git add frontend/src/views/LoginView.vue
git commit -m "feat(frontend): 登录页与登录闭环"
```

---

## Phase E · 对话页与 SSE 流式

### Task 19: 对话页布局与消息组件

**Files:**
- Create: `frontend/src/components/ChatMessage.vue`
- Create: `frontend/src/components/ChatInput.vue`
- Create: `frontend/src/views/ChatView.vue`

- [ ] **Step 1: 写 `src/components/ChatMessage.vue`**

```vue
<template>
  <div class="msg" :class="role">
    <div class="bubble">
      <span v-if="content">{{ content }}</span>
      <span v-else class="placeholder">…</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ role: 'user' | 'assistant'; content: string }>()
</script>

<style scoped>
.msg {
  display: flex;
  margin: 8px 0;
}
.msg.user { justify-content: flex-end; }
.msg.assistant { justify-content: flex-start; }
.bubble {
  max-width: 70%;
  padding: 10px 14px;
  border-radius: 12px;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
}
.msg.user .bubble { background: #2080f0; color: #fff; }
.msg.assistant .bubble { background: #f0f2f5; color: #1f2329; }
.placeholder { opacity: 0.5; }
</style>
```

- [ ] **Step 2: 写 `src/components/ChatInput.vue`**

```vue
<template>
  <div class="input-wrap">
    <n-input
      v-model:value="text"
      type="textarea"
      :autosize="{ minRows: 1, maxRows: 6 }"
      placeholder="请输入消息（Enter 发送，Shift+Enter 换行）"
      :disabled="disabled"
      @keydown.enter.exact.prevent="onSend"
    />
    <n-button type="primary" :loading="disabled" :disabled="!canSend" @click="onSend">
      发送
    </n-button>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { NInput, NButton } from 'naive-ui'

const props = defineProps<{ disabled: boolean }>()
const emit = defineEmits<{ (e: 'send', text: string): void }>()

const text = ref('')
const canSend = computed(() => text.value.trim().length > 0 && !props.disabled)

function onSend() {
  if (!canSend.value) return
  const t = text.value.trim()
  text.value = ''
  emit('send', t)
}
</script>

<style scoped>
.input-wrap {
  display: flex;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid #eee;
  background: #fff;
}
</style>
```

- [ ] **Step 3: 写 `src/views/ChatView.vue`（仅布局，SSE 在下一任务接入）**

```vue
<template>
  <div class="chat-shell">
    <header class="chat-header">
      <span class="title">灵工企业风控 Agent 系统</span>
      <n-space :size="12" align="center">
        <span v-if="auth.user" class="user">{{ auth.user.display_name || auth.user.username }}</span>
        <n-button quaternary size="small" @click="onLogout">退出登录</n-button>
      </n-space>
    </header>

    <main class="chat-body" ref="bodyRef">
      <ChatMessage
        v-for="(m, i) in messages"
        :key="i"
        :role="m.role"
        :content="m.content"
      />
    </main>

    <ChatInput :disabled="sending" @send="onSend" />
  </div>
</template>

<script setup lang="ts">
import { nextTick, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NSpace, useMessage } from 'naive-ui'
import { useAuthStore } from '@/stores/auth'
import ChatMessage from '@/components/ChatMessage.vue'
import ChatInput from '@/components/ChatInput.vue'

interface Msg { role: 'user' | 'assistant'; content: string }

const auth = useAuthStore()
const router = useRouter()
const message = useMessage()

const messages = reactive<Msg[]>([])
const sending = ref(false)
const bodyRef = ref<HTMLElement | null>(null)

async function onSend(text: string) {
  messages.push({ role: 'user', content: text })
  messages.push({ role: 'assistant', content: '' })
  await scrollToBottom()

  sending.value = true
  try {
    // SSE 接入将在 Task 20 实现
    messages[messages.length - 1].content = '（占位回复 — 待 Task 20 接入流式）'
  } finally {
    sending.value = false
    await scrollToBottom()
  }
}

async function onLogout() {
  await auth.logout()
  message.success('已退出')
  router.replace('/login')
}

async function scrollToBottom() {
  await nextTick()
  const el = bodyRef.value
  if (el) el.scrollTop = el.scrollHeight
}
</script>

<style scoped>
.chat-shell {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #fafafa;
}
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: #fff;
  border-bottom: 1px solid #eee;
}
.chat-header .title { font-weight: 600; font-size: 16px; }
.chat-header .user { color: #666; font-size: 13px; }
.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}
</style>
```

- [ ] **Step 4: 手动验证**

```bash
npm run dev
# 登录后应进入对话页：可看到标题栏、退出登录按钮、底部输入框
# 输入「你好」点发送 → 应出现用户气泡 + 占位的助手气泡
```

- [ ] **Step 5: 提交**

```bash
git add frontend/src/components/ChatMessage.vue frontend/src/components/ChatInput.vue frontend/src/views/ChatView.vue
git commit -m "feat(frontend): 对话页布局与消息 / 输入组件"
```

---

### Task 20: 对话 SSE 流式接入

**Files:**
- Create: `frontend/src/api/chat.ts`
- Modify: `frontend/src/views/ChatView.vue`

- [ ] **Step 1: 写 `src/api/chat.ts`**

```ts
const BASE = import.meta.env.VITE_API_BASE ?? '/api'

export interface StreamHandlers {
  onDelta: (text: string) => void
  onDone?: () => void
  onError?: (msg: string) => void
}

/**
 * 调用 /chat/stream（SSE 协议），逐 token 触发 onDelta。
 * 因为需要 POST + 自定义 Header，浏览器原生 EventSource 不适用，改用 fetch + ReadableStream 解析 text/event-stream。
 */
export async function streamChat(message: string, handlers: StreamHandlers, signal?: AbortSignal) {
  const token = localStorage.getItem('access_token') ?? ''
  const resp = await fetch(`${BASE}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      Accept: 'text/event-stream',
    },
    body: JSON.stringify({ message }),
    signal,
  })

  if (!resp.ok || !resp.body) {
    handlers.onError?.(`请求失败：${resp.status}`)
    return
  }

  const reader = resp.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    // SSE 帧以空行（\n\n）分割
    const frames = buffer.split('\n\n')
    buffer = frames.pop() ?? ''

    for (const raw of frames) {
      let event = 'message'
      const dataLines: string[] = []
      for (const line of raw.split('\n')) {
        if (line.startsWith('event:')) event = line.slice(6).trim()
        else if (line.startsWith('data:')) dataLines.push(line.slice(5).trim())
      }
      if (dataLines.length === 0) continue
      const payload = dataLines.join('\n')

      if (event === 'message') {
        try {
          const obj = JSON.parse(payload) as { delta?: string }
          if (obj.delta) handlers.onDelta(obj.delta)
        } catch {
          // 忽略非 JSON 帧
        }
      } else if (event === 'done') {
        handlers.onDone?.()
        return
      } else if (event === 'error') {
        try {
          const obj = JSON.parse(payload) as { message?: string }
          handlers.onError?.(obj.message ?? '未知错误')
        } catch {
          handlers.onError?.(payload)
        }
        return
      }
    }
  }
  handlers.onDone?.()
}
```

- [ ] **Step 2: 修改 `src/views/ChatView.vue` 的 `onSend`**

把脚本顶部新增 import：

```ts
import { streamChat } from '@/api/chat'
```

把 `onSend` 替换为：

```ts
async function onSend(text: string) {
  messages.push({ role: 'user', content: text })
  messages.push({ role: 'assistant', content: '' })
  const idx = messages.length - 1
  await scrollToBottom()

  sending.value = true
  try {
    await streamChat(text, {
      onDelta: (piece) => {
        messages[idx].content += piece
        scrollToBottom()
      },
      onError: (m) => {
        message.error(m)
        messages[idx].content = messages[idx].content || `（请求失败：${m}）`
      },
    })
  } finally {
    sending.value = false
    await scrollToBottom()
  }
}
```

- [ ] **Step 3: 端到端手动验证**

```bash
# 终端 1
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# 终端 2
cd frontend && npm run dev
```

浏览器访问 `http://localhost:5173`：

1. 被重定向到 `/login`
2. 输入 admin / Admin@2026 登录
3. 进入对话页，输入「用一句话介绍你自己」
4. 预期：助手气泡逐字渲染 DeepSeek 的回复
5. 点击「退出登录」→ 跳回 `/login`
6. 再次粘贴旧 token 调用 `/api/auth/me` 应当返回 401（黑名单生效）

- [ ] **Step 4: 提交**

```bash
git add frontend/src/api/chat.ts frontend/src/views/ChatView.vue
git commit -m "feat(frontend): 对话 SSE 流式接入"
```

---

## Phase F · 联调与启动文档

### Task 21: 端到端联调与启动文档

**Files:**
- Modify: `README.md`
- Create: `docs/RUNNING.md`

- [ ] **Step 1: 充实根目录 `README.md`**

```markdown
# 灵工企业风控 Agent 系统

单仓 monorepo：

- `backend/` — FastAPI + LangChain（DeepSeek）+ SQLAlchemy 2.x + PostgreSQL 17 + Redis
- `frontend/` — Vite + Vue 3 + TypeScript + Naive UI + Pinia + Vue Router
- `docs/` — 文档与实施计划

当前进度：已完成「登录 + 对话外壳」最小闭环（见 `docs/superpowers/plans/2026-06-01-step1-auth-and-chat-shell.md`）。

## 快速开始

详见 [docs/RUNNING.md](docs/RUNNING.md)。
```

- [ ] **Step 2: 写 `docs/RUNNING.md`**

```markdown
# 本地运行指南

## 1. 系统依赖

- Python 3.12.13
- Node.js ≥ 20
- PostgreSQL 17（监听 5432）
- Redis ≥ 7（监听 6379）
- DeepSeek API Key（从 https://platform.deepseek.com 获取）

## 2. 准备数据库

```bash
createuser -s risk || true
createdb -O risk risk_audit
```

## 3. 启动后端

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# 修改 .env：
#   - JWT_SECRET 用 `openssl rand -hex 32` 生成
#   - DEEPSEEK_API_KEY 填真实 key
#   - SEED_ADMIN_PASSWORD 可改为强密码

alembic upgrade head    # 创建表 + 种子 admin
uvicorn app.main:app --reload --port 8000
```

后端运行在 http://localhost:8000，Swagger 文档：http://localhost:8000/docs。

## 4. 启动前端

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

前端运行在 http://localhost:5173。

## 5. 验证流程

1. 浏览器打开 http://localhost:5173 → 自动跳转 `/login`
2. 输入 `admin` / `.env` 中的 `SEED_ADMIN_PASSWORD` 登录
3. 进入对话页 → 输入消息 → 应看到 DeepSeek 流式逐字回复
4. 点「退出登录」→ token 进入 Redis 黑名单，旧 token 无法再访问

## 6. 运行测试

```bash
cd backend && pytest -v
```

## 7. 常见问题

| 现象 | 检查 |
|------|------|
| 登录 500 | `.env` 的 `DATABASE_URL` 是否正确；`alembic upgrade head` 是否已执行 |
| 登录 401 | `SEED_ADMIN_PASSWORD` 与登录密码是否一致；admin 是否已种入（`SELECT * FROM users`） |
| 对话无响应 | `DEEPSEEK_API_KEY` 是否有效、是否欠费；查看后端日志 |
| 退出后旧 token 仍能访问 | Redis 是否启动；查看 `redis-cli keys 'jwt:blacklist:*'` |
```

- [ ] **Step 3: 手动跑完整流程，验证文档准确性**

按 `docs/RUNNING.md` 步骤从零执行一遍，遇到说不清楚的地方就回去补文档。

- [ ] **Step 4: 跑全部后端测试**

```bash
cd backend && pytest -v
```

预期：全部通过。

- [ ] **Step 5: 提交**

```bash
git add README.md docs/RUNNING.md
git commit -m "docs: 启动指南与项目说明"
```

---

## 完成判定

下列条件全部满足时本步骤完成：

1. `pytest -v`（后端）全部通过。
2. 浏览器从 `/login` 用 admin 登录成功，跳转到 `/chat`。
3. 在 `/chat` 发送消息可看到 DeepSeek 流式逐字回复。
4. 点击「退出登录」后 token 进入 Redis 黑名单，旧 token 调 `/api/auth/me` 返回 401。
5. 刷新 `/chat` 页面，因为 localStorage 已清除会被路由守卫重定向到 `/login`。
6. 项目目录结构与「目录结构总览」一致，所有 Python 模块可导入、前端 `npm run build` 成功。

## 下一步预告（不在本计划范围内）

- **Step 2**：引入 LangGraph + 对话记忆，持久化会话历史到 PostgreSQL。
- **Step 3**：接入业务工具（如灵工合规查询、税务核验），通过 Graph Node 调度。
- **Step 4**：审计与可观测性（LangSmith / OpenTelemetry）、多租户与角色权限。
