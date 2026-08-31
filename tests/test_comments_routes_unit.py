import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.routes import comments
from app.models.user import User, Role
from app.models.photo import Photo
from app.models.comment import Comment
from app.schemas import CommentCreate, CommentUpdate
from datetime import datetime

# --- create_comment ---
@pytest.mark.asyncio
async def test_create_comment_photo_not_found(async_db_session: AsyncSession):
    user = User(id=1, username="user", email="u@u.com", role=Role.USER)
    dto = CommentCreate(text="hello", photo_id=999)
    with pytest.raises(HTTPException):
        await comments.create_comment(comment=dto, db=async_db_session, current_user=user)

@pytest.mark.asyncio
async def test_create_comment_success_user(async_db_session: AsyncSession):
    photo = Photo(id=1, url="url", public_id="pid", user_id=1)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)
    user = User(id=1, username="user", email="u@u.com", role=Role.USER)
    dto = CommentCreate(text="hello", photo_id=1)
    result = await comments.create_comment(comment=dto, db=async_db_session, current_user=user)
    assert any(c.text == "hello" for c in result.comments)

@pytest.mark.asyncio
async def test_create_comment_success_moderator(async_db_session: AsyncSession):
    photo = Photo(id=1, url="url", public_id="pid", user_id=1)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)
    user = User(id=2, username="mod", email="m@m.com", role=Role.MODERATOR)
    dto = CommentCreate(text="mod says hi", photo_id=1)
    result = await comments.create_comment(comment=dto, db=async_db_session, current_user=user)
    assert any(c.text == "mod says hi" for c in result.comments)

# --- get_comment ---
@pytest.mark.asyncio
async def test_get_comment_not_found(async_db_session: AsyncSession):
    user = User(id=1, username="user", email="u@u.com", role=Role.USER)
    with pytest.raises(HTTPException):
        await comments.get_comment(comment_id=999, db=async_db_session, current_user=user)

@pytest.mark.asyncio
async def test_get_comment_success(async_db_session: AsyncSession):
    comment = Comment(id=1, text="hello", user_id=1, photo_id=1)
    async_db_session.add(comment); await async_db_session.commit(); await async_db_session.refresh(comment)
    user = User(id=1, username="user", email="u@u.com", role=Role.USER)
    result = await comments.get_comment(comment_id=1, db=async_db_session, current_user=user)
    assert result.text == "hello"

# --- update_comment ---
@pytest.mark.asyncio
async def test_update_comment_forbidden_user(async_db_session: AsyncSession):
    comment = Comment(id=1, text="old", user_id=2, photo_id=1)
    async_db_session.add(comment); await async_db_session.commit(); await async_db_session.refresh(comment)
    user = User(id=1, username="user", email="u@u.com", role=Role.USER)
    dto = CommentUpdate(text="new text")
    with pytest.raises(HTTPException):
        await comments.update_comment(comment_id=1, update=dto,
                                      db=async_db_session, current_user=user)

@pytest.mark.asyncio
async def test_update_comment_success_owner(async_db_session: AsyncSession):
    comment = Comment(id=1, text="old", user_id=1, photo_id=1)
    async_db_session.add(comment); await async_db_session.commit(); await async_db_session.refresh(comment)
    user = User(id=1, username="user", email="u@u.com", role=Role.USER)
    dto = CommentUpdate(text="new text")
    result = await comments.update_comment(comment_id=1, update=dto,
                                           db=async_db_session, current_user=user)
    assert result.text == "new text"

# -- update_comment_success_moderator ---
@pytest.mark.asyncio
async def test_update_comment_success_moderator(async_db_session: AsyncSession):
    # модератор редагує свій коментар
    moderator = User(id=2, username="mod", email="m@m.com", role=Role.MODERATOR, hashed_password="fake")
    async_db_session.add(moderator); await async_db_session.commit(); await async_db_session.refresh(moderator)

    comment = Comment(id=1, text="old", user_id=moderator.id, photo_id=1)
    async_db_session.add(comment); await async_db_session.commit(); await async_db_session.refresh(comment)

    dto = CommentUpdate(text="mod updated")
    result = await comments.update_comment(comment_id=1, update=dto,
                                           db=async_db_session, current_user=moderator)
    assert result.text == "mod updated"

# --- delete_comment ---
@pytest.mark.asyncio
async def test_delete_comment_not_found(async_db_session: AsyncSession):
    user = User(id=1, username="admin", email="a@a.com", role=Role.ADMIN)
    with pytest.raises(HTTPException):
        await comments.delete_comment(comment_id=999, db=async_db_session, current_user=user)

@pytest.mark.asyncio
async def test_delete_comment_forbidden_user(async_db_session: AsyncSession):
    comment = Comment(id=1, text="test", user_id=2, photo_id=1)
    async_db_session.add(comment); await async_db_session.commit(); await async_db_session.refresh(comment)
    user = User(id=1, username="user", email="u@u.com", role=Role.USER)
    with pytest.raises(HTTPException):
        await comments.delete_comment(comment_id=1, db=async_db_session, current_user=user)

@pytest.mark.asyncio
async def test_delete_comment_success_admin(async_db_session: AsyncSession):
    comment = Comment(id=1, text="test", user_id=2, photo_id=1)
    async_db_session.add(comment); await async_db_session.commit(); await async_db_session.refresh(comment)
    user = User(id=1, username="admin", email="a@a.com", role=Role.ADMIN)
    result = await comments.delete_comment(comment_id=1, db=async_db_session, current_user=user)
    assert "deleted successfully" in result["detail"]

# --- delete_comment_success_moderator ---
@pytest.mark.asyncio
async def test_delete_comment_success_moderator(async_db_session: AsyncSession):
    user = User(id=5, username="user", email="u@u.com", role=Role.USER, hashed_password="fake")
    async_db_session.add(user); await async_db_session.commit(); await async_db_session.refresh(user)

    comment = Comment(id=1, text="test", user_id=user.id, photo_id=1, user=user)
    async_db_session.add(comment); await async_db_session.commit(); await async_db_session.refresh(comment)

    moderator = User(id=2, username="mod", email="m@m.com", role=Role.MODERATOR, hashed_password="fake")
    async_db_session.add(moderator); await async_db_session.commit(); await async_db_session.refresh(moderator)

    result = await comments.delete_comment(comment_id=1, db=async_db_session, current_user=moderator)
    assert "deleted successfully" in result["detail"]

# --- delete_comment_forbidden_moderator_on_admin ---
@pytest.mark.asyncio
async def test_delete_comment_forbidden_moderator_on_admin(async_db_session: AsyncSession):
    admin = User(id=10, username="admin", email="a@a.com", role=Role.ADMIN, hashed_password="fake")
    async_db_session.add(admin); await async_db_session.commit(); await async_db_session.refresh(admin)

    comment = Comment(id=1, text="admin says", user_id=admin.id, photo_id=1, user=admin)
    async_db_session.add(comment); await async_db_session.commit(); await async_db_session.refresh(comment)

    moderator = User(id=2, username="mod", email="m@m.com", role=Role.MODERATOR, hashed_password="fake")
    async_db_session.add(moderator); await async_db_session.commit(); await async_db_session.refresh(moderator)

    with pytest.raises(HTTPException) as exc:
        await comments.delete_comment(comment_id=1, db=async_db_session, current_user=moderator)
    assert exc.value.status_code == 403

# --- update_comment ---
@pytest.mark.asyncio
async def test_update_comment_not_found(async_db_session: AsyncSession):
    user = User(id=1, username="user", email="u@u.com", role=Role.USER, hashed_password="fake")
    dto = CommentUpdate(text="new text")
    # коментар з таким ID не існує → очікуємо 404
    with pytest.raises(HTTPException) as exc:
        await comments.update_comment(comment_id=999, update=dto,
                                      db=async_db_session, current_user=user)
    assert exc.value.status_code == 404
