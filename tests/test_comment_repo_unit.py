import pytest
from app.repositories.comment_repo import CommentRepository
from app.models.comment import Comment

@pytest.mark.asyncio
async def test_create_comment_success(async_db_session):
    comment = await CommentRepository.create_comment(async_db_session, "Nice!", photo_id=1, user_id=1)
    assert isinstance(comment, Comment)
    assert comment.text == "Nice!"

@pytest.mark.asyncio
async def test_get_comment_by_id_not_found(async_db_session):
    comment = await CommentRepository.get_comment_by_id(async_db_session, 999)
    assert comment is None

@pytest.mark.asyncio
async def test_update_comment_text_not_found(async_db_session):
    updated = await CommentRepository.update_comment_text(async_db_session, 999, "Updated")
    assert updated is None

@pytest.mark.asyncio
async def test_delete_comment_not_found(async_db_session):
    deleted = await CommentRepository.delete_comment(async_db_session, 999)
    assert deleted is None
