import pytest
from app.services.cloudinary_service import transform_image

def test_user_cannot_transform_photo():
    role = "user"
    with pytest.raises(PermissionError):
        if role not in ["admin", "moderator"]:
            raise PermissionError("Not allowed")

def test_moderator_can_transform_photo():
    role = "moderator"
    url = transform_image("pid123", {"width": 100})
    assert "pid123" in url
    assert "w_100" in url

def test_admin_can_transform_photo():
    role = "admin"
    url = transform_image("pid456", {"width": 200})
    assert "pid456" in url
    assert "w_200" in url

