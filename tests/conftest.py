from typing import AsyncGenerator
from unittest.mock import AsyncMock, patch
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from slowapi import Limiter

from config.env import settings
from models.user import User
from models.subscription import Subscription


def _noop_rate_limit(self, request, endpoint_func, in_middleware=False):
    """Replace Limiter._check_request_limit so rate limits never trigger in tests.
    Must set view_rate_limit on request.state — the decorator wrapper reads it afterward."""
    request.state.view_rate_limit = None


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def initialize_database() -> AsyncGenerator[None, None]:
    test_db_name = "subscription_db_test"
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[test_db_name]
    await init_beanie(database=db, document_models=[User, Subscription])
    yield
    await client.drop_database(test_db_name)
    client.close()


@pytest_asyncio.fixture(autouse=True, loop_scope="session")
async def use_initialized_database(initialize_database):
    yield


@pytest_asyncio.fixture(autouse=True)
async def clean_collections():
    yield
    await User.delete_all()
    await Subscription.delete_all()


@pytest_asyncio.fixture(scope="session")
async def api_client(initialize_database) -> AsyncGenerator[AsyncClient, None]:
    from app import app as fastapi_app

    with patch("app.connect_to_database", new=AsyncMock()), \
         patch("app.close_database_connection", new=AsyncMock()), \
         patch.object(Limiter, "_check_request_limit", new=_noop_rate_limit):
        async with AsyncClient(
            transport=ASGITransport(app=fastapi_app),
            base_url="http://test",
            follow_redirects=True,
        ) as client:
            yield client
