"""
Файл для створення FastAPI додатку. Містить основний об'єкт додатку та реєстрацію маршрутів.
Використовує FastAPI для створення REST API та SQLAlchemy для взаємодії з базою даних. Функції
огорнуті у маршрутизаційний клас APIRouter,що дозволяє організувати маршрути у модулі. Використовує
асинхронні сесії для ефективного виконання запитів. Додатково визначає кастомну OpenAPI схему для
інтеграції з OAuth2 password flow, що дозволяє користувачам отримувати токени доступу та оновлення 
через ендпоінт /auth/login. Основні маршрути включають:
- /auth: маршрути для аутентифікації користувачів, включаючи реєстрацію та логін.
- /users: маршрути для роботи з користувачами, включаючи перегляд та редагування профілів,
призначення ролей та бан/розбан користувачів.
- /photos: маршрути для роботи з фото, включаючи завантаження, перегляд, редагування та
видалення фото.
- /comments: маршрути для роботи з коментарями до фото, включаючи створення, отримання, редагування
та видалення коментарів.
- /tags: маршрути для роботи з тегами, включаючи створення, отримання та видалення тегів.
"""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.routes import auth, users, photos, comments, tags

app = FastAPI()

# реєструємо роутери
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(photos.router)
app.include_router(comments.router)
app.include_router(tags.router)

# кастомна OpenAPI схема для кнопки Authorize
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="PhotoShare API",
        version="1.0.0",
        description="API для фотошерінгу",
        routes=app.routes,
    )
    # 🔹 додаємо OAuth2 password flow
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/auth/login",   # ендпоінт для отримання токена
                    "scopes": {}
                }
            }
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"OAuth2PasswordBearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
