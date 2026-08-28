
""" Comment routes """

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from datetime import datetime

from app.core.database import get_db
from app.models.photo import Photo
from app.models.comment import Comment
from app.models.user import User, Role
from app.schemas import CommentCreate, CommentRead, CommentUpdate, PhotoRead
from app.core.security import require_user

router = APIRouter(prefix="/comments", tags=["Comments"])

# --- створення коментаря ---
@router.post("/", response_model=PhotoRead)
async def create_comment(
    comment: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    result = await db.execute(select(Photo).where(Photo.id == comment.photo_id))
    photo = result.scalars().first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    new_comment = Comment(
        text=comment.text,
        photo_id=comment.photo_id,
        user_id=current_user.id,
        created_at=datetime.utcnow()
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    db.expire_all()

    result = await db.execute(
        select(Photo).options(
            joinedload(Photo.tags),
            joinedload(Photo.transforms),
            joinedload(Photo.comments),
            joinedload(Photo.owner)
        ).where(Photo.id == comment.photo_id)
    )
    photo_with_relations = result.scalars().first()
    return PhotoRead.model_validate(photo_with_relations)


# --- отримати коментар ---
@router.get("/{comment_id}", response_model=CommentRead)
async def get_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return CommentRead.model_validate(comment)


# --- редагування коментаря (тільки автор) ---
@router.put(
    "/{comment_id}",
    response_model=CommentRead,
    description="Редагує коментар. Доступно лише автору коментаря."
)
async def update_comment(
    comment_id: int,
    update: CommentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    comment.text = update.text
    comment.updated_at = datetime.utcnow()
    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    # 🔹 Повертаємо саме оновлений коментар
    return CommentRead.model_validate(comment)



# --- видалення коментаря ---
@router.delete(
    "/{comment_id}",
    response_model=dict,
    description="Видаляє коментар. Доступно лише модератору або адміну."
)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    # 🔹 за ТЗ: видаляти можуть тільки модератор або адмін
    if current_user.role not in [Role.ADMIN, Role.MODERATOR]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    await db.delete(comment)
    await db.commit()

    # 🔹 Повертаємо просте повідомлення
    return {"detail": f"Comment {comment_id} deleted successfully"}
