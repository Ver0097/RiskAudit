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
