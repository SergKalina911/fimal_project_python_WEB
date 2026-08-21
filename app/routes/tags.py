from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.tag import Tag
from app.schemas import TagCreate, TagRead
from app.core.security import require_user, require_admin

router = APIRouter(prefix="/tags", tags=["Tags"])

@router.post("/", response_model=TagRead)
async def create_tag(
    tag: TagCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)   # 🔹 тільки адмін може створювати нові теги
):
    new_tag = Tag(name=tag.name)
    db.add(new_tag)
    await db.commit()
    await db.refresh(new_tag)
    return new_tag

@router.get("/", response_model=list[TagRead])
async def list_tags(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_user)   # 🔹 будь-який активний користувач може переглядати
):
    result = await db.execute(select(Tag))
    return result.scalars().all()
