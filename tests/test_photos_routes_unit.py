import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.routes import photos
from app.models.user import User, Role
from app.models.photo import Photo
from datetime import datetime


class DummyFile:
    filename = "test.jpg"

    def __init__(self):
        import io
        # додаємо атрибут file, як у UploadFile
        self.file = io.BytesIO(b"fake image data")


# --- upload_photo ---
@pytest.mark.asyncio
async def test_upload_photo_fails_on_cloudinary(mocker, async_db_session: AsyncSession):
    mocker.patch("app.routes.photos.upload_image", return_value=None)
    user = User(id=1, username="test", email="t@t.com", role=Role.USER)
    file = DummyFile()
    with pytest.raises(HTTPException):
        await photos.upload_photo(file=file, description="desc", tag_names=[],
                                  db=async_db_session, current_user=user)

# --- moderate_photo ---
@pytest.mark.asyncio
async def test_moderate_photo_not_found(async_db_session: AsyncSession):
    user = User(id=1, username="admin", email="a@a.com", role=Role.ADMIN)
    with pytest.raises(HTTPException):
        await photos.moderate_photo(photo_id=999, transformation="resize",
                                    tag_names=[], db=async_db_session, current_user=user)

@pytest.mark.asyncio
async def test_moderate_photo_invalid_transformation(async_db_session: AsyncSession):
    photo = Photo(id=1, url="url", public_id="pid", user_id=1)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)
    user = User(id=2, username="admin", email="a@a.com", role=Role.ADMIN)
    with pytest.raises(HTTPException):
        await photos.moderate_photo(photo_id=1, transformation="wrong",
                                    tag_names=[], db=async_db_session, current_user=user)

# --- moderate_photo_success_admin ---
@pytest.mark.asyncio
async def test_moderate_photo_success_admin(mocker, async_db_session: AsyncSession):
    owner = User(id=1, username="owner", email="o@o.com", role=Role.USER, hashed_password="fake")
    async_db_session.add(owner); await async_db_session.commit(); await async_db_session.refresh(owner)

    photo = Photo(id=1, url="url", public_id="pid", user_id=owner.id,
                  description="x", created_at=datetime.utcnow(), owner=owner)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)

    mocker.patch("app.routes.photos.transform_image", return_value="http://fake/transformed.jpg")
    mocker.patch("app.routes.photos.upload_bytes", return_value={"secure_url": "http://fake/qr.jpg"})

    admin = User(id=2, username="admin", email="a@a.com", role=Role.ADMIN, hashed_password="fake")
    result = await photos.moderate_photo(photo_id=1, transformation="resize",
                                         tag_names=["summer"], db=async_db_session, current_user=admin)
    assert result.url == "http://fake/transformed.jpg"


# --- moderate_photo_success_moderator ---
@pytest.mark.asyncio
async def test_moderate_photo_success_moderator(mocker, async_db_session: AsyncSession):
    # створюємо модератора
    moderator = User(id=3, username="mod", email="m@m.com",
                     role=Role.MODERATOR, hashed_password="fake")
    async_db_session.add(moderator)
    await async_db_session.commit()
    await async_db_session.refresh(moderator)

    # створюємо фото, яке належить модератору
    photo = Photo(id=1, url="url", public_id="pid", user_id=moderator.id,
                  description="x", created_at=datetime.utcnow(), owner=moderator)
    async_db_session.add(photo)
    await async_db_session.commit()
    await async_db_session.refresh(photo)

    # мок трансформацій
    mocker.patch("app.routes.photos.transform_image", return_value="http://fake/transformed.jpg")
    mocker.patch("app.routes.photos.upload_bytes", return_value={"secure_url": "http://fake/qr.jpg"})

    # модератор модеруює власне фото → успіх
    result = await photos.moderate_photo(photo_id=1, transformation="resize",
                                         tag_names=[], db=async_db_session, current_user=moderator)
    assert result.status == "approved"



@pytest.mark.asyncio
async def test_moderate_photo_forbidden_user(async_db_session: AsyncSession):
    photo = Photo(id=1, url="url", public_id="pid", user_id=2)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)
    user = User(id=1, username="user", email="u@u.com", role=Role.USER)
    with pytest.raises(HTTPException):
        await photos.moderate_photo(photo_id=1, transformation="resize",
                                    tag_names=[], db=async_db_session, current_user=user)

# --- update_photo_success_owner ---
@pytest.mark.asyncio
async def test_update_photo_success_owner(async_db_session: AsyncSession):
    owner = User(id=1, username="owner", email="o@o.com", role=Role.USER, hashed_password="fake")
    async_db_session.add(owner); await async_db_session.commit(); await async_db_session.refresh(owner)

    photo = Photo(id=1, url="url", public_id="pid", user_id=owner.id,
                  description="old", created_at=datetime.utcnow(), owner=owner)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)

    result = await photos.update_photo(photo_id=1, description="new desc",
                                       tag_names=["tag1"], db=async_db_session, current_user=owner)
    assert result.description == "new desc"


@pytest.mark.asyncio
async def test_update_photo_forbidden_moderator(async_db_session: AsyncSession):
    photo = Photo(id=1, url="url", public_id="pid", user_id=2)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)
    user = User(id=3, username="mod", email="m@m.com", role=Role.MODERATOR)
    with pytest.raises(HTTPException):
        await photos.update_photo(photo_id=1, description="new desc",
                                  tag_names=["tag1"], db=async_db_session, current_user=user)

# --- delete_photo ---
@pytest.mark.asyncio
async def test_delete_photo_success_owner(async_db_session: AsyncSession):
    photo = Photo(id=1, url="url", public_id="pid", user_id=1)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)
    user = User(id=1, username="owner", email="o@o.com", role=Role.USER)
    result = await photos.delete_photo(photo_id=1, db=async_db_session, current_user=user)
    assert "deleted successfully" in result["detail"]

@pytest.mark.asyncio
async def test_delete_photo_success_admin(async_db_session: AsyncSession):
    photo = Photo(id=1, url="url", public_id="pid", user_id=2)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)
    user = User(id=2, username="admin", email="a@a.com", role=Role.ADMIN)
    result = await photos.delete_photo(photo_id=1, db=async_db_session, current_user=user)
    assert "deleted successfully" in result["detail"]

@pytest.mark.asyncio
async def test_delete_photo_forbidden_moderator(async_db_session: AsyncSession):
    photo = Photo(id=1, url="url", public_id="pid", user_id=2)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)
    user = User(id=3, username="mod", email="m@m.com", role=Role.MODERATOR)
    with pytest.raises(HTTPException):
        await photos.delete_photo(photo_id=1, db=async_db_session, current_user=user)

# --- add_tags_success_owner ---
@pytest.mark.asyncio
async def test_add_tags_success_owner(async_db_session: AsyncSession):
    owner = User(id=1, username="owner", email="o@o.com", role=Role.USER, hashed_password="fake")
    async_db_session.add(owner); await async_db_session.commit(); await async_db_session.refresh(owner)

    photo = Photo(id=1, url="url", public_id="pid", user_id=owner.id,
                  description="x", created_at=datetime.utcnow(), owner=owner)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)

    result = await photos.add_tags(photo_id=1, tag_names=["extra"],
                                   db=async_db_session, current_user=owner)
    assert any(tag.name == "extra" for tag in result.tags)


@pytest.mark.asyncio
async def test_add_tags_forbidden_moderator(async_db_session: AsyncSession):
    photo = Photo(id=1, url="url", public_id="pid", user_id=2)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)
    user = User(id=3, username="mod", email="m@m.com", role=Role.MODERATOR)
    with pytest.raises(HTTPException):
        await photos.add_tags(photo_id=1, tag_names=["extra"],
                              db=async_db_session, current_user=user)

# --- delete_photo_tag ---
@pytest.mark.asyncio
async def test_delete_photo_tag_success_owner(async_db_session: AsyncSession):
    photo = Photo(id=1, url="url", public_id="pid", user_id=1)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)

    user = User(id=1, username="owner", email="o@o.com", role=Role.USER)
    # тут можна додати тег і потім видалити, для простоти перевіряємо 404
    with pytest.raises(HTTPException):
        await photos.delete_photo_tag(photo_id=1, tag_id=999,
                                      db=async_db_session, current_user=user)

@pytest.mark.asyncio
async def test_delete_photo_tag_forbidden_moderator(async_db_session: AsyncSession):
    photo = Photo(id=1, url="url", public_id="pid", user_id=2)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)

    user = User(id=3, username="mod", email="m@m.com", role=Role.MODERATOR)
    with pytest.raises(HTTPException):
        await photos.delete_photo_tag(photo_id=1, tag_id=1,
                                      db=async_db_session, current_user=user)


# --- get_user_photos ---
@pytest.mark.asyncio
async def test_get_user_photos_empty(async_db_session: AsyncSession):
    result = await photos.get_user_photos(user_id=999, db=async_db_session)
    assert result == []

# --------------------------------------------------------------------------------


# --- delete_photo_tag_success_admin ---
@pytest.mark.asyncio
async def test_delete_photo_tag_success_admin(async_db_session: AsyncSession):
    admin = User(id=2, username="admin", email="a@a.com", role=Role.ADMIN, hashed_password="fake")
    async_db_session.add(admin); await async_db_session.commit(); await async_db_session.refresh(admin)

    photo = Photo(id=1, url="url", public_id="pid", user_id=admin.id,
                  description="x", created_at=datetime.utcnow(), owner=admin)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)

    result = await photos.add_tags(photo_id=1, tag_names=["tag1"], db=async_db_session, current_user=admin)
    tag_id = result.tags[0].id

    result = await photos.delete_photo_tag(photo_id=1, tag_id=tag_id,
                                           db=async_db_session, current_user=admin)
    assert all(tag.id != tag_id for tag in result.tags)

# --- tags limit ---
@pytest.mark.asyncio
async def test_add_tags_limit_exceeded(async_db_session: AsyncSession):
    owner = User(id=1, username="owner", email="o@o.com", role=Role.USER, hashed_password="fake")
    async_db_session.add(owner); await async_db_session.commit(); await async_db_session.refresh(owner)

    photo = Photo(id=1, url="url", public_id="pid", user_id=owner.id,
                  description="x", created_at=datetime.utcnow(), owner=owner)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)

    with pytest.raises(HTTPException) as exc:
        await photos.add_tags(photo_id=1, tag_names=["t1","t2","t3","t4","t5","t6"],
                              db=async_db_session, current_user=owner)
    assert exc.value.status_code == 400

# --- add_tags_duplicate ---
import sqlalchemy

@pytest.mark.asyncio
async def test_add_tags_duplicate(async_db_session: AsyncSession):
    owner = User(id=1, username="owner", email="o@o.com",
                 role=Role.USER, hashed_password="fake")
    async_db_session.add(owner); await async_db_session.commit(); await async_db_session.refresh(owner)

    photo = Photo(id=1, url="url", public_id="pid", user_id=owner.id,
                  description="x", created_at=datetime.utcnow(), owner=owner)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)

    await photos.add_tags(photo_id=1, tag_names=["tag1"], db=async_db_session, current_user=owner)

    # друга спроба → очікуємо IntegrityError
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        await photos.add_tags(photo_id=1, tag_names=["tag1"], db=async_db_session, current_user=owner)

# --- get_user_photos ---
@pytest.mark.asyncio
async def test_get_user_photos_non_empty(async_db_session: AsyncSession):
    owner = User(id=1, username="owner", email="o@o.com", role=Role.USER, hashed_password="fake")
    async_db_session.add(owner); await async_db_session.commit(); await async_db_session.refresh(owner)

    photo = Photo(id=1, url="url", public_id="pid", user_id=owner.id,
                  description="x", created_at=datetime.utcnow(), owner=owner)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)

    result = await photos.get_user_photos(user_id=owner.id, db=async_db_session)
    assert len(result) == 1
    assert result[0].description == "x"

# --- transformations ---
# --- moderate_photo_circle ---
@pytest.mark.asyncio
async def test_moderate_photo_circle(mocker, async_db_session: AsyncSession):
    owner = User(id=1, username="owner", email="o@o.com", role=Role.USER, hashed_password="fake")
    async_db_session.add(owner); await async_db_session.commit(); await async_db_session.refresh(owner)

    photo = Photo(id=1, url="url", public_id="pid", user_id=owner.id,
                  description="x", created_at=datetime.utcnow(), owner=owner)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)

    mocker.patch("app.routes.photos.transform_image", return_value="http://fake/circle.jpg")
    mocker.patch("app.routes.photos.upload_bytes", return_value={"secure_url": "http://fake/qr.jpg"})

    result = await photos.moderate_photo(photo_id=1, transformation="circle",
                                         tag_names=[], db=async_db_session, current_user=owner)
    assert result.url == "http://fake/circle.jpg"


# --- moderate_photo_watermark ---
@pytest.mark.asyncio
async def test_moderate_photo_text(mocker, async_db_session: AsyncSession):
    owner = User(id=1, username="owner", email="o@o.com", role=Role.USER, hashed_password="fake")
    async_db_session.add(owner); await async_db_session.commit(); await async_db_session.refresh(owner)

    photo = Photo(id=1, url="url", public_id="pid", user_id=owner.id,
                  description="x", created_at=datetime.utcnow(), owner=owner)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)

    mocker.patch("app.routes.photos.transform_image", return_value="http://fake/text.jpg")
    mocker.patch("app.routes.photos.upload_bytes", return_value={"secure_url": "http://fake/qr.jpg"})

    result = await photos.moderate_photo(photo_id=1, transformation="text",
                                         tag_names=[], db=async_db_session, current_user=owner)
    assert result.url == "http://fake/text.jpg"

@pytest.mark.asyncio
async def test_delete_photo_tag_not_found(async_db_session: AsyncSession):
    owner = User(id=1, username="owner", email="o@o.com",
                 role=Role.USER, hashed_password="fake")
    async_db_session.add(owner); await async_db_session.commit(); await async_db_session.refresh(owner)

    photo = Photo(id=1, url="url", public_id="pid", user_id=owner.id,
                  description="x", created_at=datetime.utcnow(), owner=owner)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)

    # тегу немає → очікуємо 404
    with pytest.raises(HTTPException) as exc:
        await photos.delete_photo_tag(photo_id=1, tag_id=999,
                                      db=async_db_session, current_user=owner)
    assert exc.value.status_code == 404
    

@pytest.mark.asyncio
async def test_moderate_photo_forbidden_moderator(async_db_session: AsyncSession):
    owner = User(id=1, username="owner", email="o@o.com",
                 role=Role.USER, hashed_password="fake")
    moderator = User(id=2, username="mod", email="m@m.com",
                     role=Role.MODERATOR, hashed_password="fake")
    async_db_session.add_all([owner, moderator]); await async_db_session.commit()
    await async_db_session.refresh(owner); await async_db_session.refresh(moderator)

    photo = Photo(id=1, url="url", public_id="pid", user_id=owner.id,
                  description="x", created_at=datetime.utcnow(), owner=owner)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)

    with pytest.raises(HTTPException) as exc:
        await photos.moderate_photo(photo_id=1, transformation="resize",
                                    tag_names=[], db=async_db_session, current_user=moderator)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_update_photo_not_found(async_db_session: AsyncSession):
    user = User(id=1, username="u", email="u@u.com", role=Role.USER, hashed_password="fake")
    async_db_session.add(user); await async_db_session.commit(); await async_db_session.refresh(user)
    with pytest.raises(HTTPException) as exc:
        await photos.update_photo(photo_id=999, description="desc",
                                  tag_names=["t1"], db=async_db_session, current_user=user)
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_update_photo_tags_limit(async_db_session: AsyncSession):
    owner = User(id=1, username="o", email="o@o.com", role=Role.USER, hashed_password="fake")
    async_db_session.add(owner); await async_db_session.commit(); await async_db_session.refresh(owner)
    photo = Photo(id=1, url="url", public_id="pid", user_id=owner.id,
                  description="old", created_at=datetime.utcnow(), owner=owner)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)
    with pytest.raises(HTTPException) as exc:
        await photos.update_photo(photo_id=1, description="new",
                                  tag_names=["t1","t2","t3","t4","t5","t6"],
                                  db=async_db_session, current_user=owner)
    assert exc.value.status_code == 400



@pytest.mark.asyncio
async def test_moderate_photo_qr_fail(mocker, async_db_session: AsyncSession):
    owner = User(id=1, username="owner", email="o@o.com", role=Role.USER, hashed_password="fake")
    async_db_session.add(owner); await async_db_session.commit(); await async_db_session.refresh(owner)
    photo = Photo(id=1, url="url", public_id="pid", user_id=owner.id,
                  description="x", created_at=datetime.utcnow(), owner=owner)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)

    mocker.patch("app.routes.photos.transform_image", return_value="http://fake/transformed.jpg")
    mocker.patch("app.routes.photos.upload_bytes", return_value=None)  # QR upload fails

    with pytest.raises(HTTPException) as exc:
        await photos.moderate_photo(photo_id=1, transformation="resize",
                                    tag_names=[], db=async_db_session, current_user=owner)
    assert exc.value.status_code == 500

@pytest.mark.asyncio
async def test_update_photo_replace_tags(async_db_session: AsyncSession):
    owner = User(id=1, username="owner", email="o@o.com", role=Role.USER, hashed_password="fake")
    async_db_session.add(owner); await async_db_session.commit(); await async_db_session.refresh(owner)
    photo = Photo(id=1, url="url", public_id="pid", user_id=owner.id,
                  description="old", created_at=datetime.utcnow(), owner=owner)
    async_db_session.add(photo); await async_db_session.commit(); await async_db_session.refresh(photo)

    # додаємо перший тег
    await photos.add_tags(photo_id=1, tag_names=["tag1"], db=async_db_session, current_user=owner)
    # тепер оновлюємо з іншим тегом
    result = await photos.update_photo(photo_id=1, description="new",
                                       tag_names=["tag2"], db=async_db_session, current_user=owner)
    assert any(tag.name == "tag2" for tag in result.tags)
    assert all(tag.name != "tag1" for tag in result.tags)


@pytest.mark.asyncio
async def test_upload_photo_tags_limit(mocker, async_db_session: AsyncSession):
    # замокаємо Cloudinary upload, щоб не йти у реальний сервіс
    mocker.patch("app.routes.photos.upload_image", return_value={"secure_url": "http://fake.jpg", "public_id": "pid"})

    owner = User(id=1, username="owner", email="o@o.com", role=Role.USER, hashed_password="fake")
    async_db_session.add(owner)
    await async_db_session.commit()
    await async_db_session.refresh(owner)

    file = DummyFile()

    # одразу перевищуємо ліміт тегів (>5)
    with pytest.raises(HTTPException) as exc:
        await photos.upload_photo(
            file=file,
            description="desc",
            tag_names=["t1", "t2", "t3", "t4", "t5", "t6"],
            db=async_db_session,
            current_user=owner
        )
    assert exc.value.status_code == 400

