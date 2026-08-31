import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_app_starts_and_has_routes():
    # перевіряємо що сервер стартує і повертає docs
    response = client.get("/docs")
    assert response.status_code == 200

    # перевіряємо що openapi схема містить потрібні групи
    schema = client.get("/openapi.json").json()
    paths = schema["paths"].keys()

    assert any("/auth" in p for p in paths)
    assert any("/users" in p for p in paths)
    assert any("/photos" in p for p in paths)
    assert any("/comments" in p for p in paths)
    assert any("/tags" in p for p in paths)

def test_openapi_schema_contains_oauth2():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "OAuth2PasswordBearer" in schema["components"]["securitySchemes"]
    assert schema["components"]["securitySchemes"]["OAuth2PasswordBearer"]["type"] == "oauth2"
