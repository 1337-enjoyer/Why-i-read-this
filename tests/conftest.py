import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

BASE_URL = 'http://test'


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        yield ac
