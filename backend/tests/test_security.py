import time
import pytest
from app.core import security


def test_hash_and_verify_password():
    """密码哈希与校验需正确处理正确与错误密码。"""
    h = security.hash_password("S3cret!")
    assert h != "S3cret!"
    assert security.verify_password("S3cret!", h) is True
    assert security.verify_password("wrong", h) is False


def test_create_and_decode_access_token():
    """access token 应携带 sub/type/jti/exp 等关键字段。"""
    token = security.create_access_token(subject="alice", ttl_minutes=5)
    payload = security.decode_token(token)
    assert payload["sub"] == "alice"
    assert payload["type"] == "access"
    assert "jti" in payload
    assert "exp" in payload


def test_decode_invalid_token_raises():
    """非法 token 解码必须抛出 InvalidTokenError。"""
    with pytest.raises(security.InvalidTokenError):
        security.decode_token("not.a.jwt")


def test_token_expiry_enforced(monkeypatch):
    """已过期 token 应抛 InvalidTokenError。"""
    token = security.create_access_token(subject="bob", ttl_minutes=-1)
    with pytest.raises(security.InvalidTokenError):
        security.decode_token(token)
