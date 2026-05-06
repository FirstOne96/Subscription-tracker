import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")

SIGN_UP = "/api/v1/auth/sign-up"
USERS = "/api/v1/users"


async def _sign_up(api_client: AsyncClient, name: str, email: str) -> dict:
    resp = await api_client.post(SIGN_UP, json={
        "name": name, "email": email, "password": "secret123",
    })
    return resp.json()


async def test_get_users_empty_initially(api_client: AsyncClient):
    response = await api_client.get(USERS)
    assert response.status_code == 200
    assert response.json() == []


async def test_get_users_returns_created_users(api_client: AsyncClient):
    await _sign_up(api_client, "Alice", "alice-list@example.com")
    response = await api_client.get(USERS)
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 1
    assert users[0]["email"] == "alice-list@example.com"


async def test_get_user_by_id_requires_auth(api_client: AsyncClient):
    data = await _sign_up(api_client, "Bob", "bob-noauth@example.com")
    user_id = data["user"]["id"]
    response = await api_client.get(f"{USERS}/{user_id}")
    assert response.status_code == 403


async def test_get_user_by_id_success(api_client: AsyncClient):
    data = await _sign_up(api_client, "Carol", "carol-byid@example.com")
    token = data["token"]
    user_id = data["user"]["id"]

    response = await api_client.get(
        f"{USERS}/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == user_id
    assert body["email"] == "carol-byid@example.com"
    assert body["name"] == "Carol"


async def test_get_user_invalid_id_returns_400(api_client: AsyncClient):
    data = await _sign_up(api_client, "Dave", "dave-badid@example.com")
    token = data["token"]

    response = await api_client.get(
        f"{USERS}/not-a-valid-object-id",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400


async def test_get_user_not_found_returns_404(api_client: AsyncClient):
    data = await _sign_up(api_client, "Eve", "eve-notfound@example.com")
    token = data["token"]
    fake_id = "000000000000000000000000"

    response = await api_client.get(
        f"{USERS}/{fake_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


async def test_create_user_endpoint_returns_501(api_client: AsyncClient):
    response = await api_client.post(USERS, json={})
    assert response.status_code == 501


async def test_update_user_endpoint_returns_501(api_client: AsyncClient):
    response = await api_client.put(f"{USERS}/000000000000000000000000", json={})
    assert response.status_code == 501


async def test_delete_user_endpoint_returns_501(api_client: AsyncClient):
    response = await api_client.delete(f"{USERS}/000000000000000000000000")
    assert response.status_code == 501
