# app/services/cloudinary_service.py

import cloudinary
import cloudinary.uploader
import cloudinary.utils   # 🔹 додано для формування URL з трансформаціями
from app.core.config import settings

# Конфігурація Cloudinary через settings
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)

def upload_image(file, folder: str = "photos") -> str:
    """Завантажує файл у Cloudinary та повертає secure_url"""
    result = cloudinary.uploader.upload(file.file, folder=folder)
    return result.get("secure_url")

def transform_image(public_id: str, transformation: list[dict]) -> str:
    """
    Формує URL для трансформованого фото через Cloudinary (без повторного завантаження).
    :param public_id: унікальний public_id фото в Cloudinary
    :param transformation: список трансформацій (dict), напр. [{"width":300,"height":300,"crop":"fill"}]
    :return: трансформований URL
    """
    # 🔹 Замість повторного upload використовуємо build_url
    url, options = cloudinary.utils.cloudinary_url(
        public_id,
        transformation=transformation,
        secure=True
    )
    return url
