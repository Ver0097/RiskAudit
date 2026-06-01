# 数据库 SQL 维护

本目录维护「灵工企业风控 Agent 系统」的 PostgreSQL 建库脚本。

## 文件清单

- `init.sql` — 全量初始化：建表 + 索引 + 种子管理员 + 写入 alembic_version。**幂等**（使用 `IF NOT EXISTS` / `ON CONFLICT DO NOTHING`）。

## 何时用 SQL，何时用 Alembic

| 场景 | 推荐方式 |
|------|---------|
| 本地/CI 用 Python 启动 | `alembic upgrade head` |
| 远程库已就绪、无 Python 环境 | `psql ... -f backend/sql/init.sql` |
| 表结构变更（增/改/删字段） | **必须**先写 Alembic 迁移，再手动同步到 `init.sql` |
| 紧急排障、需要查看完整建库 SQL | 直接读 `init.sql` |

**Alembic 是版本化源头**。SQL 文件仅作为同步快照，两者必须保持同步——任何 schema 变更先落到 Alembic，再 review 后同步 SQL。

## 远程 PG 初始化步骤

```bash
# 1. 在远程 PG 上创建数据库与账号（若尚未创建）
psql -h 47.93.140.34 -p 5433 -U postgres <<'SQL'
CREATE USER risk WITH PASSWORD 'risk';
CREATE DATABASE risk_audit OWNER risk;
GRANT ALL PRIVILEGES ON DATABASE risk_audit TO risk;
SQL

# 2. 用 init.sql 初始化表结构与管理员账号
psql -h 47.93.140.34 -p 5433 -U risk -d risk_audit -f backend/sql/init.sql

# 3. 验证
psql -h 47.93.140.34 -p 5433 -U risk -d risk_audit -c "SELECT id, username, is_admin FROM users;"
```

## 重置数据库（开发用）

```sql
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS alembic_version;
```

或更猛烈：

```bash
psql -h 47.93.140.34 -p 5433 -U postgres -c "DROP DATABASE risk_audit;"
psql -h 47.93.140.34 -p 5433 -U postgres -c "CREATE DATABASE risk_audit OWNER risk;"
psql -h 47.93.140.34 -p 5433 -U risk -d risk_audit -f backend/sql/init.sql
```

## 后续表结构变更流程

1. 改 `backend/app/models/<model>.py`
2. `cd backend && alembic revision --autogenerate -m "<描述>"` 生成新迁移文件
3. 本地执行 `alembic upgrade head` 验证
4. **同步更新 `backend/sql/init.sql`**：在文件末尾追加新表/字段的 DDL，并把 `INSERT INTO alembic_version` 的版本号改为最新 revision
5. PR review 时确保 Alembic 迁移与 init.sql 描述一致
