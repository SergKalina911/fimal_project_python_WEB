import pytest
from datetime import datetime, UTC
from pydantic import ValidationError
from app.schemas import UserRead, PhotoRead, CommentRead, TagRead

def test_user_read_schema_serialization():
    user = UserRead(id=1, username="test", email="t@test.com", role="user", is_active=True)
    data = user.model_dump()
    assert data["username"] == "test"
    assert data["email"] == "t@test.com"

def test_photo_read_schema_serialization():
    photo = PhotoRead(
        id=1,
        url="http://fake/url.jpg",
        description="desc",
        user_id=1,
        tags=[],
        status="active"
    )
    data = photo.model_dump()
    assert data["url"].startswith("http://fake/")
    assert data["description"] == "desc"
    assert data["status"] == "active"

def test_photo_read_missing_status_raises():
    with pytest.raises(ValidationError):
        PhotoRead(id=1, url="http://fake/url.jpg", description="desc", user_id=1, tags=[])

def test_comment_read_schema_serialization():
    comment = CommentRead(
        id=1,
        text="Nice!",
        photo_id=1,
        user_id=1,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    data = comment.model_dump()
    assert data["text"] == "Nice!"
    assert data["photo_id"] == 1
    assert "created_at" in data
    assert "updated_at" in data

def test_comment_read_missing_dates_raises():
    with pytest.raises(ValidationError):
        CommentRead(id=1, text="Nice!", photo_id=1, user_id=1)

def test_tag_read_schema_serialization():
    tag = TagRead(id=1, name="travel")
    data = tag.model_dump()
    assert data["name"] == "travel"

def test_tag_read_missing_name_raises():
    with pytest.raises(ValidationError):
        TagRead(id=1)
