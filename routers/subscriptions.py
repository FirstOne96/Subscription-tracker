from typing import List
from fastapi import APIRouter, Depends, status, Request
from controllers.subscriptions import (
    get_subscriptions,
    get_subscription,
    get_user_subscriptions,
    get_upcoming_renewals,
    create_subscription,
    cancel_subscription,
)
from middleware.auth import get_current_user
from models.user import User
from schemas.subscription import SubscriptionCreate, SubscriptionResponse
from middleware.rate_limit import limiter


router = APIRouter(prefix="/api/v1/subscriptions", tags=["subscriptions"])


# Specific paths first
@router.get("/upcoming-renewals", response_model=List[SubscriptionResponse])
async def upcoming_renewals_route() -> List[SubscriptionResponse]:
    return await get_upcoming_renewals()


@router.get("/user/{user_id}", response_model=List[SubscriptionResponse])
async def get_user_subscriptions_route(
    user_id: str,
    current_user: User = Depends(get_current_user),
) -> List[SubscriptionResponse]:
    return await get_user_subscriptions(user_id, current_user)


@router.post(
    "/",
    response_model=SubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("30/1 minute")
async def create_subscription_route(
    request: Request,
    body: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
) -> SubscriptionResponse:
    return await create_subscription(body, current_user)


@router.get("/", response_model=List[SubscriptionResponse])
async def get_subscriptions_route() -> List[SubscriptionResponse]:
    return await get_subscriptions()


# Generic paths last
@router.put("/{sub_id}/cancel", response_model=SubscriptionResponse)
@limiter.limit("30/1 minute")
async def cancel_subscription_route(request: Request, sub_id: str) -> SubscriptionResponse:
    return await cancel_subscription(sub_id)


@router.get("/{sub_id}", response_model=SubscriptionResponse)
async def get_subscription_route(sub_id: str) -> SubscriptionResponse:
    return await get_subscription(sub_id)