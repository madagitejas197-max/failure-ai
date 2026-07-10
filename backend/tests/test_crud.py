import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, MagicMock
import uuid

from app.main import app
from app.database import get_db
from app.models import User, UserRole, Project, Failure, Tag
from app.core.dependencies import get_current_user


class MockScalar:
    def __init__(self, items):
        self.items = items if isinstance(items, list) else [items]

    def first(self):
        return self.items[0] if self.items else None

    def all(self):
        return self.items


class MockResult:
    def __init__(self, items):
        self.items = items

    def scalars(self):
        return MockScalar(self.items)


@pytest.fixture
def test_user():
    user = User(
        email="user@example.com",
        display_name="Test User",
        role=UserRole.user,
    )
    user.id = uuid.uuid4()
    return user


@pytest.mark.asyncio
async def test_create_project(test_user):
    mock_db = MagicMock()
    mock_db.execute = AsyncMock()
    mock_db.flush = AsyncMock()
    mock_db.commit = AsyncMock()
    
    added_items = []

    def mock_add(item):
        added_items.append(item)

    mock_db.add.side_effect = mock_add

    # Set up execute mock side effect
    def mock_execute(statement, *args, **kwargs):
        stmt_str = str(statement).lower()
        if "from projects" in stmt_str or "projects.id" in stmt_str:
            projects = [item for item in added_items if isinstance(item, Project)]
            return MockResult(projects)
        return MockResult([])

    mock_db.execute.side_effect = mock_execute

    async def override_get_db():
        yield mock_db

    async def override_get_current_user():
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    # Use ASGITransport to avoid deprecation warning
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/projects",
            json={
                "name": "Test Project",
                "description": "A project for testing CRUD",
                "tech_stack": ["React", "FastAPI"],
                "visibility": "public",
            },
            headers={"Authorization": "Bearer test-token"},
        )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["tech_stack"] == ["React", "FastAPI"]
    assert "id" in data
    assert mock_db.add.call_count >= 1
    assert mock_db.flush.call_count >= 1


@pytest.mark.asyncio
async def test_create_failure_with_secrets_redaction(test_user):
    mock_db = MagicMock()
    mock_db.execute = AsyncMock()
    mock_db.flush = AsyncMock()
    mock_db.commit = AsyncMock()

    added_items = []

    def mock_add(item):
        added_items.append(item)

    mock_db.add.side_effect = mock_add

    project = Project(name="Test Project", owner_id=test_user.id)
    project.id = uuid.uuid4()

    # Dynamic side effect to return the correct objects based on query
    def mock_execute(statement, *args, **kwargs):
        stmt_str = str(statement).lower()
        if "from projects" in stmt_str or "projects.id" in stmt_str:
            return MockResult([project])
        elif "from failures" in stmt_str or "failures.id" in stmt_str:
            failures = [item for item in added_items if isinstance(item, Failure)]
            return MockResult(failures)
        elif "tag" in stmt_str:
            tags = [item for item in added_items if isinstance(item, Tag)]
            return MockResult(tags)
        return MockResult([])

    mock_db.execute.side_effect = mock_execute

    async def override_get_db():
        yield mock_db

    async def override_get_current_user():
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/failures",
            json={
                "project_id": str(project.id),
                "category": "security",
                "tech_stack": ["AWS", "Postgres"],
                "title": "Leaked AWS Credentials",
                "problem": "AWS credentials leaked in logs",
                "root_cause": "Hardcoded keys",
                "solution": "Use IAM Roles",
                "lesson_learned": "Never hardcode keys",
                "severity": "critical",
                "logs": "Connecting to postgresql://admin:super_secret@host:5432/db with token ghp_abc123XYZabc123XYZabc123XYZabc123XYZabc",
                "visibility": "public",
                "status": "published",
            },
            headers={"Authorization": "Bearer test-token"},
        )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Leaked AWS Credentials"
    assert data["status"] == "flagged"  # Flagged due to secrets scanner
    assert "super_secret" not in data["logs_redacted"]
    assert "ghp_abc" not in data["logs_redacted"]
    assert "<REDACTED>" in data["logs_redacted"]

