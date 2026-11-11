from fastapi import FastAPI

app = FastAPI(
    title="HER AI",
    description="Your Personal AI Companion",
    version="0.1.0"
)


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
