import pytest
from sqlalchemy.exc import IntegrityError
from app.repositories.photo_repo import PhotoRepository
from app.models.photo import Photo

@pytest.mark.asyncio
async def test_create_photo_fails_without_public_id(async_db_session):
    # Репозиторій не ставить public_id → очікуємо IntegrityError
    with pytest.raises(IntegrityError):
        await PhotoRepository.create_photo(async_db_session,
                                           url="http://fake/url.jpg",
                                           description="desc",
                                           user_id=1)

@pytest.mark.asyncio
async def test_create_photo_direct_model(async_db_session):
    # Створюємо валідний об’єкт напряму через модель
    p = Photo(url="http://fake/url.jpg",
              description="desc",
              user_id=1,
              public_id="fake123")
    async_db_session.add(p)
    await async_db_session.commit()
    await async_db_session.refresh(p)
    assert isinstance(p, Photo)
    assert p.public_id == "fake123"
    assert p.url.startswith("http://fake/")


@pytest.mark.asyncio
async def test_get_photo_by_id_success(async_db_session):
    p = Photo(url="http://fake/url.jpg", description="desc", user_id=1, public_id="fake123")
    async_db_session.add(p)
    await async_db_session.commit()
    await async_db_session.refresh(p)

    fetched = await PhotoRepository.get_photo_by_id(async_db_session, p.id)
    assert isinstance(fetched, Photo)
    assert fetched.id == p.id

@pytest.mark.asyncio
async def test_get_photo_by_id_not_found(async_db_session):
    result = await PhotoRepository.get_photo_by_id(async_db_session, 999)
    assert result is None

@pytest.mark.asyncio
async def test_get_photos_by_user(async_db_session):
    p1 = Photo(url="http://fake/1.jpg", description="d1", user_id=1, public_id="p1")
    p2 = Photo(url="http://fake/2.jpg", description="d2", user_id=1, public_id="p2")
    async_db_session.add_all([p1, p2])
    await async_db_session.commit()
    photos = await PhotoRepository.get_photos_by_user(async_db_session, 1)
    assert len(photos) == 2
    assert all(isinstance(p, Photo) for p in photos)

@pytest.mark.asyncio
async def test_update_photo_description(async_db_session):
    p = Photo(url="http://fake/url.jpg", description="old", user_id=1, public_id="upd")
    async_db_session.add(p)
    await async_db_session.commit()
    await async_db_session.refresh(p)

    updated = await PhotoRepository.update_photo_description(async_db_session, p.id, "new")
    assert updated.description == "new"

    none_case = await PhotoRepository.update_photo_description(async_db_session, 999, "x")
    assert none_case is None

@pytest.mark.asyncio
async def test_delete_photo(async_db_session):
    p = Photo(url="http://fake/url.jpg", description="del", user_id=1, public_id="del")
    async_db_session.add(p)
    await async_db_session.commit()
    await async_db_session.refresh(p)

    deleted = await PhotoRepository.delete_photo(async_db_session, p.id)
    assert deleted.id == p.id

    none_case = await PhotoRepository.delete_photo(async_db_session, 999)
    assert none_case is None
