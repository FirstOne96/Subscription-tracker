from dataclasses import dataclass
from datetime import datetime


@dataclass
class MailInfo:
    user_name: str
    subscription_name: str
    renewal_date: datetime
    plan_name: str
    price: float
    currency: str
    payment_method: str


def reminder_7_day(info: MailInfo) -> tuple[str, str]:
    subject = f"Your {info.subscription_name} subscription renews in 7 days"
    body = f"""
    <h2>Hi {info.user_name},</h2>
    <p>This is a friendly reminder that your <strong>{info.subscription_name}</strong>
    subscription is set to renew on <strong>{info.renewal_date.strftime('%B %d, %Y')}</strong>.</p>
    <ul>
        <li>Plan: {info.plan_name}</li>
        <li>Price: {info.price} {info.currency}</li>
        <li>Payment method: {info.payment_method}</li>
    </ul>
    <p>If you no longer wish to renew, you can cancel through your account settings.</p>
    """
    return subject, body


def reminder_5_day(info: MailInfo) -> tuple[str, str]:
    subject = f"Your {info.subscription_name} subscription renews in 5 days"
    body = f"""
    <h2>Hi {info.user_name},</h2>
    <p>Just a quick heads-up that your <strong>{info.subscription_name}</strong>
    subscription will renew on <strong>{info.renewal_date.strftime('%B %d, %Y')}</strong>.</p>
    <ul>
        <li>Plan: {info.plan_name}</li>
        <li>Price: {info.price} {info.currency}</li>
        <li>Payment method: {info.payment_method}</li>
    </ul>
    <p>If you'd like to make any changes before then, you can do so in your account settings.</p>
    """
    return subject, body


def reminder_2_day(info: MailInfo) -> tuple[str, str]:
    subject = f"Your {info.subscription_name} subscription renews in 2 days"
    body = f"""
    <h2>Hi {info.user_name},</h2>
    <p>Your <strong>{info.subscription_name}</strong> subscription is scheduled to renew on
    <strong>{info.renewal_date.strftime('%B %d, %Y')}</strong>.</p>
    <ul>
        <li>Plan: {info.plan_name}</li>
        <li>Price: {info.price} {info.currency}</li>
        <li>Payment method: {info.payment_method}</li>
    </ul>
    <p>Please review your subscription settings soon if you'd like to update or cancel it.</p>
    """
    return subject, body


def reminder_1_day(info: MailInfo) -> tuple[str, str]:
    subject = f"Final reminder: your {info.subscription_name} subscription renews tomorrow"
    body = f"""
    <h2>Hi {info.user_name},</h2>
    <p>This is your final reminder that your <strong>{info.subscription_name}</strong>
    subscription renews on <strong>{info.renewal_date.strftime('%B %d, %Y')}</strong>.</p>
    <ul>
        <li>Plan: {info.plan_name}</li>
        <li>Price: {info.price} {info.currency}</li>
        <li>Payment method: {info.payment_method}</li>
    </ul>
    <p>If you want to make changes before the renewal, please do so now in your account settings.</p>
    <p>Thanks for using SubDub!</p>
    """
    return subject, body


TEMPLATES = {
    "7_day_reminder": reminder_7_day,
    "5_day_reminder": reminder_5_day,
    "2_day_reminder": reminder_2_day,
    "1_day_reminder": reminder_1_day,
}