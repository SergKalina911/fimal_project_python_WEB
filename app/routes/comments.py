from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.photo import Photo

from app.core.database import get_db
from app.models.comment import Comment
from app.models.user import User
from app.schemas import CommentRead, CommentCreate
from app.core.security import require_user, require_moderator

router = APIRouter(prefix="/comments", tags=["Comments"])

# --- створення коментаря (будь-який активний користувач) ---
@router.post("/", response_model=CommentRead)
async def create_comment(
    comment: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)   # 🔹 будь-який активний користувач
):
    # 🔹 Перевірка існування фото
    result = await db.execute(select(Photo).where(Photo.id == comment.photo_id))
    photo = result.scalars().first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    new_comment = Comment(
        text=comment.text,
        photo_id=comment.photo_id,
        user_id=current_user.id
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment

# --- отримати коментар (будь-який активний користувач) ---
@router.get("/{comment_id}", response_model=CommentRead)
async def get_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)   # 🔹 будь-який активний користувач
):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment

# --- видалення коментаря (модератор або адмін) ---
@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_moderator)   # 🔹 модератор або адмін
):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    await db.delete(comment)
    await db.commit()
    return {"detail": "Comment deleted"}
