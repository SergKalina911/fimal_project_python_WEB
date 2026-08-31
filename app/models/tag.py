"""
Файл для визначення моделі тегу у базі даних. Містить клас Tag, який описує структуру
таблиці тегів та її зв’язки з іншими моделями (Photo).
"""

from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.core.database import Base

# Проміжна таблиця для many-to-many
photo_tags = Table(
    "photo_tags",
    Base.metadata,
    Column("photo_id", Integer, ForeignKey("photos.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    # Зв’язки
    photos = relationship("Photo", secondary=photo_tags, back_populates="tags", lazy="selectin")
