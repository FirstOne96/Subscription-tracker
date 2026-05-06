from datetime import datetime, timedelta, timezone
import pytest
from models.subscription import Subscription
from models.user import User

pytestmark = pytest.mark.asyncio(loop_scope="session")

async def test_renewal_date_is_computed_when_missing():
    """If renewal_date is not provided, the hook computes it on insert."""
    
    user = User(
        name="Test User",
        email="renewal-test@example.com",
        password="hashed",
    )
    await user.insert()
    
    sub = Subscription(
        name="Netflix",
        price=15.99,
        frequency="monthly",
        category="entertainment",
        payment_method="Visa",
        start_date=datetime.now(timezone.utc) - timedelta(days=10),
        user=user,
    )
    await sub.insert()
    
    # The hook should have set renewal_date to start_date + 30 days.
    expected = sub.start_date + timedelta(days=30)
    assert sub.renewal_date == expected


async def test_status_becomes_expired_when_renewal_date_is_in_past():
    """A subscription whose computed renewal date is in the past gets marked expired."""
    
    user = User(
        name="Test User",
        email="expired-test@example.com",
        password="hashed",
    )
    await user.insert()
    
    sub = Subscription(
        name="Old Sub",
        price=5.0,
        frequency="weekly",
        category="other",
        payment_method="Visa",
        start_date=datetime.now(timezone.utc) - timedelta(days=30),
        user=user,
    )
    await sub.insert()
    
    assert sub.status == "expired"