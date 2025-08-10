from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.mqtt import MQTTService
from app.api.v1.router import mailer_router

setup_logging(
    level=settings.log_level,
    log_file=settings.log_file
)

mqtt_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global mqtt_service
    try:
        mqtt_service = MQTTService()
        await mqtt_service.connect()
        print("MQTT service started successfully")
    except Exception as e:
        print(f"Failed to start MQTT service: {e}")
        mqtt_service = None
    
    yield
    
    # Shutdown
    if mqtt_service:
        try:
            await mqtt_service.disconnect()
            print("MQTT service stopped successfully")
        except Exception as e:
            print(f"Warning: Error stopping MQTT service: {e}")


app = FastAPI(
    title="Mailer Service",
    version=settings.version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
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
    mqtt_status = "connected" if mqtt_service and mqtt_service.connected else "disconnected"
    return { 
        "status": "ok",
        "mqtt": mqtt_status
    }