import pytest
from app.repositories.comment_repo import CommentRepository
from app.models.comment import Comment

@pytest.mark.asyncio
async def test_create_comment_sets_timestamps(async_db_session):
    comment = await CommentRepository.create_comment(async_db_session, text="Nice!", photo_id=1, user_id=1)
    assert isinstance(comment, Comment)
    assert comment.text == "Nice!"
    assert comment.photo_id == 1
    assert comment.user_id == 1
    assert hasattr(comment, "created_at")
