from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.user import User, Role
from app.schemas import UserRead, UserUpdate
from app.core.security import require_admin, require_user

router = APIRouter(prefix="/users", tags=["Users"])

# --- перегляд профілю по id ---
@router.get("/{user_id}", response_model=UserRead)
async def get_user_profile(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 🔹 дозволяємо переглядати лише свій профіль або якщо користувач — адмін
    if user.id != current_user.id and current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return user


# --- оновлення профілю по id ---
@router.put("/{user_id}", response_model=UserRead)
async def update_user_profile(
    user_id: int,
    update_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 🔹 користувач може оновлювати лише свій профіль, адмін — будь‑який
    if user.id != current_user.id and current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(user, field, value)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# --- призначення ролі (тільки адмін) ---
@router.put("/{user_id}/role", response_model=UserRead)
async def assign_role(
    user_id: int,
    new_role: Role,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)   # 🔹 тільки адмін
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = new_role
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
