import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")

SIGN_UP = "/api/v1/auth/sign-up"
SUBS = "/api/v1/subscriptions"


def _sub_payload(**overrides) -> dict:
    data = dict(
        name="Netflix",
        price=15.99,
        currency="USD",
        frequency="monthly",
        category="entertainment",
        payment_method="Visa",
        start_date=(datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
    )
    data.update(overrides)
    return data


async def _sign_up(api_client: AsyncClient, email: str) -> tuple[str, str]:
    """Returns (user_id, token)."""
    resp = await api_client.post(SIGN_UP, json={
        "name": "Test User", "email": email, "password": "secret123",
    })
    data = resp.json()
    return data["user"]["id"], data["token"]


async def _create_sub(api_client: AsyncClient, token: str, **overrides) -> dict:
    with patch("controllers.subscriptions.schedule_reminders"):
        resp = await api_client.post(
            SUBS,
            json=_sub_payload(**overrides),
            headers={"Authorization": f"Bearer {token}"},
        )
    return resp.json()


# --- auth guard ---

async def test_create_subscription_requires_auth(api_client: AsyncClient):
    response = await api_client.post(SUBS, json=_sub_payload())
    assert response.status_code == 403


# --- create ---

async def test_create_subscription_returns_201(api_client: AsyncClient):
    _, token = await _sign_up(api_client, "create-ok@example.com")
    with patch("controllers.subscriptions.schedule_reminders"):
        response = await api_client.post(
            SUBS, json=_sub_payload(),
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Netflix"
    assert data["status"] == "active"
    assert data["currency"] == "USD"
    assert "id" in data
    assert "renewal_date" in data


async def test_create_subscription_schedules_reminders(api_client: AsyncClient):
    _, token = await _sign_up(api_client, "reminder-check@example.com")
    with patch("controllers.subscriptions.schedule_reminders") as mock_task:
        await api_client.post(
            SUBS, json=_sub_payload(),
            headers={"Authorization": f"Bearer {token}"},
        )
    mock_task.delay.assert_called_once()


async def test_create_subscription_invalid_body_returns_422(api_client: AsyncClient):
    _, token = await _sign_up(api_client, "invalid-body@example.com")
    response = await api_client.post(
        SUBS,
        json={"name": "X", "price": -1, "currency": "INVALID"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


# --- get all ---

async def test_get_subscriptions_returns_list(api_client: AsyncClient):
    response = await api_client.get(SUBS)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_get_subscriptions_includes_created_ones(api_client: AsyncClient):
    _, token = await _sign_up(api_client, "get-all@example.com")
    await _create_sub(api_client, token)
    response = await api_client.get(SUBS)
    assert response.status_code == 200
    assert len(response.json()) >= 1


# --- get one ---

async def test_get_subscription_by_id(api_client: AsyncClient):
    _, token = await _sign_up(api_client, "get-one@example.com")
    created = await _create_sub(api_client, token)
    sub_id = created["id"]

    response = await api_client.get(f"{SUBS}/{sub_id}")
    assert response.status_code == 200
    assert response.json()["id"] == sub_id


async def test_get_subscription_invalid_id_returns_400(api_client: AsyncClient):
    response = await api_client.get(f"{SUBS}/not-a-valid-id")
    assert response.status_code == 400


async def test_get_subscription_not_found_returns_404(api_client: AsyncClient):
    response = await api_client.get(f"{SUBS}/000000000000000000000000")
    assert response.status_code == 404


# --- user subscriptions ---

async def test_get_user_subscriptions_requires_auth(api_client: AsyncClient):
    user_id, _ = await _sign_up(api_client, "user-subs-noauth@example.com")
    response = await api_client.get(f"{SUBS}/user/{user_id}")
    assert response.status_code == 403


async def test_get_user_subscriptions_returns_own_subs(api_client: AsyncClient):
    user_id, token = await _sign_up(api_client, "user-subs-ok@example.com")
    await _create_sub(api_client, token)

    response = await api_client.get(
        f"{SUBS}/user/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    subs = response.json()
    assert len(subs) == 1
    assert subs[0]["name"] == "Netflix"


async def test_get_user_subscriptions_rejects_other_user(api_client: AsyncClient):
    user_id, _ = await _sign_up(api_client, "user-a@example.com")
    _, other_token = await _sign_up(api_client, "user-b@example.com")

    response = await api_client.get(
        f"{SUBS}/user/{user_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert response.status_code == 401


# --- cancel ---

async def test_cancel_subscription_sets_status_cancelled(api_client: AsyncClient):
    _, token = await _sign_up(api_client, "cancel-me@example.com")
    created = await _create_sub(api_client, token)
    sub_id = created["id"]

    response = await api_client.put(f"{SUBS}/{sub_id}/cancel")
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


async def test_cancel_nonexistent_subscription_returns_404(api_client: AsyncClient):
    response = await api_client.put(f"{SUBS}/000000000000000000000000/cancel")
    assert response.status_code == 404


async def test_cancel_invalid_id_returns_400(api_client: AsyncClient):
    response = await api_client.put(f"{SUBS}/bad-id/cancel")
    assert response.status_code == 400


# --- upcoming renewals ---

async def test_get_upcoming_renewals_returns_list(api_client: AsyncClient):
    response = await api_client.get(f"{SUBS}/upcoming-renewals")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_upcoming_renewals_includes_sub_renewing_within_7_days(api_client: AsyncClient):
    _, token = await _sign_up(api_client, "upcoming@example.com")
    renewal = datetime.now(timezone.utc) + timedelta(days=3)
    await _create_sub(api_client, token, renewal_date=renewal.isoformat())

    response = await api_client.get(f"{SUBS}/upcoming-renewals")
    assert response.status_code == 200
    assert len(response.json()) >= 1


async def test_upcoming_renewals_excludes_sub_renewing_after_7_days(api_client: AsyncClient):
    _, token = await _sign_up(api_client, "far-renewal@example.com")
    renewal = datetime.now(timezone.utc) + timedelta(days=30)
    sub_data = await _create_sub(api_client, token, renewal_date=renewal.isoformat())

    response = await api_client.get(f"{SUBS}/upcoming-renewals")
    assert response.status_code == 200
    upcoming_ids = [s["id"] for s in response.json()]
    assert sub_data["id"] not in upcoming_ids
