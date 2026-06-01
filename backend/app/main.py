from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth as auth_router
from app.config import get_settings


def create_app() -> FastAPI:
    """构建 FastAPI 应用实例并完成中间件 / 路由注册。"""
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
