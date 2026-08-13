import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from src.backend.main import app
from src.backend.database import Base
from src.backend.core.dependencies import get_current_admin_user, get_current_user, get_session
from src.backend.models.user import User

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/book_api_test"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine):
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session):
    async def override_get_session():
        yield db_session

    def override_get_current_admin_user():
        return User(user_id=999, email="test_admin@test.com", is_admin=True)

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_admin_user] = override_get_current_admin_user
    app.dependency_overrides[get_current_user] = override_get_current_admin_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()