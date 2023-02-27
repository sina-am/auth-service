import abc
import json
from typing import Callable
from aio_pika import Message, connect_robust, connect
from aio_pika.abc import AbstractIncomingMessage
from app.core.logging import logger


class Serializer(abc.ABC):
    @abc.abstractmethod
    def encode(self, message: dict) -> bytes:
        raise NotImplementedError
    
    @abc.abstractmethod
    def decode(self, message: bytes) -> dict:
        raise NotImplementedError
    

class JsonSerializer(Serializer):
    def encode(self, message: dict) -> bytes:
        return json.dumps(message).encode('utf-8')

    def decode(self, message: bytes) -> dict:
        return json.loads(message.decode('utf-8'))

class Broker(abc.ABC):
    @abc.abstractmethod
    async def ping(self): 
        """ Checks for broker health """
        raise NotImplementedError

    @abc.abstractmethod    
    async def consume(self, loop):
        raise NotImplementedError
    
    @abc.abstractmethod
    async def publish(self, queue_name: str, message: dict):
        raise NotImplementedError

class RabbitMQ(Broker):
    def __init__(self, 
                 address: str, 
                 port: int, 
                 username: str = "", 
                 password: str = "",
                 serializer: Serializer = JsonSerializer()
                 ) -> None:
        self.address = address
        self.port = port
        self.username = username
        self.password = password
        self.serializer = serializer

    async def ping(self):
        await connect(
            host=self.address,
            port=self.port, 
            login=self.username,
            password=self.password,
        )

    async def publish(self, queue_name: str, message: dict):
        connection = await connect_robust(
            host=self.address,
            port=self.port, 
            login=self.username,
            password=self.password
        )
        channel = await connection.channel()
        await channel.declare_queue(queue_name)
        await channel.default_exchange.publish(
            Message(
                body=self.serializer.encode(message),
                app_id=1,
            ), routing_key=queue_name
        )

    async def consume(self, loop, queue_name: str, on_message: Callable[[dict], dict]):
        connection = await connect_robust(
            host=self.address,
            port=self.port, 
            login=self.username,
            password=self.password,
            loop=loop
        )
        channel = await connection.channel()
        queue = await channel.declare_queue(queue_name)

        logger.info("Consuming from queue")
        async with queue.iterator() as iterator:
            message: AbstractIncomingMessage
            async for message in iterator:
                try:
                    async with message.process(requeue=False):
                        assert message.reply_to is not None

                        response = on_message(self.serializer.decode(message.body))

                        await self.exchange.publish(
                            Message(
                                body=self.serializer.encode(response),
                                content_type='json/application',
                                correlation_id=message.correlation_id,
                            ),
                            routing_key=message.reply_to,
                        )
                        logger.info("Request complete")
                except Exception:
                    logger.exception(f"Processing error for message {message}")