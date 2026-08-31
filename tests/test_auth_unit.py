import pytest
from app.models.user import User, Role
from app.core.security import create_access_token, verify_password, get_password_hash

@pytest.mark.asyncio
async def test_create_first_user_is_admin(async_db_session):
    user = User(username="admin", email="admin@test.com",
                hashed_password=get_password_hash("secret"),
                role=Role.ADMIN, is_active=True)
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    assert user.role == Role.ADMIN
    assert user.email == "admin@test.com"

@pytest.mark.asyncio
async def test_check_user_credentials_ok(async_db_session):
    user = User(username="test", email="test@test.com",
                hashed_password=get_password_hash("secret"),
                role=Role.USER, is_active=True)
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    assert verify_password("secret", user.hashed_password)

def test_access_token_contains_user_id():
    token = create_access_token(user_id=1)
    assert isinstance(token, str)
    assert "ey" in token
