from datetime import datetime
import pytest
from pymongo.errors import DuplicateKeyError
from models.user import User

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_user_is_created_with_timestamps():
    user = User(name="Alice", email="alice-ts@example.com", password="hashed_pw")
    await user.insert()

    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)
    assert user.id is not None


async def test_duplicate_email_is_rejected():
    await User(name="Bob", email="bob-dup@example.com", password="hashed_pw").insert()

    with pytest.raises(DuplicateKeyError):
        await User(name="Bob2", email="bob-dup@example.com", password="hashed_pw").insert()


async def test_updated_at_changes_on_replace():
    user = User(name="Carol", email="carol-ts@example.com", password="hashed_pw")
    await user.insert()
    original_updated_at = user.updated_at

    user.name = "Carol Updated"
    await user.replace()

    assert user.updated_at >= original_updated_at


async def test_user_fields_are_stored_correctly():
    user = User(name="Dave", email="dave@example.com", password="hashed_pw")
    await user.insert()

    fetched = await User.get(user.id)
    assert fetched.name == "Dave"
    assert fetched.email == "dave@example.com"


async def test_find_user_by_email():
    user = User(name="Eve", email="eve@example.com", password="hashed_pw")
    await user.insert()

    found = await User.find_one(User.email == "eve@example.com")
    assert found is not None
    assert found.id == user.id


async def test_find_nonexistent_user_returns_none():
    result = await User.find_one(User.email == "ghost@example.com")
    assert result is None
