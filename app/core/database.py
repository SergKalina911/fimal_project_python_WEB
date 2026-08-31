"""
Файл для налаштування бази даних та створення асинхронного сеансу SQLAlchemy. Використовується для
взаємодії з базою даних у FastAPI додатку.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Асинхронний engine
engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)

# Session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# Базовий клас для моделей
Base = declarative_base()

# Dependency для FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Ініціалізація (викликається у main.py)
def init_db():
    pass  # Alembic керує схемою
