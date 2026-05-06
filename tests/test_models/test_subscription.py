from datetime import datetime, timedelta, timezone
import pytest
from pydantic import ValidationError
from models.subscription import Subscription
from models.user import User

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def _make_user(email: str) -> User:
    user = User(name="Test User", email=email, password="hashed")
    await user.insert()
    return user


async def _make_sub(user: User, **kwargs) -> Subscription:
    defaults = dict(
        name="Netflix",
        price=15.99,
        frequency="monthly",
        category="entertainment",
        payment_method="Visa",
        start_date=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    defaults.update(kwargs)
    sub = Subscription(**defaults, user=user)
    await sub.insert()
    return sub


# --- renewal_date computation ---

async def test_renewal_date_is_computed_when_missing():
    user = await _make_user("renewal-test@example.com")
    sub = await _make_sub(user, start_date=datetime.now(timezone.utc) - timedelta(days=10))
    assert sub.renewal_date == sub.start_date + timedelta(days=30)


async def test_explicit_renewal_date_is_not_overwritten():
    user = await _make_user("explicit-renewal@example.com")
    custom = datetime.now(timezone.utc) + timedelta(days=90)
    sub = await _make_sub(user, renewal_date=custom)
    assert sub.renewal_date == custom


async def test_daily_frequency_computes_one_day():
    user = await _make_user("daily-freq@example.com")
    start = datetime.now(timezone.utc) - timedelta(hours=1)
    sub = await _make_sub(user, frequency="daily", start_date=start)
    assert sub.renewal_date == start + timedelta(days=1)


async def test_weekly_frequency_computes_seven_days():
    user = await _make_user("weekly-freq@example.com")
    start = datetime.now(timezone.utc) - timedelta(hours=1)
    sub = await _make_sub(user, frequency="weekly", start_date=start)
    assert sub.renewal_date == start + timedelta(days=7)


async def test_yearly_frequency_computes_365_days():
    user = await _make_user("yearly-freq@example.com")
    start = datetime.now(timezone.utc) - timedelta(hours=1)
    sub = await _make_sub(user, frequency="yearly", category="education", start_date=start)
    assert sub.renewal_date == start + timedelta(days=365)


# --- status transitions ---

async def test_status_becomes_expired_when_renewal_date_is_in_past():
    user = await _make_user("expired-test@example.com")
    sub = await _make_sub(
        user, frequency="weekly",
        start_date=datetime.now(timezone.utc) - timedelta(days=30),
    )
    assert sub.status == "expired"


async def test_active_status_preserved_for_future_renewal():
    user = await _make_user("active-test@example.com")
    sub = await _make_sub(
        user,
        start_date=datetime.now(timezone.utc) - timedelta(hours=1),
        renewal_date=datetime.now(timezone.utc) + timedelta(days=30),
    )
    assert sub.status == "active"


async def test_cancelled_status_not_overridden_to_expired():
    user = await _make_user("cancelled-test@example.com")
    sub = await _make_sub(
        user,
        status="cancelled",
        start_date=datetime.now(timezone.utc) - timedelta(days=30),
    )
    assert sub.status == "cancelled"


async def test_cancelled_status_preserved_on_save():
    user = await _make_user("cancel-save@example.com")
    sub = await _make_sub(
        user,
        start_date=datetime.now(timezone.utc) - timedelta(hours=1),
        renewal_date=datetime.now(timezone.utc) + timedelta(days=5),
    )
    sub.status = "cancelled"
    await sub.save()
    assert sub.status == "cancelled"


# --- validator ---

async def test_future_start_date_raises_validation_error():
    with pytest.raises(ValidationError):
        Subscription(
            name="Future Sub",
            price=10.0,
            frequency="monthly",
            category="entertainment",
            payment_method="Visa",
            start_date=datetime.now(timezone.utc) + timedelta(days=1),
            user=None,
        )
