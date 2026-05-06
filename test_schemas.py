from datetime import datetime, timezone, timedelta
from schemas.auth import SignUpRequest, SignInRequest, AuthResponse
from schemas.user import UserPublic
from schemas.subscription import SubscriptionCreate, SubscriptionResponse


# Valid sign-up
req = SignUpRequest(name="Alice", email="alice@example.com", password="password123")
print(req)

# Should reject short name
try:
    SignUpRequest(name="A", email="alice@example.com", password="password123")
    print("ERROR: should have rejected short name")
except Exception as e:
    print(f"Correctly rejected short name: {type(e).__name__}")

# Should reject malformed email
try:
    SignUpRequest(name="Alice", email="not-an-email", password="password123")
    print("ERROR: should have rejected bad email")
except Exception as e:
    print(f"Correctly rejected bad email: {type(e).__name__}")

# Valid subscription create
sub = SubscriptionCreate(
    name="Netflix",
    price=15.99,
    frequency="monthly",
    category="entertainment",
    payment_method="Visa",
    start_date=datetime.now(timezone.utc) - timedelta(days=10),
)
print(sub)