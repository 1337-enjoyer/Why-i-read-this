import pytest
import respx
from httpx import ASGITransport, AsyncClient, Response
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db

from app.models.user import User  # noqa: F401
from app.models.read_article import ReadArticle  # noqa: F401

BASE_URL = "http://test"
WIKI_API = "https://ru.wikipedia.org/w/api.php"

TEST_DATABASE_URL = (
    "postgresql+asyncpg://app:app_pass@localhost:5433/app_db_test"
)

engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)
TestingSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

WIKI_OK_PAYLOAD = {
    "query": {
        "pages": {
            "6984570": {
                "pageid": 6984570,
                "title": "Натюрморт с драпировкой",
                "extract": "«Натюрморт с драпировкой» — картина Поля Сезанна...",
                "thumbnail": {"source": "https://example.com/img.jpg"},
            }
        }
    }
}
WIKI_EMPTY_PAYLOAD = {"query": {"pages": {}}}


@pytest.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestingSessionLocal() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def mock_wiki_ok():
    with respx.mock:
        respx.get(WIKI_API).mock(
            return_value=Response(200, json=WIKI_OK_PAYLOAD)
        )
        yield


@pytest.fixture
def mock_wiki_empty():
    with respx.mock:
        respx.get(WIKI_API).mock(
            return_value=Response(200, json=WIKI_EMPTY_PAYLOAD)
        )
        yield
