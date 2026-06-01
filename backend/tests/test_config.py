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
