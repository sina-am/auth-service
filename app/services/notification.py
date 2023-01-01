from abc import ABC, abstractmethod

from app.services.sms.melipayamak import Rest
from app.core.config import settings
from app.core.logging import logger


class Notification(ABC):
    @abstractmethod
    def send(self, phone: str, message: str):
        pass


class SMSNotification(Notification):
    def __init__(self) -> None:
        self.from_phone = settings.melipayamak.phone
        self.provider = Rest(settings.melipayamak.username, settings.melipayamak.password)
        super().__init__()

    def send(self, phone: str, message: str):
        self.provider.send(phone, self.from_phone, message)
        
    
class FakeSMSNotification(Notification):
    def send(self, phone: str, message: str):
        logger.info(f'message: {message} sended to {phone}')    