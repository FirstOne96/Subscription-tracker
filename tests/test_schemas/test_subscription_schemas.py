import pytest
from datetime import datetime, timedelta, timezone
from pydantic import ValidationError
from schemas.subscription import SubscriptionCreate


def _base(**overrides) -> dict:
    data = dict(
        name="Netflix",
        price=15.99,
        currency="USD",
        frequency="monthly",
        category="entertainment",
        payment_method="Visa",
        start_date=datetime.now(timezone.utc) - timedelta(days=1),
    )
    data.update(overrides)
    return data


def test_subscription_create_valid():
    sub = SubscriptionCreate(**_base())
    assert sub.name == "Netflix"
    assert sub.price == 15.99
    assert sub.currency == "USD"


def test_subscription_create_default_currency_is_czk():
    data = _base()
    del data["currency"]
    sub = SubscriptionCreate(**data)
    assert sub.currency == "CZK"


def test_subscription_create_default_frequency_is_monthly():
    data = _base()
    del data["frequency"]
    sub = SubscriptionCreate(**data)
    assert sub.frequency == "monthly"


def test_subscription_create_renewal_date_defaults_to_none():
    sub = SubscriptionCreate(**_base())
    assert sub.renewal_date is None


def test_subscription_create_name_too_short():
    with pytest.raises(ValidationError):
        SubscriptionCreate(**_base(name="N"))


def test_subscription_create_name_too_long():
    with pytest.raises(ValidationError):
        SubscriptionCreate(**_base(name="N" * 51))


def test_subscription_create_negative_price():
    with pytest.raises(ValidationError):
        SubscriptionCreate(**_base(price=-1.0))


def test_subscription_create_zero_price_is_allowed():
    sub = SubscriptionCreate(**_base(price=0.0))
    assert sub.price == 0.0


def test_subscription_create_invalid_currency():
    with pytest.raises(ValidationError):
        SubscriptionCreate(**_base(currency="GBP"))


def test_subscription_create_invalid_frequency():
    with pytest.raises(ValidationError):
        SubscriptionCreate(**_base(frequency="quarterly"))


def test_subscription_create_invalid_category():
    with pytest.raises(ValidationError):
        SubscriptionCreate(**_base(category="gaming"))


def test_subscription_create_all_valid_currencies():
    for currency in ("USD", "EUR", "CZK", "UAH"):
        sub = SubscriptionCreate(**_base(currency=currency))
        assert sub.currency == currency


def test_subscription_create_all_valid_frequencies():
    for freq in ("daily", "weekly", "monthly", "yearly"):
        sub = SubscriptionCreate(**_base(frequency=freq))
        assert sub.frequency == freq


def test_subscription_create_explicit_renewal_date():
    renewal = datetime.now(timezone.utc) + timedelta(days=30)
    sub = SubscriptionCreate(**_base(renewal_date=renewal))
    assert sub.renewal_date == renewal
