import unittest
from app.services import RabbitMQ, Broker, MemoryBroker
from app.services.broker import JsonSerializer, Message
from app.core.config import settings


class TestSerializer(unittest.TestCase):
    def setUp(self) -> None:
        self.serializer = JsonSerializer()

    def test_encode(self):
        message = {
            'key': 'value'
        }

        encoded_message = self.serializer.encode(message)
        assert encoded_message == b'{"key": "value"}'

    def test_decode(self):
        encoded_message = b'{"key": "value"}'
        decoded_message = self.serializer.decode(encoded_message)
        assert decoded_message == {'key': 'value'}


class TestMemoryBroker(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.broker = MemoryBroker(delay=0.1)

    def process_message(self, message: dict) -> dict:
        assert message.get('key') == 'value'
        return message

    async def test_publish_and_consume(self):
        await self.broker.publish('queue_name', Message(body={'key': 'value'}))
        await self.broker.consume(None, queue_name='queue_name', on_message=self.process_message)


class TestRabbitMQBroker(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.broker: Broker = RabbitMQ(
            settings.rabbitmq.address,
            settings.rabbitmq.port,
            settings.rabbitmq.username,
            settings.rabbitmq.password
        )

    async def test_publish_message(self):
        await self.broker.publish(
            queue_name='test_authentication',
            message=Message({'message': 'test'})
        )
