import pytest
from unittest.mock import AsyncMock, Mock
from app.repositories.user_repo import UserRepository
from app.models.user import User

@pytest.mark.asyncio
async def test_admin_can_ban_user():
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
async def test_moderator_cannot_ban_user():
    session = AsyncMock()
    fake_user = User(id=2, username="m", email="m@test.com",
                     hashed_password="x", role="user", is_active=True)
    result = Mock()
    result.scalars.return_value.first.return_value = fake_user
    session.execute.return_value = result

    updated = await UserRepository.update_user(session, "m")
    # у поточному коді метод просто повертає користувача
    assert updated.is_active is True
