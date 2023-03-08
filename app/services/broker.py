import abc
import asyncio
import json
import uuid
from dataclasses import dataclass
from typing import Callable, Any, Dict, Union
from aio_pika import Message as PikaMessage, connect_robust, connect
from aio_pika.abc import AbstractIncomingMessage
from app.core.logging import logger


@dataclass
class Message:
    body: Any
    content_type: str = "application/json"
    content_encoding: str = ""
    id: uuid.UUID = uuid.uuid4()
    type: Union[str, None] = None


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
    async def ping(self) -> bool:
        """ Checks for broker health """
        raise NotImplementedError

    @abc.abstractmethod
    async def consume(self, loop, queue_name: str, on_message: Callable[[dict], dict]):
        raise NotImplementedError

    @abc.abstractmethod
    async def publish(self, queue_name: str, message: Message):
        raise NotImplementedError


class MemoryBroker(Broker):
    def __init__(self, delay: float = 1) -> None:
        self.delay = delay
        self.queues: Dict[str, Any] = {}

    async def ping(self):
        return True

    async def consume(self, loop, queue_name: str, on_message: Callable[[dict], dict]):
        for i in range(5):
            await asyncio.sleep(self.delay)
            queue = self.queues.get(queue_name)
            if not queue or len(queue) == 0:
                continue
            on_message(queue.pop(0))

    async def publish(self, queue_name: str, message: Message):
        if not self.queues.get(queue_name):
            self.queues[queue_name] = []

        self.queues[queue_name].append(message.body)


class RabbitMQ(Broker):
    def __init__(self,
                 address: str,
                 port: int,
                 username: str = "",
                 password: str = "",
                 serializers: Union[Dict[str, Serializer], None] = None
                 ) -> None:
        self.address = address
        self.port = port
        self.username = username
        self.password = password
        if serializers:
            self.serializers = serializers
        else:
            self.serializers = self.get_default_serializers()

    def get_default_serializers(self) -> Dict[str, Serializer]:
        return {
            'application/json': JsonSerializer(),
        }

    async def ping(self) -> bool:
        try:
            await connect(
                host=self.address,
                port=self.port,
                login=self.username,
                password=self.password,
            )
            return True
        except Exception:
            return False

    async def publish(self, queue_name: str, message: Message):
        connection = await connect_robust(
            host=self.address,
            port=self.port,
            login=self.username,
            password=self.password
        )
        channel = await connection.channel()
        await channel.declare_queue(queue_name)
        await channel.default_exchange.publish(
            PikaMessage(
                message_id=message.id.hex,
                body=self.serializers[message.content_type].encode(
                    message.body),
                content_type=message.content_type,
                type=message.type,
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
                        assert message.reply_to
                        assert message.content_type

                        response = on_message(
                            self.serializers[message.content_type].decode(message.body))

                        await channel.default_exchange.publish(
                            PikaMessage(
                                body=self.serializers["application/json"].encode(
                                    response),
                                content_type='json/application',
                                correlation_id=message.correlation_id,
                            ),
                            routing_key=message.reply_to,
                        )
                        logger.info("Request complete")
                except Exception:
                    logger.exception(f"Processing error for message {message}")
