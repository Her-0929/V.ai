import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.rate_limit import limiter
from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.conversations import router as conversations_router
from app.api.memories import router as memories_router
from app.api.profile import router as profile_router

from app.core.database import SessionLocal
from app.services.ingestion.worker import job_worker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan handler: runs watchdog recovery of interrupted background jobs on startup."""
    try:
        db = SessionLocal()
        recovered = job_worker.recover_stuck_jobs(db)
        if recovered > 0:
            logging.info("Startup watchdog: Recovered %d stalled ingestion jobs.", recovered)
        db.close()
    except Exception as exc:
        logging.warning("Startup watchdog warning: %s", exc)
    yield


app = FastAPI(
    title="HER AI",
    description="Your Personal AI Companion — a thoughtful, memory-aware, emotionally intelligent AI.",
    version="0.4.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Rate Limiter state & exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — Environment-specific allowed origins + any vercel preview
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_cors_origins,
    allow_origin_regex=r"^https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(conversations_router)
app.include_router(memories_router)
app.include_router(profile_router)


@app.get("/", tags=["System"])
async def root():
    return {
        "name": "HER AI",
        "version": "0.4.0",
        "status": "running",
        "description": "Your Personal AI Companion",
        "endpoints": {
            "docs": "/docs",
            "auth": "/api/auth",
            "chat": "POST /api/chat",
            "conversations": "/api/conversations",
            "memories": "/api/memories",
            "profile": "/api/profile",
            "health": "/health",
        },
    }


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "version": "0.4.0"}
