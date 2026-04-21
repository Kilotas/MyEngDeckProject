import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.db.models import Base
from src.core.deps import get_uow
from src.main import app
from src.uow.sqlalchemy import SQLAlchemyUoW

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(engine):
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return factory


@pytest_asyncio.fixture
async def client(session_factory):
    def override_uow():
        return SQLAlchemyUoW(session_factory)

    app.dependency_overrides[get_uow] = override_uow
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_client(client):
    """Клиент с зарегистрированным и залогиненным пользователем."""
    await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
    })
    resp = await client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "password123",
    })
    token = resp.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client
