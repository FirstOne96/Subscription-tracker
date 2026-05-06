from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from config.database import connect_to_database, close_database_connection
from middleware.rate_limit import limiter
from middleware.error_handler import register_exception_handlers

from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.subscriptions import router as subscriptions_router
from routers.workflows import router as workflows_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_database()
    yield
    await close_database_connection()


app = FastAPI(
    title="Subscription Management API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Custom error handlers
register_exception_handlers(app)

# Routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(subscriptions_router)
app.include_router(workflows_router)


@app.get("/")
async def root():
    return {"title": "Subscription Management API"}