### D:\Old_notebook\GoIt\Python\Project_Web\fimal_project_python_WEB\app\main.py

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
