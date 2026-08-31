""" 
Файл для визначення репозиторію користувачів у базі даних. Містить клас UserRepository, який надає
методи для створення, отримання та оновлення користувачів. Використовує SQLAlchemy для взаємодії з
базою даних та асинхронні сесії для ефективного виконання запитів. Методи огорнуті у статичні
методи, що дозволяє викликати їх без створення екземпляру класу.
Методи включають:
- create_user: Створює нового користувача з хешованим паролем та роллю.
- get_user_by_username: Отримує користувача за його ім'ям користувача.
- update_user: Оновлює інформацію про користувача.
- check_user_credentials: Перевіряє облікові дані користувача.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.models.user import User, Role
from app.core.security import get_password_hash, verify_password

class UserRepository:
    @staticmethod
    async def create_user(session: AsyncSession, username: str, password: str, role: str = Role.USER):
        hashed_password = get_password_hash(password)
        user = User(username=username, hashed_password=hashed_password, role=role, is_active=True)  
        session.add(user)
        try:
            await session.commit()
            await session.refresh(user)
            return user
        except IntegrityError:
            await session.rollback()
            return None

    @staticmethod
    async def get_user_by_username(session: AsyncSession, username: str):
        result = await session.execute(select(User).where(User.username == username))
        return result.scalars().first()

    @staticmethod
    async def update_user(session: AsyncSession, username: str, **kwargs):
        user = await UserRepository.get_user_by_username(session, username)
        if not user:
            return None
        for key, value in kwargs.items():
            setattr(user, key, value)
        try:
            await session.commit()
            await session.refresh(user)
            return user
        except IntegrityError:
            await session.rollback()
            return None

    @staticmethod
    async def check_user_credentials(session: AsyncSession, username: str, password: str):
        user = await UserRepository.get_user_by_username(session, username)
        if not user or not verify_password(password, user.hashed_password):   
            return None
        return user
