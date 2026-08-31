import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import app.routes.tags as tags   # ← правильний імпорт
from app.models.user import User, Role
from app.models.tag import Tag
from app.schemas import TagCreate

# --- create_tag ---
@pytest.mark.asyncio
async def test_create_tag_success(async_db_session: AsyncSession):
    admin = User(id=1, username="a", email="a@a.com", role=Role.ADMIN, hashed_password="fake")
    async_db_session.add(admin)
    await async_db_session.commit()
    await async_db_session.refresh(admin)

    body = TagCreate(name="tag1")
    result = await tags.create_tag(tag=body, db=async_db_session, current_user=admin)
    assert result.name == "tag1"

# --- list_tags ---
@pytest.mark.asyncio
async def test_list_tags_success(async_db_session: AsyncSession):
    user = User(id=1, username="u", email="u@u.com", role=Role.USER, hashed_password="fake")
    tag1 = Tag(id=1, name="t1")
    tag2 = Tag(id=2, name="t2")
    async_db_session.add_all([user, tag1, tag2])
    await async_db_session.commit()

    result = await tags.list_tags(db=async_db_session, current_user=user)
    assert len(result) == 2
    assert {t.name for t in result} == {"t1", "t2"}

# --- delete_tag ---
@pytest.mark.asyncio
async def test_delete_tag_forbidden(async_db_session: AsyncSession):
    user = User(id=1, username="u", email="u@u.com", role=Role.USER, hashed_password="fake")
    async_db_session.add(user)
    await async_db_session.commit()

    with pytest.raises(HTTPException) as exc:
        await tags.delete_tag(tag_id=1, db=async_db_session, current_user=user)
    assert exc.value.status_code == 403

@pytest.mark.asyncio
async def test_delete_tag_not_found(async_db_session: AsyncSession):
    admin = User(id=1, username="a", email="a@a.com", role=Role.ADMIN, hashed_password="fake")
    async_db_session.add(admin)
    await async_db_session.commit()

    with pytest.raises(HTTPException) as exc:
        await tags.delete_tag(tag_id=999, db=async_db_session, current_user=admin)
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_delete_tag_success(async_db_session: AsyncSession):
    admin = User(id=1, username="a", email="a@a.com", role=Role.ADMIN, hashed_password="fake")
    tag = Tag(id=1, name="t1")
    async_db_session.add_all([admin, tag])
    await async_db_session.commit()
    await async_db_session.refresh(tag)

    result = await tags.delete_tag(tag_id=tag.id, db=async_db_session, current_user=admin)
    assert "deleted" in result["detail"]
