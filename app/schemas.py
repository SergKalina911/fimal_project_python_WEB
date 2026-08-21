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

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    # 🔹 інші поля можна додати за потреби
    # is_active: Optional[bool] = None   # тільки для адміна
    # description: Optional[str] = None  # якщо треба додати поле опису

# --- Tag ---
class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagRead(TagBase):
    id: int

    class Config:
        from_attributes = True


# --- Photo ---
class PhotoBase(BaseModel):
    url: str
    description: Optional[str] = None

class PhotoCreate(PhotoBase):
    user_id: int
    # тут краще одразу приймати список id тегів
    tag_ids: Optional[List[int]] = []

class PhotoRead(PhotoBase):
    id: int
    user_id: int
    status: str   # 🔹 додано, щоб відображати статус фото
    tags: List[TagRead] = []   # список тегів, які прив’язані до фото
    

    class Config:
        from_attributes = True


# --- Comment ---
class CommentBase(BaseModel):
    text: str

class CommentCreate(CommentBase):
    photo_id: int
    # user_id: int

class CommentRead(CommentBase):
    id: int
    photo_id: int
    user_id: int

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
