from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime, ForeignKey, Table


import enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.tag import photo_tags
from sqlalchemy.sql import func

# ENUM значення одразу в нижньому регістрі
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
    description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    status = Column(
        photo_status_enum,
        default="new",   # дефолт теж у нижньому регістрі
        nullable=False
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Зв’язки
    owner = relationship("User", back_populates="photos", lazy="selectin")
    tags = relationship("Tag", secondary=photo_tags, back_populates="photos", lazy="selectin")
    comments = relationship("Comment", back_populates="photo", lazy="selectin")
