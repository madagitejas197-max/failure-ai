import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock
import uuid

from app.main import app
from app.database import get_db
from app.models import User, UserRole


# Mock security functions to avoid passlib bcrypt issues under Python 3.12
@pytest.fixture(autouse=True)
def mock_security(monkeypatch):
    monkeypatch.setattr("app.routers.auth.hash_password", lambda x: f"hashed_{x}")
    monkeypatch.setattr("app.routers.auth.verify_password", lambda plain, hashed: hashed == f"hashed_{plain}")
    monkeypatch.setattr("app.core.security.hash_password", lambda x: f"hashed_{x}")
    monkeypatch.setattr("app.core.security.verify_password", lambda plain, hashed: hashed == f"hashed_{plain}")


class MockUserScalar:
    def __init__(self, user):
        self.user = user

    def first(self):
        return self.user

    def all(self):
        return [self.user] if self.user else []


class MockResult:
    def __init__(self, user):
        self.user = user

    def scalars(self):
        return MockUserScalar(self.user)


@pytest.mark.asyncio
async def test_register_user_success():
    # Setup mock DB session
    mock_db = AsyncMock()
    mock_db.execute.return_value = MockResult(None)  # No existing user

    # Override get_db dependency
    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "strongpassword",
                "display_name": "Test User",
            },
        )

    # Clean up overrides
    app.dependency_overrides.clear()

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["display_name"] == "Test User"
    assert "id" in data
    mock_db.add.assert_called_once()
    mock_db.flush.assert_called_once()


@pytest.mark.asyncio
async def test_register_user_already_exists():
    # Setup mock DB session returning an existing user
    existing_user = User(
        email="exists@example.com",
        display_name="Existing User",
        password_hash="hashed_password",
    )
    mock_db = AsyncMock()
    mock_db.execute.return_value = MockResult(existing_user)

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "exists@example.com",
                "password": "password",
                "display_name": "Existing User",
            },
        )

    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json()["detail"] == "A user with this email already exists."


@pytest.mark.asyncio
async def test_login_success():
    hashed = "hashed_mypassword"
    existing_user = User(
        email="login@example.com",
        display_name="Login User",
        password_hash=hashed,
    )
    # Mocking ID generation since it's not set by default constructor in python-land for test
    existing_user.id = uuid.uuid4()

    mock_db = AsyncMock()
    mock_db.execute.return_value = MockResult(existing_user)

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "mypassword",
            },
        )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
