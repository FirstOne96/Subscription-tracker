import asyncio
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from config.env import settings
from models.user import User
from models.subscription import Subscription


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def initialize_database() -> AsyncGenerator[None, None]:
    """
    Connect to a test database and initialize Beanie once per test session.
    This makes Document classes (User, Subscription) usable in tests.
    """
    # Use a separate database name for tests so we never accidentally
    # touch the development data.
    test_db_name = "subscription_db_test"
    
    # Build a Motor client from the same URI but pointing at the test DB.
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[test_db_name]
    
    await init_beanie(database=db, document_models=[User, Subscription])
    
    yield
    
    # Teardown: drop the test database so the next run starts clean.
    await client.drop_database(test_db_name)
    client.close()


@pytest_asyncio.fixture(autouse=True, loop_scope="session")
async def use_initialized_database(initialize_database):
    """
    Auto-applied fixture: every test depends on the database being initialized.
    The `autouse=True` means we don't have to list this in every test signature.
    """
    yield

@pytest_asyncio.fixture(autouse=True)
async def clean_collections():
    """Clean test collections before each test."""
    yield
    # Run after the test: delete all documents from these collections.
    await User.delete_all()
    await Subscription.delete_all()