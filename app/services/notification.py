from abc import ABC, abstractmethod
from functools import cached_property

import requests
from app.core.logging import logger
from app.services.broker import Broker, Message


class SMSNotification(ABC):
    @abstractmethod
    async def send(self, phone: str, text: str):
        pass


class MelipayamakSMSNotification(SMSNotification):
    def __init__(self, phone: str, username: str, password: str) -> None:
        self.base_url = "https://rest.payamak-panel.com/api/SendSMS/%s"
        self.username = username
        self.password = password
        self.from_phone = phone

    def __post(self, url, data):
        r = requests.post(url, data)
        return r.json()

    @cached_property
    def __credentials(self):
        return {
            'username': self.username,
            'password': self.password
        }

    async def send(self, phone: str, text: str):
        url = self.base_url % ('SendSMS')
        data = {
            'to': phone,
            'from': self.from_phone,
            'text': text,
            'isFlash': False
        }
        return self.__post(url, {**data, **self.__credentials})


class ExternalSMSNotification(SMSNotification):
    """ Sends notifications to an external service 
        using a message broker 
    """

    def __init__(self, broker: Broker) -> None:
        self.broker = broker

    async def send(self, phone: str, text: str):
        await self.broker.publish(
            queue_name='notification',
            message=Message(
                body={
                    'phone_number': phone,
                    'message': text
                },
                type='sms'
            )
        )


class FakeSMSNotification(SMSNotification):
    async def send(self, phone: str, text: str):
        logger.info(f'message: {text} sended to {phone}')
