import unittest
from app.services import RabbitMQ, Broker
from app.services.broker import JsonSerializer
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
            message={'message': 'test'}
            )