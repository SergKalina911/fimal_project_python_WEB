# app/services/cloudinary_service.py

import cloudinary
import cloudinary.uploader
import cloudinary.utils   # 🔹 для формування URL з трансформаціями
from app.core.config import settings

# --- Конфігурація Cloudinary ---
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)

def upload_image(file, folder: str = "photos") -> dict:
    """
    Завантажує файл у Cloudinary (звичайний UploadFile з FastAPI).
    Використовується при створенні фото користувачем.
    """
    result = cloudinary.uploader.upload(file.file, folder=folder)
    return {
        "secure_url": result.get("secure_url"),
        "public_id": result.get("public_id")
    }

def upload_bytes(buffer, folder: str = "photos") -> dict:
    """
    🔹 Новий метод: завантажує байти напряму (наприклад QR-код з BytesIO).
    Це прибирає костиль із UploadFile(file=qr_buffer).
    """
    result = cloudinary.uploader.upload(buffer, folder=folder)
    return {
        "secure_url": result.get("secure_url"),
        "public_id": result.get("public_id")
    }

def transform_image(public_id: str, transformation: list[dict]) -> str:
    """
    Формує URL для трансформованого фото через Cloudinary.
    Використовує public_id, щоб не вантажити фото повторно.
    """
    url, options = cloudinary.utils.cloudinary_url(
        public_id,
        transformation=transformation,
        secure=True
    )
    return url
