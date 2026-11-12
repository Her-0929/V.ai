
from fastapi import FastAPI

from app.api.chat import router as chat_router


app = FastAPI(
    title="HER AI",
    description="Your Personal AI Companion",
    version="0.1.0"
)


# Register API routes
app.include_router(chat_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to HER AI",
        "status": "running",
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }
