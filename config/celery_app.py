from celery import Celery
from config.env import settings


celery_app = Celery(
    "subscription_management",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["tasks.reminder"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)
