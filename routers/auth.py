from fastapi import APIRouter, Request, status
from controllers.auth import sign_up, sign_in, sign_out
from middleware.rate_limit import limiter
from schemas.auth import SignUpRequest, SignInRequest, AuthResponse


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/sign-up",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/10 seconds")
async def sign_up_route(request: Request, body: SignUpRequest) -> AuthResponse:
    return await sign_up(body)


@router.post("/sign-in", response_model=AuthResponse)
@limiter.limit("5/10 seconds")
async def sign_in_route(request: Request, body: SignInRequest) -> AuthResponse:
    return await sign_in(body)


@router.post("/sign-out")
async def sign_out_route() -> dict:
    return await sign_out()