import pytest
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.routes import auth
from app.models.user import User, Role
from app.core.security import get_password_hash

# --- signup ---
@pytest.mark.asyncio
async def test_signup_success_first_admin(async_db_session: AsyncSession, mocker):
    body = type("obj", (), {"username": "admin", "email": "a@a.com", "password": "pass"})
    mocker.patch("app.routes.auth.create_access_token", return_value="access")
    mocker.patch("app.routes.auth.create_refresh_token", return_value="refresh")
    result = await auth.signup(body=body, db=async_db_session)
    assert result.access_token == "access"
    assert result.refresh_token == "refresh"

@pytest.mark.asyncio
async def test_signup_conflict(mocker, async_db_session: AsyncSession):
    body = type("obj", (), {"username": "u", "email": "u@u.com", "password": "pass"})
    mocker.patch("app.routes.auth.get_password_hash", return_value="hashed")
    mocker.patch.object(async_db_session, "commit", side_effect=IntegrityError("conflict", {}, None))
    with pytest.raises(HTTPException) as exc:
        await auth.signup(body=body, db=async_db_session)
    assert exc.value.status_code == 409

# --- login ---
@pytest.mark.asyncio
async def test_login_success(async_db_session: AsyncSession, mocker):
    hashed = get_password_hash("pass")
    user = User(id=1, username="u", email="u@u.com", hashed_password=hashed, role=Role.USER)
    async_db_session.add(user); await async_db_session.commit(); await async_db_session.refresh(user)

    form = OAuth2PasswordRequestForm(username="u@u.com", password="pass", scope="")
    mocker.patch("app.routes.auth.create_access_token", return_value="access")
    mocker.patch("app.routes.auth.create_refresh_token", return_value="refresh")
    result = await auth.login(form_data=form, db=async_db_session)
    assert result.access_token == "access"

@pytest.mark.asyncio
async def test_login_not_found(async_db_session: AsyncSession):
    form = OAuth2PasswordRequestForm(username="no@no.com", password="pass", scope="")
    with pytest.raises(HTTPException) as exc:
        await auth.login(form_data=form, db=async_db_session)
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_login_inactive(async_db_session: AsyncSession):
    hashed = get_password_hash("pass")
    user = User(id=1, username="u", email="u@u.com", hashed_password=hashed, role=Role.USER, is_active=False)
    async_db_session.add(user); await async_db_session.commit(); await async_db_session.refresh(user)

    form = OAuth2PasswordRequestForm(username="u@u.com", password="pass", scope="")
    with pytest.raises(HTTPException) as exc:
        await auth.login(form_data=form, db=async_db_session)
    assert exc.value.status_code == 403

@pytest.mark.asyncio
async def test_login_invalid_password(async_db_session: AsyncSession):
    hashed = get_password_hash("right")
    user = User(id=1, username="u", email="u@u.com", hashed_password=hashed, role=Role.USER)
    async_db_session.add(user); await async_db_session.commit(); await async_db_session.refresh(user)

    form = OAuth2PasswordRequestForm(username="u@u.com", password="wrong", scope="")
    with pytest.raises(HTTPException) as exc:
        await auth.login(form_data=form, db=async_db_session)
    assert exc.value.status_code == 401

@pytest.mark.asyncio
async def test_signup_success_second_user(async_db_session: AsyncSession, mocker):
    # спочатку створюємо адміна
    admin = User(id=1, username="admin", email="a@a.com",
                 hashed_password=get_password_hash("pass"), role=Role.ADMIN)
    async_db_session.add(admin)
    await async_db_session.commit()
    await async_db_session.refresh(admin)

    # тепер реєструємо другого користувача
    body = type("obj", (), {"username": "user", "email": "u@u.com", "password": "pass"})
    mocker.patch("app.routes.auth.create_access_token", return_value="access")
    mocker.patch("app.routes.auth.create_refresh_token", return_value="refresh")

    result = await auth.signup(body=body, db=async_db_session)
    assert result.access_token == "access"
    assert result.refresh_token == "refresh"

    # перевіряємо, що роль призначена USER
    user = await async_db_session.get(User, 2)
    assert user.role == Role.USER
