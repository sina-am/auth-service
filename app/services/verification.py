import abc
from typing import Union
import asyncio
from app.types import VerificationCodeField
from app.services.notification import SMSNotification
from app.database import errors, Database
from app.cache import Cache
from app.models.verification import (
    LegalUserCodeVerificationIn, RealUserCodeVerificationIn,
    LegalUserSendSMSCodeIn, RealUserSendSMSCodeIn,
)


class InvalidVerificationCodeError(Exception):
    pass


class VerificationCodeAlreadySendError(Exception):
    pass


class VerificationService(abc.ABC):
    @abc.abstractmethod
    async def verify(self, v: Union[RealUserCodeVerificationIn, LegalUserCodeVerificationIn], delete_on_success: bool = False):
        raise NotImplementedError

    @abc.abstractmethod
    async def send(self, v: Union[RealUserSendSMSCodeIn, LegalUserSendSMSCodeIn]):
        raise NotImplementedError


class FakeVerificationService(VerificationService):
    async def verify(self, v: Union[RealUserCodeVerificationIn, LegalUserCodeVerificationIn], delete_on_success: bool = False):
        return

    async def send(self, v: Union[RealUserSendSMSCodeIn, LegalUserSendSMSCodeIn]):
        return


class SMSVerificationService(VerificationService):
    def __init__(self, notification: SMSNotification, cache: Cache, db: Database):
        self.notification = notification
        self.cache = cache
        self.database = db

    def __set(self, phone: str, extra_info, code: VerificationCodeField, expire_time=360):
        self.cache.set(str(phone), {"code": code,
                       "extra": extra_info}, expire_time)

    def __get(self, phone: str) -> Union[dict, None]:
        return self.cache.get(str(phone))

    def __delete(self, phone):
        self.cache.delete(phone)

    def __get_extra_info(self, v: Union[RealUserSendSMSCodeIn, LegalUserSendSMSCodeIn]) -> str:
        if isinstance(v, LegalUserSendSMSCodeIn):
            return v.company_code
        return v.national_code

    def __validate(self, v: Union[RealUserSendSMSCodeIn, LegalUserSendSMSCodeIn]):
        if isinstance(v, LegalUserSendSMSCodeIn):
            return self.__validate_for_legal_user(v)
        return self.__validate_for_real_user(v)

    def __validate_for_legal_user(self, v: LegalUserSendSMSCodeIn):
        if v.verify_as == 'EXISTENT_USER':
            user = self.database.users.get_by_company_code(v.company_code)
            if user.phone_number == v.phone_number:
                return
            raise errors.UserDoesNotExist("user does not exist")
        elif v.verify_as == 'NEW_USER' and self.database.users.check_by_company_code(v.company_code):
            raise errors.UserAlreadyExist('user already exist')

    def __validate_for_real_user(self, v: RealUserSendSMSCodeIn):
        if v.verify_as == 'EXISTENT_USER':
            user = self.database.users.get_by_national_code(v.national_code)
            if user.phone_number == v.phone_number:
                return
            raise errors.UserDoesNotExist('user does not exist')
        elif v.verify_as == 'NEW_USER' and self.database.users.check_by_national_code(v.national_code):
            raise errors.UserAlreadyExist('user already exist')

    async def verify(self, v: Union[RealUserCodeVerificationIn, LegalUserCodeVerificationIn], delete_on_success: bool = False):
        """ Raise on invalid verification. """
        self.__validate(v)

        info = self.__get(v.phone_number)
        if info and info['code'] == v.code and info['extra'] == self.__get_extra_info(v):
            if delete_on_success:
                self.__delete(v.phone_number)
            return

        raise InvalidVerificationCodeError()

    async def send(self, v: Union[RealUserSendSMSCodeIn, LegalUserSendSMSCodeIn]):
        """ Send verification code. """
        self.__validate(v)
        info = self.__get(v.phone_number)
        if info and info['extra'] == self.__get_extra_info(v):
            raise VerificationCodeAlreadySendError(
                f"code already send to {v.phone_number}")

        code = VerificationCodeField.generate_new()
        extra_info = self.__get_extra_info(v)
        self.__set(v.phone_number, extra_info, code)
        asyncio.create_task(
            self.notification.send(
                v.phone_number, f"verification code: {code}")
        )
