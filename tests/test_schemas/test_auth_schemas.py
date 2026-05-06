import pytest
from pydantic import ValidationError
from schemas.auth import SignUpRequest, SignInRequest


def test_signup_valid():
    req = SignUpRequest(name="Alice", email="alice@example.com", password="secret123")
    assert req.name == "Alice"
    assert req.email == "alice@example.com"


def test_signup_name_too_short():
    with pytest.raises(ValidationError):
        SignUpRequest(name="A", email="a@example.com", password="secret123")


def test_signup_name_too_long():
    with pytest.raises(ValidationError):
        SignUpRequest(name="A" * 51, email="a@example.com", password="secret123")


def test_signup_invalid_email():
    with pytest.raises(ValidationError):
        SignUpRequest(name="Alice", email="not-an-email", password="secret123")


def test_signup_password_too_short():
    with pytest.raises(ValidationError):
        SignUpRequest(name="Alice", email="alice@example.com", password="12345")


def test_signup_missing_required_fields():
    with pytest.raises(ValidationError):
        SignUpRequest(name="Alice")


def test_signin_valid():
    req = SignInRequest(email="alice@example.com", password="anypassword")
    assert req.email == "alice@example.com"
    assert req.password == "anypassword"


def test_signin_invalid_email():
    with pytest.raises(ValidationError):
        SignInRequest(email="not-an-email", password="anypassword")


def test_signin_missing_password():
    with pytest.raises(ValidationError):
        SignInRequest(email="alice@example.com")
