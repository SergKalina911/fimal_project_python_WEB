import pytest
from app.repositories.tag_repo import TagRepository
from app.models.tag import Tag

@pytest.mark.asyncio
async def test_create_tag_success(async_db_session):
    tag = await TagRepository.create_tag(async_db_session, "travel")
    assert isinstance(tag, Tag)
    assert tag.name == "travel"

@pytest.mark.asyncio
async def test_get_tag_by_name_not_found(async_db_session):
    tag = await TagRepository.get_tag_by_name(async_db_session, "ghost")
    assert tag is None

@pytest.mark.asyncio
async def test_get_all_tags_returns_list(async_db_session):
    await TagRepository.create_tag(async_db_session, "t1")
    await TagRepository.create_tag(async_db_session, "t2")
    tags = await TagRepository.get_all_tags(async_db_session)
    assert isinstance(tags, list)
    assert len(tags) >= 2
