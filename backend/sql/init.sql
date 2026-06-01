-- 灵工企业风控 Agent 系统 · 数据库初始化脚本
-- 兼容 PostgreSQL 14+
-- 用法：
--   psql -h 47.93.140.34 -p 5433 -U <user> -d risk_audit -f backend/sql/init.sql
-- 等价于：
--   cd backend && alembic upgrade head
-- 选择其一即可。Alembic 是版本化源头，本文件仅用于不便引入 Python 依赖的运维场景。

BEGIN;

-- ---------- alembic_version 表（避免后续 alembic 重复迁移）----------
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- ---------- users 表（对应 Alembic 迁移 0001）----------
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(64)  NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    display_name    VARCHAR(128) NOT NULL DEFAULT '',
    is_admin        BOOLEAN      NOT NULL DEFAULT FALSE,
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_users_username UNIQUE (username)
);

CREATE INDEX IF NOT EXISTS ix_users_username ON users (username);

-- ---------- 种子管理员账号（对应 Alembic 迁移 0002）----------
-- bcrypt 哈希值对应明文 "Admin@2026"；
-- 如需更换密码，请用 Python 重新生成：
--   python -c "import bcrypt; print(bcrypt.hashpw(b'<新密码>', bcrypt.gensalt()).decode())"
INSERT INTO users (username, password_hash, display_name, is_admin, is_active)
VALUES (
    'admin',
    '$2b$12$JOf7hNt7g9DIxRHxChtqNeEgR5o4U.9xVnvvK3Bu3Nyi9usYq5ZTy',
    '系统管理员',
    TRUE,
    TRUE
)
ON CONFLICT (username) DO NOTHING;

-- ---------- 标记 Alembic 已到 head（0002）----------
INSERT INTO alembic_version (version_num)
VALUES ('0002')
ON CONFLICT DO NOTHING;

COMMIT;

-- 验证：
--   SELECT id, username, is_admin, is_active FROM users;
--   SELECT * FROM alembic_version;
