import pytest
from app.models.photo import Photo

@pytest.mark.asyncio
async def test_create_photo_with_description_and_user(async_db_session):
    photo = Photo(
        url="http://fake/url.jpg",
        description="My photo",
        user_id=1,
        public_id="fake123"   # обов’язкове поле
    )
    async_db_session.add(photo)
    await async_db_session.commit()
    await async_db_session.refresh(photo)

    assert isinstance(photo, Photo)
    assert photo.description == "My photo"
    assert photo.user_id == 1
    assert photo.public_id == "fake123"

@pytest.mark.asyncio
async def test_update_photo_description(async_db_session):
    photo = Photo(
        id=1,
        url="http://fake/url.jpg",
        description="old",
        user_id=1,
        public_id="fake123"   # обов’язкове поле
    )
    async_db_session.add(photo)
    await async_db_session.commit()
    await async_db_session.refresh(photo)

    # оновлюємо вручну
    photo.description = "new"
    async_db_session.add(photo)
    await async_db_session.commit()
    await async_db_session.refresh(photo)

    assert photo.description == "new"
    assert photo.public_id == "fake123"
