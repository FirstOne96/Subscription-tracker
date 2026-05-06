from fastapi_mail import MessageSchema, MessageType
from beanie import PydanticObjectId
from config.mail import mail
from models.subscription import Subscription
from models.user import User
from utils.email_templates import MailInfo, TEMPLATES


async def send_reminder_email(
    to: str,
    type: str,
    subscription: Subscription,
) -> None:
    if type not in TEMPLATES:
        raise ValueError(f"Unknown reminder type: {type}")
    
    # Resolve the linked user to get their name
    if not isinstance(subscription.user, User):
        await subscription.fetch_link(Subscription.user)
    
    info = MailInfo(
        user_name=subscription.user.name,
        subscription_name=subscription.name,
        renewal_date=subscription.renewal_date,
        plan_name=subscription.frequency,
        price=subscription.price,
        currency=subscription.currency,
        payment_method=subscription.payment_method,
    )
    
    subject, body = TEMPLATES[type](info)
    
    message = MessageSchema(
        subject=subject,
        recipients=[to],
        body=body,
        subtype=MessageType.html,
    )
    
    await mail.send_message(message)