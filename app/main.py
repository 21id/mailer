from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import mailer_router

app = FastAPI(
    title="Mailer Service",
    version=settings.version,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mailer_router, prefix="/api/v1")

@app.get(
    "/health",
    tags=["health"],
    summary="Health check",
)
async def health_check():
    return { "status": "ok" }