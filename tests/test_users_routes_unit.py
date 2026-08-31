import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.routes import users
from app.models.user import User, Role
from app.schemas import UserUpdate
from app.routes.users import user_to_schema
from app.models.photo import Photo
from datetime import datetime

# --- get_user_profile ---
@pytest.mark.asyncio
async def test_get_user_profile_not_found(async_db_session: AsyncSession):
    current_user = User(id=1, username="u", email="u@u.com", role=Role.USER, hashed_password="fake")
    with pytest.raises(HTTPException) as exc:
        await users.get_user_profile(user_id=999, db=async_db_session, current_user=current_user)
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_get_user_profile_forbidden(async_db_session: AsyncSession):
    owner = User(id=1, username="o", email="o@o.com", role=Role.USER, hashed_password="fake")
    other = User(id=2, username="u", email="u@u.com", role=Role.USER, hashed_password="fake")
    async_db_session.add_all([owner, other]); await async_db_session.commit()
    with pytest.raises(HTTPException) as exc:
        await users.get_user_profile(user_id=owner.id, db=async_db_session, current_user=other)
    assert exc.value.status_code == 403

@pytest.mark.asyncio
async def test_get_user_profile_success_self(async_db_session: AsyncSession):
    owner = User(id=1, username="o", email="o@o.com", role=Role.USER, hashed_password="fake")
    async_db_session.add(owner); await async_db_session.commit(); await async_db_session.refresh(owner)
    result = await users.get_user_profile(user_id=owner.id, db=async_db_session, current_user=owner)
    assert result.username == "o"

@pytest.mark.asyncio
async def test_get_user_profile_success_admin(async_db_session: AsyncSession):
    owner = User(id=1, username="o", email="o@o.com", role=Role.USER, hashed_password="fake")
    admin = User(id=2, username="a", email="a@a.com", role=Role.ADMIN, hashed_password="fake")
    async_db_session.add_all([owner, admin]); await async_db_session.commit()
    result = await users.get_user_profile(user_id=owner.id, db=async_db_session, current_user=admin)
    assert result.username == "o"

# --- update_user_profile ---
@pytest.mark.asyncio
async def test_update_user_profile_not_found(async_db_session: AsyncSession):
    current_user = User(id=1, username="u", email="u@u.com", role=Role.USER, hashed_password="fake")
    async_db_session.add(current_user); await async_db_session.commit()
    with pytest.raises(HTTPException) as exc:
        await users.update_user_profile(user_id=999, update_data=UserUpdate(username="new"),
                                        db=async_db_session, current_user=current_user)
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_update_user_profile_forbidden(async_db_session: AsyncSession):
    owner = User(id=1, username="o", email="o@o.com", role=Role.USER, hashed_password="fake")
    other = User(id=2, username="u", email="u@u.com", role=Role.USER, hashed_password="fake")
    async_db_session.add_all([owner, other]); await async_db_session.commit()
    with pytest.raises(HTTPException) as exc:
        await users.update_user_profile(user_id=owner.id, update_data=UserUpdate(username="new"),
                                        db=async_db_session, current_user=other)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_update_user_profile_success(async_db_session: AsyncSession):
    owner = User(id=1, username="o", email="o@o.com", role=Role.USER, hashed_password="fake")
    async_db_session.add(owner); await async_db_session.commit(); await async_db_session.refresh(owner)
    result = await users.update_user_profile(user_id=owner.id, update_data=UserUpdate(username="new"),
                                             db=async_db_session, current_user=owner)
    assert result.username == "new"

# --- assign_role ---
@pytest.mark.asyncio
async def test_assign_role_not_found(async_db_session: AsyncSession):
    admin = User(id=1, username="a", email="a@a.com", role=Role.ADMIN, hashed_password="fake")
    with pytest.raises(HTTPException) as exc:
        await users.assign_role(user_id=999, new_role=Role.MODERATOR, db=async_db_session, current_user=admin)
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_assign_role_success_admin(async_db_session: AsyncSession):
    admin = User(id=1, username="a", email="a@a.com", role=Role.ADMIN, hashed_password="fake")
    user = User(id=2, username="u", email="u@u.com", role=Role.USER, hashed_password="fake")
    async_db_session.add_all([admin, user]); await async_db_session.commit()
    result = await users.assign_role(user_id=user.id, new_role=Role.MODERATOR, db=async_db_session, current_user=admin)
    assert result.role == "moderator"

# --- ban/unban ---
@pytest.mark.asyncio
async def test_ban_user_not_found(async_db_session: AsyncSession):
    admin = User(id=1, username="a", email="a@a.com", role=Role.ADMIN, hashed_password="fake")
    with pytest.raises(HTTPException) as exc:
        await users.ban_user(user_id=999, db=async_db_session, current_user=admin)
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_ban_user_success_admin(async_db_session: AsyncSession):
    admin = User(id=1, username="a", email="a@a.com", role=Role.ADMIN, hashed_password="fake")
    user = User(id=2, username="u", email="u@u.com", role=Role.USER, hashed_password="fake")
    async_db_session.add_all([admin, user]); await async_db_session.commit()
    result = await users.ban_user(user_id=user.id, db=async_db_session, current_user=admin)
    assert result.is_active is False

@pytest.mark.asyncio
async def test_unban_user_not_found(async_db_session: AsyncSession):
    admin = User(id=1, username="a", email="a@a.com", role=Role.ADMIN, hashed_password="fake")
    with pytest.raises(HTTPException) as exc:
        await users.unban_user(user_id=999, db=async_db_session, current_user=admin)
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_unban_user_success_admin(async_db_session: AsyncSession):
    admin = User(id=1, username="a", email="a@a.com", role=Role.ADMIN, hashed_password="fake")
    user = User(id=2, username="u", email="u@u.com", role=Role.USER, hashed_password="fake", is_active=False)
    async_db_session.add_all([admin, user]); await async_db_session.commit()
    result = await users.unban_user(user_id=user.id, db=async_db_session, current_user=admin)
    assert result.is_active is True

@pytest.mark.asyncio
async def test_user_to_schema_no_photos(async_db_session: AsyncSession):
    user = User(id=1, username="u", email="u@u.com", role=Role.USER, hashed_password="fake")
    async_db_session.add(user); await async_db_session.commit(); await async_db_session.refresh(user)

    result = await users.user_to_schema(async_db_session, user)
    assert result.photo_count == 0
    assert result.username == "u"

@pytest.mark.asyncio
async def test_user_to_schema_with_photos(async_db_session: AsyncSession):
    user = User(id=1, username="u", email="u@u.com", role=Role.USER, hashed_password="fake")
    async_db_session.add(user); await async_db_session.commit(); await async_db_session.refresh(user)

    photo = Photo(id=1, url="url", public_id="pid", user_id=user.id,
                  description="x", created_at=datetime.utcnow(), owner=user)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)

    result = await users.user_to_schema(async_db_session, user)
    assert result.photo_count == 1
    assert result.email == "u@u.com"

@pytest.mark.asyncio
async def test_update_user_profile_conflict(mocker, async_db_session: AsyncSession):
    owner = User(id=1, username="o", email="o@o.com", role=Role.USER, hashed_password="fake")
    async_db_session.add(owner)
    await async_db_session.commit()
    await async_db_session.refresh(owner)

    # мок саме commit у сесії
    mocker.patch.object(async_db_session, "commit", side_effect=IntegrityError("conflict", {}, None))

    with pytest.raises(HTTPException) as exc:
        await users.update_user_profile(
            user_id=owner.id,
            update_data=UserUpdate(username="dup"),
            db=async_db_session,
            current_user=owner
        )
    assert exc.value.status_code == 409