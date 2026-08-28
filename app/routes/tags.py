from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_

from app.core.database import get_db
from app.models.tag import Tag, photo_tags
from app.models.user import User, Role
from app.schemas import TagCreate, TagRead
from app.core.security import require_user, require_admin

router = APIRouter(prefix="/tags", tags=["Tags"])

# --- створення тегу (тільки адмін) ---
@router.post("/", response_model=TagRead)
async def create_tag(
    tag: TagCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    new_tag = Tag(name=tag.name)
    db.add(new_tag)
    await db.commit()
    await db.refresh(new_tag)
    return TagRead.model_validate(new_tag)

# --- список тегів (будь-який активний користувач) ---
@router.get("/", response_model=list[TagRead])
async def list_tags(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    result = await db.execute(select(Tag))
    tags = result.scalars().all()
    return [TagRead.model_validate(tag) for tag in tags]

# --- видалення тегу з глобальної таблиці (тільки адмін) ---
@router.delete("/{tag_id}", response_model=dict)
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can delete tags")

    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalars().first()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    await db.execute(photo_tags.delete().where(photo_tags.c.tag_id == tag_id))
    await db.delete(tag)
    await db.commit()
    db.expire_all()   # 🔹 очищаємо кеш

    return {"detail": f"Tag {tag.name} (id={tag_id}) deleted"}
