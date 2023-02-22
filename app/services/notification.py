from abc import ABC, abstractmethod

from app.services.sms.melipayamak import Rest
from app.core.logging import logger


class SMSNotification(ABC):
    @abstractmethod
    def send(self, phone: str, message: str):
        pass


class MelipayamakSMSNotification(SMSNotification):
    def __init__(self, phone: str, username: str, password: str) -> None:
        self.from_phone = phone 
        self.provider = Rest(username, password)
        super().__init__()

    def send(self, phone: str, message: str):
        self.provider.send(phone, self.from_phone, message)
        
    
class FakeSMSNotification(SMSNotification):
    def send(self, phone: str, message: str):
        logger.info(f'message: {message} sended to {phone}')    