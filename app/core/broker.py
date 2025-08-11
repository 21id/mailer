import asyncio
from typing import Callable
import aio_pika
from aio_pika import connect_robust

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class MessageBrokerManager:
    _connection: aio_pika.Connection | None = None
    _channel: aio_pika.Channel | None = None
    _queue: aio_pika.Queue | None = None

    async def connect(self, loop: asyncio.AbstractEventLoop, callback: Callable[[aio_pika.IncomingMessage], None]):
        try:
            self._connection = await connect_robust(
                host=settings.amqp_host,
                port=settings.amqp_port,
                login=settings.amqp_user,
                password=settings.amqp_password,
                virtualhost=settings.amqp_vhost,
                loop=loop,
            )
            self._channel = await self._connection.channel()
            
            await self._channel.set_qos(prefetch_count=1)
            
            self._queue = await self._channel.declare_queue(settings.amqp_queue, durable=False)
            
            logger.info(f"Connected to AMQP: {settings.amqp_host}:{settings.amqp_port}")
            logger.info(f"Queue declared: {settings.amqp_queue}")
            logger.info(f"Prefetch count set to 1")

            await self._queue.consume(callback)
            logger.info(f"Started consuming messages from queue: {settings.amqp_queue}")

            return self._connection
        except Exception as e:
            logger.error(f"Failed to connect to AMQP: {e}")
            raise e

    async def status(self) -> bool:
        if not self._connection:
            return False
        return not self._connection.is_closed

    async def close(self):
        try:
            if self._channel:
                await self._channel.close()
            if self._connection:
                await self._connection.close()
            logger.info("AMQP connection closed")
        except Exception as e:
            logger.error(f"Error closing AMQP connection: {e}")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()