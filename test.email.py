import asyncio
from datetime import datetime, timedelta, timezone
from config.database import connect_to_database, close_database_connection
from models.subscription import Subscription
from utils.send_email import send_reminder_email


async def main():
    await connect_to_database()
    
    # Find any subscription in the database
    sub = await Subscription.find_one(fetch_links=True)
    if not sub:
        print("No subscriptions found — create one first")
        return
    
    print(f"Sending test email about subscription: {sub.name}")
    await send_reminder_email(
        to="firstonechannel96@gmail.com",  # change this!
        type="7_day_reminder",
        subscription=sub,
    )
    print("Email sent — check your inbox")
    
    await close_database_connection()


asyncio.run(main())