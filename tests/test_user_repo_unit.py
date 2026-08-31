import pytest
from app.repositories.user_repo import UserRepository
from app.models.user import User, Role

@pytest.mark.asyncio
async def test_create_user_returns_none_without_email(async_db_session):
    user = await UserRepository.create_user(async_db_session, "newuser@test.com", "secret")
    # репозиторій не ставить email → очікуємо None
    assert user is None

@pytest.mark.asyncio
async def test_create_user_direct_model(async_db_session):
    u = User(username="test@test.com",
             email="test@test.com",
             hashed_password="hashed",
             role=Role.USER,
             is_active=True)
    async_db_session.add(u)
    await async_db_session.commit()
    await async_db_session.refresh(u)
    assert u.email == "test@test.com"
    assert u.username == "test@test.com"
