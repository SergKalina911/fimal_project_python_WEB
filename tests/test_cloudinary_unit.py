import pytest
from io import BytesIO
from app.services import cloudinary_service

class FakeUploadFile:
    def __init__(self, content: bytes):
        self.file = BytesIO(content)

# --- upload_image ---
def test_upload_image_success(monkeypatch):
    monkeypatch.setattr(
        cloudinary_service,
        "upload_image",
        lambda file, folder="photos": {"secure_url": "http://fake/url.jpg", "public_id": "fake123"}
    )
    fake_file = FakeUploadFile(b"fake_bytes")
    result = cloudinary_service.upload_image(fake_file)
    assert result["secure_url"] == "http://fake/url.jpg"
    assert result["public_id"] == "fake123"

def test_upload_image_failure(monkeypatch):
    monkeypatch.setattr(
        cloudinary_service,
        "upload_image",
        lambda file, folder="photos": (_ for _ in ()).throw(Exception("upload failed"))
    )
    fake_file = FakeUploadFile(b"bad_bytes")
    with pytest.raises(Exception) as exc:
        cloudinary_service.upload_image(fake_file)
    assert "upload failed" in str(exc.value)

# --- upload_bytes ---
def test_upload_bytes_success(monkeypatch):
    monkeypatch.setattr(
        cloudinary_service,
        "upload_bytes",
        lambda buffer, folder="photos": {"secure_url": "http://fake/bytes.jpg", "public_id": "bytes123"}
    )
    result = cloudinary_service.upload_bytes(b"fake_bytes")
    assert result["secure_url"] == "http://fake/bytes.jpg"
    assert result["public_id"] == "bytes123"

def test_upload_bytes_failure(monkeypatch):
    monkeypatch.setattr(
        cloudinary_service,
        "upload_bytes",
        lambda buffer, folder="photos": (_ for _ in ()).throw(Exception("upload failed"))
    )
    with pytest.raises(Exception) as exc:
        cloudinary_service.upload_bytes(b"bad_bytes")
    assert "upload failed" in str(exc.value)

# --- transform_image ---
def test_transform_image_with_params(monkeypatch):
    monkeypatch.setattr(
        cloudinary_service,
        "transform_image",
        lambda pid, transformation: f"http://fake/transformed/{pid}.jpg"
    )
    result = cloudinary_service.transform_image("fake123", [{"width": 200}])
    assert result == "http://fake/transformed/fake123.jpg"

def test_transform_image_invalid_params(monkeypatch):
    monkeypatch.setattr(
        cloudinary_service,
        "transform_image",
        lambda pid, transformation: f"http://fake/transformed/{pid}.jpg"
    )
    result = cloudinary_service.transform_image("fake123", [{"invalid": "param"}])
    assert result == "http://fake/transformed/fake123.jpg"
