from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy.sql import func
class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    photo_id = Column(Integer, ForeignKey("photos.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Зв’язки
    photo = relationship("Photo", back_populates="comments", lazy="selectin")
    user = relationship("User", back_populates="comments", lazy="selectin")
