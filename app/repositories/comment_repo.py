from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.comment import Comment

class CommentRepository:
    @staticmethod
    async def create_comment(session: AsyncSession, text: str, photo_id: int, user_id: int):
        comment = Comment(text=text, photo_id=photo_id, user_id=user_id)
        session.add(comment)
        await session.commit()
        await session.refresh(comment)
        return comment

    @staticmethod
    async def get_comment_by_id(session: AsyncSession, comment_id: int):
        result = await session.execute(select(Comment).where(Comment.id == comment_id))
        return result.scalars().first()

    @staticmethod
    async def get_comments_by_photo(session: AsyncSession, photo_id: int):
        result = await session.execute(select(Comment).where(Comment.photo_id == photo_id))
        return result.scalars().all()

    @staticmethod
    async def update_comment_text(session: AsyncSession, comment_id: int, new_text: str):
        comment = await CommentRepository.get_comment_by_id(session, comment_id)
        if not comment:
            return None
        comment.text = new_text
        session.add(comment)
        await session.commit()
        await session.refresh(comment)
        return comment

    @staticmethod
    async def delete_comment(session: AsyncSession, comment_id: int):
        comment = await CommentRepository.get_comment_by_id(session, comment_id)
        if not comment:
            return None
        await session.delete(comment)
        await session.commit()
        return comment
