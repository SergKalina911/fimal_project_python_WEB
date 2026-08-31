"""
Конфігураційний файл для FastAPI додатку з використанням Pydantic Settings. Для зручності, всі
змінні середовища зберігаються у файлі .env.
"""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    DATABASE_URL: str
    SYNC_DATABASE_URL: str

    # JWT
    SECRET_KEY: str = "supersecret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Email
    EMAIL_HOST: str
    EMAIL_PORT: int = 465
    EMAIL_HOST_USER: str
    EMAIL_HOST_PASSWORD: str

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # App
    APP_PORT: int = 8000

    class Config:
        env_file = ".env"
        extra = "ignore"   # дозволяємо зайві змінні

settings = Settings()
