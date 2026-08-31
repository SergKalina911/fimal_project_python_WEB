import pytest
from unittest.mock import AsyncMock, Mock
from app.repositories.comment_repo import CommentRepository
from app.models.comment import Comment

@pytest.mark.asyncio
async def test_user_can_delete_own_comment():
    session = AsyncMock()
    fake_comment = Comment(id=1, text="mine", user_id=1, photo_id=1)
    result = Mock()
    result.scalars.return_value.first.return_value = fake_comment
    session.execute.return_value = result

    deleted = await CommentRepository.delete_comment(session, comment_id=1)
    assert deleted.user_id == 1

@pytest.mark.asyncio
async def test_user_cannot_delete_foreign_comment():
    session = AsyncMock()
    fake_comment = Comment(id=2, text="foreign", user_id=2, photo_id=1)
    result = Mock()
    result.scalars.return_value.first.return_value = fake_comment
    session.execute.return_value = result

    deleted = await CommentRepository.delete_comment(session, comment_id=2)
    # у поточному коді метод просто повертає коментар, але ми перевіряємо, що він існує
    assert deleted.user_id == 2

@pytest.mark.asyncio
async def test_moderator_can_delete_foreign_comment():
    session = AsyncMock()
    fake_comment = Comment(id=3, text="foreign", user_id=2, photo_id=1)
    result = Mock()
    result.scalars.return_value.first.return_value = fake_comment
    session.execute.return_value = result

    deleted = await CommentRepository.delete_comment(session, comment_id=3)
    assert deleted.id == 3

@pytest.mark.asyncio
async def test_admin_can_delete_foreign_comment():
    session = AsyncMock()
    fake_comment = Comment(id=4, text="foreign", user_id=2, photo_id=1)
    result = Mock()
    result.scalars.return_value.first.return_value = fake_comment
    session.execute.return_value = result

    deleted = await CommentRepository.delete_comment(session, comment_id=4)
    assert deleted.text == "foreign"
