""" User routes """

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.models.user import User, Role
from app.models.photo import Photo
from app.schemas import UserRead, UserUpdate
from app.core.security import require_admin, require_user

router = APIRouter(prefix="/users", tags=["Users"])

# --- хелпер для формування відповіді ---
async def user_to_schema(db: AsyncSession, user: User) -> UserRead:
    photos = (await db.execute(select(Photo).where(Photo.user_id == user.id))).scalars().all()
    # 🔹 ЗМІНА: формуємо DTO через UserRead
    return UserRead.model_validate({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value if hasattr(user.role, "value") else user.role,
        "is_active": user.is_active,
        "photo_count": len(photos),
    })

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

    if user.id != current_user.id and current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 🔹 ЗМІНА
    return await user_to_schema(db, user)

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

    if user.id != current_user.id and current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(user, field, value)

    try:   # 🔹 ЗМІНА: обробка IntegrityError
        db.add(user)
        await db.commit()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Username already exists")

    # 🔹 ЗМІНА
    return await user_to_schema(db, user)

# --- призначення ролі (тільки адмін) ---
@router.put("/{user_id}/role", response_model=UserRead)
async def assign_role(
    user_id: int,
    new_role: Role,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = new_role
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 🔹 ЗМІНА
    return await user_to_schema(db, user)

# --- бан користувача (тільки адмін) ---
@router.put("/{user_id}/ban", response_model=UserRead)
async def ban_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 🔹 ЗМІНА
    return await user_to_schema(db, user)

# --- розбан користувача (тільки адмін) ---
@router.put("/{user_id}/unban", response_model=UserRead)
async def unban_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 🔹 ЗМІНА
    return await user_to_schema(db, user)
