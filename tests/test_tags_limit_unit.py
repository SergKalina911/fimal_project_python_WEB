import pytest
from app.models.tag import Tag
from app.models.photo import Photo

def test_photo_can_have_any_number_of_tags():
    tags = [Tag(id=i, name=f"tag{i}") for i in range(6)]
    photo = Photo(id=1, url="http://fake", description="desc", user_id=1, tags=tags, status="active")
    assert len(photo.tags) == 6

def test_photo_can_have_duplicate_tags():
    tag1 = Tag(id=1, name="travel")
    tags = [tag1, tag1]
    photo = Photo(id=2, url="http://fake2", description="desc2", user_id=1, tags=tags, status="active")
    assert len(photo.tags) == 2
    assert photo.tags[0].name == "travel"
