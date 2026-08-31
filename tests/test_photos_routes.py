import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_photo_requires_auth():
    # правильний шлях: POST /photos/
    response = client.post(
        "/photos/",
        files={"file": ("test.jpg", b"fakeimg", "image/jpeg")}
    )
    assert response.status_code == 401  # без токена

def test_moderate_photo_requires_auth():
    response = client.put("/photos/1/moderate", data={"transformation": "resize"})
    assert response.status_code == 401

def test_update_photo_requires_auth():
    response = client.put("/photos/1", data={"description": "new desc"})
    assert response.status_code == 401

def test_delete_photo_requires_auth():
    response = client.delete("/photos/1")
    assert response.status_code == 401

def test_add_tags_requires_auth():
    response = client.post("/photos/1/tags", json={"tag_names": ["summer"]})
    assert response.status_code == 401

def test_delete_photo_tag_requires_auth():
    response = client.delete("/photos/1/tags/1")
    assert response.status_code == 401

def test_get_user_photos_empty():
    response = client.get("/photos/user/999")
    assert response.status_code == 200
    assert response.json() == []
