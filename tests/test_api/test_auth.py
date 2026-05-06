import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")

SIGN_UP = "/api/v1/auth/sign-up"
SIGN_IN = "/api/v1/auth/sign-in"
SIGN_OUT = "/api/v1/auth/sign-out"


async def test_sign_up_returns_token_and_user(api_client: AsyncClient):
    response = await api_client.post(SIGN_UP, json={
        "name": "Alice", "email": "alice@example.com", "password": "secret123",
    })
    assert response.status_code == 201
    data = response.json()
    assert "token" in data
    assert data["user"]["email"] == "alice@example.com"
    assert data["user"]["name"] == "Alice"
    assert "id" in data["user"]


async def test_sign_up_duplicate_email_returns_400(api_client: AsyncClient):
    payload = {"name": "Bob", "email": "bob-dup@example.com", "password": "secret123"}
    await api_client.post(SIGN_UP, json=payload)
    response = await api_client.post(SIGN_UP, json=payload)
    assert response.status_code == 400


async def test_sign_up_invalid_email_returns_422(api_client: AsyncClient):
    response = await api_client.post(SIGN_UP, json={
        "name": "Alice", "email": "not-an-email", "password": "secret123",
    })
    assert response.status_code == 422


async def test_sign_up_name_too_short_returns_422(api_client: AsyncClient):
    response = await api_client.post(SIGN_UP, json={
        "name": "A", "email": "short@example.com", "password": "secret123",
    })
    assert response.status_code == 422


async def test_sign_up_password_too_short_returns_422(api_client: AsyncClient):
    response = await api_client.post(SIGN_UP, json={
        "name": "Alice", "email": "alice-pw@example.com", "password": "123",
    })
    assert response.status_code == 422


async def test_sign_in_success_returns_token(api_client: AsyncClient):
    await api_client.post(SIGN_UP, json={
        "name": "Carol", "email": "carol@example.com", "password": "secret123",
    })
    response = await api_client.post(SIGN_IN, json={
        "email": "carol@example.com", "password": "secret123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["user"]["email"] == "carol@example.com"


async def test_sign_in_wrong_password_returns_401(api_client: AsyncClient):
    await api_client.post(SIGN_UP, json={
        "name": "Dave", "email": "dave@example.com", "password": "correct_pw",
    })
    response = await api_client.post(SIGN_IN, json={
        "email": "dave@example.com", "password": "wrong_pw",
    })
    assert response.status_code == 401


async def test_sign_in_nonexistent_user_returns_404(api_client: AsyncClient):
    response = await api_client.post(SIGN_IN, json={
        "email": "ghost@example.com", "password": "secret123",
    })
    assert response.status_code == 404


async def test_sign_out_returns_success(api_client: AsyncClient):
    response = await api_client.post(SIGN_OUT)
    assert response.status_code == 200
    assert response.json()["success"] is True
