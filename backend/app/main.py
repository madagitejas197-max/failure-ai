"""
FailureAI — FastAPI application entry point.

Registers:
  - Middleware (CORS)
  - Routers
  - Lifespan hooks (DB connectivity check on startup)
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import get_settings
from app.database import engine
from app.routers import health

settings = get_settings()


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup checks then yield control to FastAPI."""
    # Verify database connection on startup
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ Database connection OK")
    except Exception as exc:
        print(f"⚠️  Database not reachable on startup: {exc}")
        print("   The app will start but DB-dependent endpoints will fail.")
    yield
    # Teardown: dispose connection pool
    await engine.dispose()
    print("🛑 Database connection pool closed")


# ── Application ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    description=(
        "AI-powered Software Failure Intelligence Platform — "
        "learn from software failures before they repeat."
    ),
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
