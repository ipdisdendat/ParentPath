"""Pytest configuration and fixtures"""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient

from api.main import app
from api.database import Base, get_db
from api.config import settings

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://parentpath:parentpath_dev_2024@localhost:5432/parentpath_test"


@pytest_asyncio.fixture
async def test_db():
    """Create test database session"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_db):
    """Create test HTTP client"""

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def mock_gemini(monkeypatch):
    """Mock Gemini API responses"""
    async def mock_parse_pdf(*args, **kwargs):
        return [
            {
                "type": "Event",
                "title": "Basketball practice",
                "description": "Weekly practice",
                "date": "2024-11-20",
                "time": "16:00",
                "audience_tags": ["grade_5", "Basketball"],
                "source_page": 1,
                "source_snippet": "Basketball practice on Nov 20 at 4pm",
                "confidence_score": 0.95,
                "reasoning": ""
            }
        ]

    async def mock_embed(*args, **kwargs):
        return [0.1] * 768

    async def mock_translate(*args, **kwargs):
        return args[0]  # Return original text

    monkeypatch.setattr("api.services.gemini_service.parse_pdf_newsletter", mock_parse_pdf)
    monkeypatch.setattr("api.services.gemini_service.generate_embedding", mock_embed)
    monkeypatch.setattr("api.services.gemini_service.translate_text", mock_translate)
