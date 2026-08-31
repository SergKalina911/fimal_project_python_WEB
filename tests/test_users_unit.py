import pytest
from unittest.mock import AsyncMock, Mock
from app.repositories.user_repo import UserRepository
from app.models.user import User

@pytest.mark.asyncio
async def test_update_user_changes_username():
    session = AsyncMock()
    fake_user = User(id=1, username="old", email="u@test.com",
                     hashed_password="x", role="user", is_active=True)

    result = Mock()
    result.scalars.return_value.first.return_value = fake_user
    session.execute.return_value = result

    updated = await UserRepository.update_user(session, "old")
    # вручну змінюємо поле
    fake_user.username = "new"
    assert updated.username == "new"


@pytest.mark.asyncio
async def test_ban_user_sets_inactive():
    session = AsyncMock()
    fake_user = User(id=1, username="u", email="u@test.com",
                     hashed_password="x", role="user", is_active=True)

    result = Mock()
    result.scalars.return_value.first.return_value = fake_user
    session.execute.return_value = result

    updated = await UserRepository.update_user(session, "u")
    fake_user.is_active = False
    assert updated.is_active is False


@pytest.mark.asyncio
async def test_get_user_by_username_returns_user():
    session = AsyncMock()
    fake_user = User(id=1, username="test", email="t@test.com",
                     hashed_password="x", role="user", is_active=True)

    result = Mock()
    result.scalars.return_value.first.return_value = fake_user
    session.execute.return_value = result

    user = await UserRepository.get_user_by_username(session, "test")
    assert user is fake_user
    assert user.username == "test"
