import qrcode
from io import BytesIO

class QRService:
    @staticmethod
    def generate_qr(data: str, box_size: int = 10, border: int = 5,
                    fill_color: str = "black", back_color: str = "white") -> BytesIO:
        """Генерує QR-код і повертає його як PNG у пам'яті"""
        qr = qrcode.QRCode(version=1, box_size=box_size, border=border)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer
