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

预期：单元测试全部通过（test_config / test_main / test_security / test_llm_service / test_chat_stream_requires_auth / test_me_requires_token）。需要 DB + Redis 实际可用的集成测试在已启动后端依赖后亦应全部通过。

## 7. 常见问题

| 现象 | 检查 |
|------|------|
| 登录 500 | `.env` 的 `DATABASE_URL` 是否正确；`alembic upgrade head` 是否已执行 |
| 登录 401 | `SEED_ADMIN_PASSWORD` 与登录密码是否一致；admin 是否已种入（`SELECT * FROM users`） |
| 对话无响应 | `DEEPSEEK_API_KEY` 是否有效、是否欠费；查看后端日志 |
| 退出后旧 token 仍能访问 | Redis 是否启动；查看 `redis-cli keys 'jwt:blacklist:*'` |
