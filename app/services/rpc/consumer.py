from aio_pika import Message, connect_robust, connect
from aio_pika.abc import AbstractIncomingMessage
from app.services.rpc.handler import request_handler
from app.core.logging import logger
from app.core.config import settings


class RabbitMQ:
    def __init__(self, address: str, port: int, username: str = "", password: str = "") -> None:
        self.address = address
        self.port = port
        self.username = username
        self.password = password

    async def ping(self):
        await connect(
            host=self.address,
            port=self.port, 
            login=self.username,
            password=self.password,
        )

    async def consume(self, loop):
        self.connection = await connect_robust(
            host=self.address,
            port=self.port, 
            login=self.username,
            password=self.password,
            loop=loop
        )
        self.channel = await self.connection.channel()
        self.exchange = self.channel.default_exchange   
        self.queue = await self.channel.declare_queue("rpc_auth")

        logger.info("Consuming from queue")
        async with self.queue.iterator() as qiterator:
            message: AbstractIncomingMessage
            async for message in qiterator:
                try:
                    async with message.process(requeue=False):
                        assert message.reply_to is not None

                        response = request_handler(message.body)

                        await self.exchange.publish(
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