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
