import pytest
from datetime import timedelta, datetime, UTC
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    is_refresh_token,
)

def test_password_hash_and_verify_success_and_fail():
    password = "secret"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)

def test_access_token_valid():
    token = create_access_token(user_id=123)
    payload = decode_token(token)
    assert payload["sub"] == "123"
    assert payload["type"] == "access"

def test_refresh_token_valid():
    token = create_refresh_token(user_id=456)
    payload = decode_token(token)
    assert payload["sub"] == "456"
    assert payload["type"] == "refresh"
    assert is_refresh_token(token)

def test_invalid_token_returns_none():
    payload = decode_token("invalid.token.value")
    assert payload is None

def test_expired_access_token():
    # створюємо токен з минулим часом
    expire = datetime.now(UTC) - timedelta(seconds=1)
    to_encode = {"sub": "789", "exp": expire, "type": "access"}
    from jose import jwt
    token = jwt.encode(to_encode, "supersecret", algorithm="HS256")
    payload = decode_token(token)
    # decode_token повертає None для простроченого токена
    assert payload is None
