import asyncio
import json
import uuid
from typing import MutableMapping

from aio_pika import Message, connect_robust
from aio_pika.abc import (AbstractChannel, AbstractConnection, AbstractIncomingMessage, AbstractQueue)
from app.core.config import settings


class AuthenticationRpcClient:
    connection: AbstractConnection
    channel: AbstractChannel
    callback_queue: AbstractQueue
    loop: asyncio.AbstractEventLoop

    def __init__(self) -> None:
        self.futures: MutableMapping[str, asyncio.Future] = {}
        self.loop = asyncio.get_running_loop()

    async def connect(self) -> "AuthenticationRpcClient":
        self.connection = await connect_robust(
            host=settings.rabbitmq.address,
            port=settings.rabbitmq.port, 
            login=settings.rabbitmq.username,
            password=settings.rabbitmq.password,
            loop=self.loop
        )
        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue(exclusive=True)
        await self.callback_queue.consume(self.on_response)

        return self

    def on_response(self, message: AbstractIncomingMessage) -> None:
        if message.correlation_id is None:
            print(f"Bad message {message!r}")
            return

        future: asyncio.Future = self.futures.pop(message.correlation_id)
        future.set_result(message.body)

    async def call(self, token: str) -> int:
        correlation_id = str(uuid.uuid4())
        future = self.loop.create_future()

        self.futures[correlation_id] = future

        await self.channel.default_exchange.publish(
            Message(
                str(token).encode(),
                content_type="text/plain",
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name,
            ),
            routing_key="rpc_queue",
        )
        return await future


async def authenticate_rpc(token: str):
    auth_rpc = await AuthenticationRpcClient().connect()
    return await auth_rpc.call(json.dumps({
        'service_name': 'jwt_verification',
        'type': 'Bearer',
        'token': token
    }))
