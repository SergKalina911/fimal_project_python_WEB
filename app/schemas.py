from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

# --- User ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserRead(UserBase):
    id: int
    email: str
    role: str
    is_active: bool
    photo_count: int | None = None   # 🔹 кількість фото користувача

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    # 🔹 інші поля можна додати за потреби


# --- Tag ---
class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagRead(TagBase):
    id: int

    class Config:
        from_attributes = True


# --- Comment ---
class CommentBase(BaseModel):
    text: str

class CommentCreate(CommentBase):
    photo_id: int

class CommentRead(CommentBase):
    id: int
    photo_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]   # 🔹 дозволяємо None

    class Config:
        from_attributes = True

class CommentUpdate(BaseModel):   # 🔹 нова схема для PUT
    text: str


# --- Photo ---
class PhotoBase(BaseModel):
    url: str
    description: Optional[str] = None

class PhotoCreate(PhotoBase):
    user_id: int
    tag_ids: Optional[List[int]] = []


# --- PhotoTransform ---
class PhotoTransformRead(BaseModel):
    id: int
    photo_id: int
    transformed_url: str
    qr_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PhotoRead(PhotoBase):
    id: int
    user_id: int
    status: str
    tags: List[TagRead] = []
    transforms: List[PhotoTransformRead] = []
    comments: List[CommentRead] = []   # 🔹 список коментарів з таймстемпами
    owner: UserRead | None = None      # 🔹 власник фото

    class Config:
        from_attributes = True


# --- Token ---
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# --- Допоміжна схема для прив’язки тегів ---
class TagAttach(BaseModel):
    tag_ids: List[int]
