import asyncio
from datetime import datetime, timedelta, timezone
from config.database import connect_to_database, close_database_connection
from models.user import User
from models.subscription import Subscription

async def main():
    await connect_to_database()

    # Create a user
    user = User(name="John Doe", email="john.doe@example.com", password="securepassword")
    await user.insert()
    print(f"User created with ID: {user.id}")

    sub1 = Subscription(
        name="Netflix",
        price=9.99,
        currency="USD",
        frequency="monthly",
        category="entertainment",
        payment_method="credit card",
        start_date=datetime.now(timezone.utc) - timedelta(days=15),
        user=user
    )

    await sub1.insert()
    print(f"Subscription created with ID: {sub1.id}")

    sub2 = Subscription(
        name="Spotify",
        price=89,
        currency="CZK",
        frequency="monthly",
        category="entertainment",
        payment_method="credit card",
        start_date=datetime.now(timezone.utc) - timedelta(days=40),
        user=user
    )

    await sub2.insert()
    print(f"Subscription created with ID: {sub2.id}")

    await close_database_connection()

if __name__ == "__main__":
    asyncio.run(main())