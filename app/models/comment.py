from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy.sql import func

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    photo_id = Column(Integer, ForeignKey("photos.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # час створення — завжди обов’язковий
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # час редагування — дефолт при створенні, автоматично оновлюється при UPDATE
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    photo = relationship("Photo", back_populates="comments", lazy="selectin")
    user = relationship("User", back_populates="comments", lazy="selectin")
