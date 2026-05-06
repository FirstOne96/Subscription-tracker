import asyncio
from datetime import datetime, timedelta, timezone
from beanie import PydanticObjectId
from celery import Celery
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from config.celery_app import celery_app
from config.env import settings
from models.subscription import Subscription
from models.user import User
from utils.send_email import send_reminder_email


def run_async(coro):
    """Run an async coroutine to completion in a Celery worker context."""
    return asyncio.run(coro)


async def init_db_for_task():
    """Initialize Beanie inside a Celery task. Each task call gets fresh DB connection."""
    client = AsyncIOMotorClient(settings.MONGODB_URI, tz_aware=True)
    db = client.get_default_database()
    await init_beanie(database=db, document_models=[User, Subscription])
    return client


@celery_app.task(name="schedule_reminders")
def schedule_reminders(subscription_id: str) -> None:
    """Schedule reminder emails for a subscription at 7, 5, 2, and 1 days before renewal."""
    
    async def _run():
        client = await init_db_for_task()
        try:
            sub = await Subscription.get(PydanticObjectId(subscription_id), fetch_links=True)
            if not sub:
                print(f"[schedule_reminders] subscription {subscription_id} not found")
                return
            
            if sub.status != "active":
                print(f"[schedule_reminders] subscription {subscription_id} is not active, skipping")
                return
            
            now = datetime.now(timezone.utc)
            if sub.renewal_date <= now:
                print(f"[schedule_reminders] renewal date is in the past, skipping")
                return
            
            for days_before in [7, 5, 2, 1]:
                reminder_dt = sub.renewal_date - timedelta(days=days_before)
                if reminder_dt <= now:
                    continue
                
                send_reminder_email_task.apply_async(
                    args=[subscription_id, f"{days_before}_day_reminder"],
                    eta=reminder_dt,
                )
                print(f"[schedule_reminders] scheduled {days_before}-day reminder for {reminder_dt}")
        finally:
            client.close()
    
    run_async(_run())


@celery_app.task(name="send_reminder_email_task")
def send_reminder_email_task(subscription_id: str, reminder_type: str) -> None:
    """Send a reminder email for a subscription. Re-validates active status before sending."""
    
    async def _run():
        client = await init_db_for_task()
        try:
            sub = await Subscription.get(PydanticObjectId(subscription_id), fetch_links=True)
            if not sub:
                print(f"[send_reminder_email_task] subscription {subscription_id} not found")
                return
            
            if sub.status != "active":
                print(f"[send_reminder_email_task] subscription is no longer active, skipping")
                return
            
            recipient = sub.user.email
            await send_reminder_email(to=recipient, type=reminder_type, subscription=sub)
            print(f"[send_reminder_email_task] sent {reminder_type} to {recipient}")
        finally:
            client.close()
    
    run_async(_run())