import asyncio
from contextlib import asynccontextmanager
import aio_pika
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.controller import MailerController
from app.core.broker import MessageBrokerManager
from app.core.config import settings
from app.api.v1.router import mailer_router
from app.core.logging import get_logger, setup_logging
from app.models.email import EmailRequest

setup_logging(
    level="DEBUG"
)

logger = get_logger(__name__)
manager = MessageBrokerManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    async def callback(message: aio_pika.IncomingMessage):
        async with message.process():
            body = message.body.decode()
            try:
                mail = EmailRequest.model_validate_json(body)
                await MailerController.send_email(mail)
            except Exception as e:
                logger.error(f"Failed to process message: {e}")

    try:
        loop = asyncio.get_running_loop()
        await manager.connect(loop, callback)
        logger.info("Message broker started successfully")
        yield
        
    except Exception as e:
        logger.error(f"Failed to start message broker: {e}")
        raise
    finally:
        await manager.close()
        logger.info("Message broker stopped")

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
    return { 
        "status": "ok",
        "broker_status": await manager.status(),
    }