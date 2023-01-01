from asyncio.log import logger
import logging
from aio_pika import Message, connect_robust
from aio_pika.abc import AbstractIncomingMessage
from app.services.rpc.handler import request_handler
from app.core.logging import logger
from app.core.config import settings


async def consume(loop):
    connection = await connect_robust(
        host=settings.rabbitmq.address,
        port=settings.rabbitmq.port, 
        login=settings.rabbitmq.username,
        password=settings.rabbitmq.password,
        loop=loop
    )
    channel = await connection.channel()
    exchange = channel.default_exchange

    # Declaring queue
    queue = await channel.declare_queue("rpc_queue")
    logger.info("Awaiting RPC requests.")

    async with queue.iterator() as qiterator:
        message: AbstractIncomingMessage
        async for message in qiterator:
            try:
                async with message.process(requeue=False):
                    assert message.reply_to is not None

                    response = request_handler(message.body)

                    await exchange.publish(
                        Message(
                            body=response,
                            content_type='json/application',
                            correlation_id=message.correlation_id,
                        ),
                        routing_key=message.reply_to,
                    )
                    logger.info("Request complete")
            except Exception:
                logger.exception(f"Processing error for message {message}")