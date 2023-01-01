import json
from typing import Union
from app.types import PhoneNumberField, VerificationCodeField
from app.services.notification import SMSNotification, Notification
from app.cache.connection import redis_connection_pool
from app.database import storage, errors
from redis import Redis
from app.models.verification import RealUserCodeVerificationIn, LegalUserCodeVerificationIn

 
class SMSVerificationWithExtraInfo:
    def __init__(self, phone: PhoneNumberField, extra_info: str, test: bool = False) -> None:
        self.redis = Redis(connection_pool=redis_connection_pool)
        self.phone = phone
        self.notification = SMSNotification(self.phone)
        self.extra_info = extra_info

    def set(self, code: VerificationCodeField, expire_time=360):
        self.redis.set(self.phone, json.dumps({'code': code, 'extra': self.extra_info}))
        self.redis.expire(self.phone, expire_time)
    
    def get(self) -> Union[dict, None]:
        info = self.redis.get(self.phone)
        if info:
            return json.loads(info)
        return None

    def delete(self):
        self.redis.delete(self.phone)

    def check_already_exist(self) -> bool:
        info = self.get()
        if info and info['extra'] == self.extra_info:
            return True
        return False

    def verify(self, code: VerificationCodeField) -> bool:
        info = self.get()
        if info and info['code'] == code and info['extra'] == self.extra_info:
            return True
        return False

    def send(self):
        code = VerificationCodeField.generate_new()
        self.set(code)
        self.notification.send(self.phone, f"verification code: {code}")


def get_service(
    verification: Union[RealUserCodeVerificationIn, LegalUserCodeVerificationIn]
    ) -> SMSVerificationWithExtraInfo:

    if hasattr(verification, 'company_code'):
        validate_verify_as_for_legal(verification)
        return SMSVerificationWithExtraInfo(verification.phone_number, verification.company_code)
    elif hasattr(verification, 'national_code'):
        validate_verify_as_for_real(verification)
        return SMSVerificationWithExtraInfo(verification.phone_number, verification.national_code)
    else:
        raise TypeError("invalid verification type format")


def verify_code(
    verification: Union[RealUserCodeVerificationIn, LegalUserCodeVerificationIn], 
    delete_code: bool = False) -> bool:

    service = get_service(verification)

    result = service.verify(verification.code)
    if delete_code and result:
        service.delete()

    return result


def validate_verify_as_for_legal(v: LegalUserCodeVerificationIn):
    if v.verify_as == 'EXISTENT_USER' and not storage.users.check_by_company_code(v.company_code):
        raise errors.UserDoesNotExist("user does not exist")
    elif v.verify_as == 'NEW_USER' and storage.users.check_by_company_code(v.company_code):
        raise errors.UserAlreadyExist('user already exist')


def validate_verify_as_for_real(v: RealUserCodeVerificationIn):
    if v.verify_as == 'EXISTENT_USER' and not storage.users.check_by_national_code(v.national_code):
        raise errors.UserDoesNotExist('user does not exist')
    elif v.verify_as == 'NEW_USER' and storage.users.check_by_national_code(v.national_code):
        raise errors.UserAlreadyExist('user already exist')
