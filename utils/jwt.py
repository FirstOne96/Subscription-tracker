import re
from datetime import timedelta, datetime, timezone
from jose import jwt
from config.env import settings


def parse_expiry(expiry_str: str) -> timedelta:
    """Parse a string like '1d', '7h', '30m' into a timedelta."""
    match = re.match(r"^(\d+)([dhm])$", expiry_str)
    if not match:
        raise ValueError(f"Invalid expiry format: {expiry_str}")
    value = int(match.group(1))
    unit = match.group(2)
    if unit == "d":
        return timedelta(days=value)
    if unit == "h":
        return timedelta(hours=value)
    if unit == "m":
        return timedelta(minutes=value)
    raise ValueError(f"Unsupported unit: {unit}")

def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + parse_expiry(settings.JWT_EXPIRES_IN)
    payload = {"userId": user_id, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")