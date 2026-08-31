"""
В цьому файлі ми імпортуємо всі моделі, щоб вони були доступні при імпорті пакету `app.models`. Це
дозволяє уникнути проблем з циклічними імпортами та забезпечує зручний доступ до всіх моделей
у додатку.
"""

from .user import User
from .photo import Photo
from .comment import Comment
from .tag import Tag
