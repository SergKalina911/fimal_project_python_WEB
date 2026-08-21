from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.tag import Tag

class TagRepository:
    @staticmethod
    async def create_tag(session: AsyncSession, name: str):
        tag = Tag(name=name)
        session.add(tag)
        await session.commit()
        await session.refresh(tag)
        return tag

    @staticmethod
    async def get_tag_by_name(session: AsyncSession, name: str):
        result = await session.execute(select(Tag).where(Tag.name == name))
        return result.scalars().first()

    @staticmethod
    async def get_all_tags(session: AsyncSession):
        result = await session.execute(select(Tag))
        return result.scalars().all()
