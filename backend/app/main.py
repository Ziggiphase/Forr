import sys
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine
from app.models.base import Base
from app.services.telegram_poller import poll_telegram

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB (in production, use Alembic directly)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    poller_task = asyncio.create_task(poll_telegram())
    yield
    poller_task.cancel()

app = FastAPI(
    title="Forr API",
    description="AI-powered business communication platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.businesses import router as businesses_router
from app.api.products import router as products_router
from app.api.webhooks import router as webhooks_router
from app.api.inbox import router as inbox_router
from app.api.analytics import router as analytics_router
from app.api.billing import router as billing_router
from app.api.notifications import router as notifications_router
from app.api.search import router as search_router

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(businesses_router, prefix="/api/v1/businesses", tags=["businesses"])
app.include_router(products_router, prefix="/api/v1/businesses", tags=["products"])
app.include_router(webhooks_router, prefix="/api/v1/webhooks", tags=["webhooks"])
app.include_router(inbox_router, prefix="/api/v1", tags=["inbox"])
app.include_router(analytics_router, prefix="/api/v1", tags=["analytics"])
app.include_router(billing_router, prefix="/api/v1", tags=["billing"])
app.include_router(notifications_router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(search_router, prefix="/api/v1/search", tags=["search"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/api/v1/health")
async def api_health_check():
    """API v1 health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}
