# tests/conftest.py
import pytest
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.database import Base

# ✅ Підтягуємо тестове середовище з .env.test
load_dotenv(".env.test")

# ✅ In-memory SQLite для модульних тестів
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(autouse=True)
async def setup_db():
    """Створюємо таблиці перед кожним тестом і дропаємо після."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def async_db_session():
    """Фікстура для роботи з асинхронною сесією БД."""
    async with TestingSessionLocal() as session:
        yield session

# ✅ Моки для зовнішніх сервісів (Cloudinary, QR)
@pytest.fixture(autouse=True)
def mock_services(monkeypatch):
    monkeypatch.setattr(
        "app.services.cloudinary_service.upload_image",
        lambda f, folder="photos": {"secure_url": "http://fake/url.jpg", "public_id": "fake123"}
    )
    monkeypatch.setattr(
        "app.services.cloudinary_service.upload_bytes",
        lambda b, folder="qr_codes": {"secure_url": "http://fake/qr.png", "public_id": "qr123"}
    )
    monkeypatch.setattr(
        "app.services.cloudinary_service.transform_image",
        lambda pid, transformation: f"http://fake/transformed/{pid}.jpg"
    )
    monkeypatch.setattr(
        "app.services.qr_service.QRService.generate_qr",
        lambda d, **kwargs: b"fake_qr_bytes"
    )
