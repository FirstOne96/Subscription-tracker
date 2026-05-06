from models.subscription import Subscription
from models.user import User
from schemas.subscription import SubscriptionCreate, SubscriptionResponse
from typing import List
from beanie import Insert, PydanticObjectId, Replace, SaveChanges, before_event
from bson.errors import InvalidId
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
from tasks.reminder import schedule_reminders

def to_response(sub: Subscription) -> SubscriptionResponse:
    return SubscriptionResponse(
        id=str(sub.id),
        name=sub.name,
        price=sub.price,
        currency=sub.currency,
        frequency=sub.frequency,
        category=sub.category,
        payment_method=sub.payment_method,
        status=sub.status,
        start_date=sub.start_date,
        renewal_date=sub.renewal_date,
        user_id=str(sub.user.id),
        created_at=sub.created_at,
        updated_at=sub.updated_at,
    )


async def get_subscriptions() -> List[SubscriptionResponse]:
    subs = await Subscription.find_all(fetch_links=True).to_list()
    return [to_response(sub) for sub in subs]


async def get_subscription(sub_id: str) -> SubscriptionResponse:
    try:
        oid = PydanticObjectId(sub_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid subscription ID")
    
    sub = await Subscription.get(oid, fetch_links=True)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return to_response(sub)

async def create_subscription(
    body: SubscriptionCreate,
    current_user: User,
) -> SubscriptionResponse:
    sub = Subscription(
        **body.model_dump(),
        user=current_user,
    )
    await sub.insert()
    
    # Schedule reminder emails as a background task
    schedule_reminders.delay(str(sub.id))
    
    return to_response(sub)


async def get_user_subscriptions(
    user_id: str,
    current_user: User,
) -> List[SubscriptionResponse]:
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You can only access your own subscriptions",
        )
    
    try:
        oid = PydanticObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    subs = await Subscription.find(Subscription.user.id == oid, fetch_links=True).to_list()
    return [to_response(sub) for sub in subs]


async def get_upcoming_renewals() -> List[SubscriptionResponse]:
    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(days=7)
    
    subs = await Subscription.find(
        Subscription.status == "active",
        Subscription.renewal_date <= cutoff,
        Subscription.renewal_date >= now,
        fetch_links=True,
    ).to_list()
    
    return [to_response(sub) for sub in subs]


async def cancel_subscription(sub_id: str) -> SubscriptionResponse:
    try:
        oid = PydanticObjectId(sub_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid subscription ID")
    
    sub = await Subscription.get(oid, fetch_links=True)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    sub.status = "cancelled"
    await sub.save()
    return to_response(sub)


@before_event(Insert, Replace, SaveChanges)
async def compute_renewal_and_status(self):
    days = {"daily": 1, "weekly": 7, "monthly": 30, "yearly": 365}[self.frequency]
    if self.renewal_date is None:
        self.renewal_date = self.start_date + timedelta(days=days)
    
    # Don't override an explicit "cancelled" status
    if self.status != "cancelled" and self.renewal_date < datetime.now(timezone.utc):
        self.status = "expired"

        
