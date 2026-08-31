""" 
Файл для визначення репозиторію фотографій у базі даних. Містить клас PhotoRepository, який надає
методи для створення, отримання, оновлення та видалення фотографій. Використовує SQLAlchemy для
взаємодії з базою даних та асинхронні сесії для ефективного виконання запитів. Методи огорнуті
у статичні методи, що дозволяє викликати їх без створення екземпляру класу.  
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.photo import Photo

class PhotoRepository:
    @staticmethod
    async def create_photo(session: AsyncSession, url: str, description: str, user_id: int):
        photo = Photo(url=url, description=description, user_id=user_id)
        session.add(photo)
        await session.commit()
        await session.refresh(photo)
        return photo

    @staticmethod
    async def get_photo_by_id(session: AsyncSession, photo_id: int):
        result = await session.execute(select(Photo).where(Photo.id == photo_id))
        return result.scalars().first()

    @staticmethod
    async def get_photos_by_user(session: AsyncSession, user_id: int):
        result = await session.execute(select(Photo).where(Photo.user_id == user_id))
        return result.scalars().all()

    @staticmethod
    async def update_photo_description(session: AsyncSession, photo_id: int, description: str):
        photo = await PhotoRepository.get_photo_by_id(session, photo_id)
        if not photo:
            return None
        photo.description = description
        session.add(photo)
        await session.commit()
        await session.refresh(photo)
        return photo

    @staticmethod
    async def delete_photo(session: AsyncSession, photo_id: int):
        photo = await PhotoRepository.get_photo_by_id(session, photo_id)
        if not photo:
            return None
        await session.delete(photo)
        await session.commit()
        return photo
