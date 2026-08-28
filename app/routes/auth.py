from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User, Role
from app.schemas import UserCreate, UserLogin, Token, UserRead   # 🔹 ЗМІНА: додано UserRead

router = APIRouter(prefix="/auth", tags=["Auth"])

# --- реєстрація ---
@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(body: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.role == Role.ADMIN))
    admin_exists = result.scalars().first()
    role = Role.ADMIN if not admin_exists else Role.USER

    hashed_password = get_password_hash(body.password)
    new_user = User(
        username=body.username,
        email=body.email,
        hashed_password=hashed_password,
        role=role
    )
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="User already exists")

    access_token = create_access_token(new_user.id)
    refresh_token = create_refresh_token(new_user.id)

    # 🔹 ЗМІНА: повертаємо DTO Token
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

# --- логін ---
@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive or banned")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    # 🔹 ЗМІНА: повертаємо DTO Token
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

