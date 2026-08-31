""" 
Файл для генерації QR-кодів. Містить клас QRService, який надає метод generate_qr для створення
QR-коду з переданих даних. Використовує бібліотеку qrcode для генерації зображень QR-кодів та
BytesIO для збереження зображення у пам'яті у форматі PNG. Метод дозволяє налаштовувати розмір
блоків, товщину рамки та кольори заповнення і фону. Повертає об'єкт BytesIO, що містить
PNG-зображення QR-коду.
"""
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
