import json
from typing import Union
from app.cache import get_cache
from app.database import get_db
from app.types import VerificationCodeField
from app.services.notification import SMSNotification
from app.database import errors
from app.models.verification import (
    LegalUserCodeVerificationIn, RealUserCodeVerificationIn,
    LegalUserSendSMSCodeIn, RealUserSendSMSCodeIn,
)

class InvalidVerificationCode(Exception):
    pass

class SMSVerificationService:
    def __init__(self, notification: SMSNotification):
        self.notification = notification
        self.cache = get_cache ()
        self.database = get_db() 
 
    def set(self, phone: str, extra_info, code: VerificationCodeField, expire_time=360):
        self.cache.set(phone, {"code": code, "extra": extra_info}, expire_time)
    
    def get(self, phone: str) -> Union[dict, None]:
        return self.cache.get(phone)

    def delete(self, phone):
        self.cache.delete(phone)

    def __get_extra_info(self, v: Union[RealUserSendSMSCodeIn, LegalUserSendSMSCodeIn]) -> str:
        if isinstance(v, LegalUserSendSMSCodeIn):
            return v.company_code
        return v.national_code

    def check_already_exist(self, v: Union[RealUserSendSMSCodeIn, LegalUserSendSMSCodeIn]) -> bool:
        info = self.get(v.phone_number)
        if info and info['extra'] == self.__get_extra_info(v):
            return True
        return False

    def verify(self, v: Union[RealUserCodeVerificationIn, LegalUserCodeVerificationIn], delete_on_success: bool = False):
        """ Raise on invalid verification. """
        info = self.get(v.phone_number)
        if info and info['code'] == v.code and info['extra'] == self.__get_extra_info(v):
            if delete_on_success:
                self.delete(v.phone_number)
                return
            
        raise InvalidVerificationCode()

    def send(self, v: Union[RealUserSendSMSCodeIn, LegalUserSendSMSCodeIn]):
        """ Send verification code. """
        code = VerificationCodeField.generate_new()
        extra_info = self.__get_extra_info(v)
        self.set(v.phone_number, extra_info, code)
        self.notification.send(v.phone_number, f"verification code: {code}")
         

    def verify_and_validate(self, v: Union[RealUserCodeVerificationIn, LegalUserCodeVerificationIn], delete_on_success: bool = False):
        """ Shortcut for validating and verifying. """
        self.validate_model(v)
        return self.verify(v, delete_on_success=delete_on_success)

    def validate_model(self, v: Union[RealUserSendSMSCodeIn, LegalUserSendSMSCodeIn]):
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
