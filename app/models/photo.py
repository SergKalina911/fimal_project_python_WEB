""" 
Файл для визначення моделі фото у базі даних. Містить клас Photo, який описує структуру
таблиці фото та її зв’язки з іншими моделями (User, Tag, Comment, PhotoTransform).
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.tag import photo_tags
from sqlalchemy.sql import func

photo_status_enum = Enum(
    "new", "moderation", "approved", "rejected",
    name="photo_status",
    native_enum=True,
    create_constraint=True
)

class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    public_id = Column(String, nullable=False)   # 🔹 тепер NOT NULL
    description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    status = Column(photo_status_enum, default="new", nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # 🔹 зв’язки з каскадом
    owner = relationship("User", back_populates="photos", lazy="selectin")
    tags = relationship("Tag", secondary=photo_tags, back_populates="photos", lazy="selectin")
    comments = relationship(
        "Comment",
        back_populates="photo",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin"
    )
    transforms = relationship(
        "PhotoTransform",
        back_populates="photo",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin"
    )


class PhotoTransform(Base):
    __tablename__ = "photo_transforms"

    id = Column(Integer, primary_key=True, index=True)
    photo_id = Column(Integer, ForeignKey("photos.id", ondelete="CASCADE"), nullable=False)
    transformed_url = Column(String, nullable=False)
    qr_url = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    photo = relationship("Photo", back_populates="transforms", lazy="selectin")
