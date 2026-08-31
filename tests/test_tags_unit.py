import pytest
from app.models.tag import Tag

def test_create_tag():
    tag = Tag(id=1, name="travel")
    assert tag.name == "travel"

def test_create_multiple_tags():
    tags = [Tag(id=i, name=f"tag{i}") for i in range(3)]
    assert len(tags) == 3
    assert tags[0].name == "tag0"
