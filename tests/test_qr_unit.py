import pytest
from app.services.qr_service import QRService

def test_generate_qr_returns_bytes():
    qr_bytes = QRService.generate_qr("http://example.com")
    assert isinstance(qr_bytes, (bytes, bytearray))
    assert len(qr_bytes) > 0  # PNG або fake байти не порожні

def test_generate_qr_empty_string_still_returns_bytes():
    qr_bytes = QRService.generate_qr("")
    assert isinstance(qr_bytes, (bytes, bytearray))
    assert len(qr_bytes) > 0  # навіть для порожнього рядка повертає байти

def test_generate_qr_with_custom_params():
    qr_bytes = QRService.generate_qr(
        "custom-data",
        box_size=5,
        border=2,
        fill_color="blue",
        back_color="yellow"
    )
    assert isinstance(qr_bytes, (bytes, bytearray))
    assert len(qr_bytes) > 0

def test_generate_qr_invalid_color_still_returns_bytes():
    qr_bytes = QRService.generate_qr("data", fill_color="notacolor")
    assert isinstance(qr_bytes, (bytes, bytearray))
    assert len(qr_bytes) > 0
