from random import randint
import re
from typing import NewType
from bson import ObjectId

from pydantic import constr
from app.utils.translation import _

from enum import Enum


class StrEnum(str, Enum):
    pass


class UserType(StrEnum):
    LEGAL = "LEGAL"
    REAL = "REAL"


class Gender(StrEnum):
    male = "MALE"
    female = "FEMALE"


GenderField = NewType('GenderField', Gender)
UserTypeField = NewType('UserTypeField', UserType)
CityNameField = constr(to_lower=True)
ProvinceNameField = constr(to_lower=True)


class BaseField(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    def __repr__(self):
        return f'{self.__class__.__name__}({super().__repr__()})'


class ObjectIdField(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        try:
            return ObjectId(str(v))
        except Exception:
            raise ValueError("not a valid ObjectId")


class CompanyCodeField(BaseField):
    """
    Validator for Company code
    """
    company_code_regex = re.compile(r'[0-9]{11}$')

    @classmethod
    def validate(cls, v):
        # skip validation if it's already validated
        if isinstance(v, CompanyCodeField):
            return v
        if not isinstance(v, str):
            raise TypeError('string required')
        m = cls.company_code_regex.fullmatch(v)
        if not m:
            raise ValueError(_('invalid company code format'))

        return cls(m.group(0))


class NationalCodeField(BaseField):
    """
    Validator for Iran national code
    """
    national_code_regex = re.compile(r'[0-9]{10}$')

    @classmethod
    def validate(cls, v):
        # skip validation if it's already validated
        if isinstance(v, NationalCodeField):
            return v
        if not isinstance(v, str):
            raise TypeError('string required')
        m = cls.national_code_regex.fullmatch(v)
        if not m:
            raise ValueError(_('invalid national code format'))

        return cls(m.group(0))


class PostCodeField(BaseField):
    """
    Validator for Iran post code
    """
    post_code_regex = re.compile(r'[0-9]{11}$')

    @classmethod
    def validate(cls, v):
        # skip validation if it's already validated
        if isinstance(v, PostCodeField):
            return v
        if not isinstance(v, str):
            raise TypeError('string required')
        m = cls.post_code_regex.fullmatch(v)
        if not m:
            raise ValueError(_('invalid post code format'))

        return cls(m.group(0))


class PhoneNumberField(BaseField):
    @classmethod
    def validate(cls, v):
        if isinstance(v, PhoneNumberField):
            return v
        if not isinstance(v, str):
            raise TypeError('string required')
        if not v.isnumeric() or len(v) != 10:
            raise ValueError(_('invalid phone number'))
        return cls(v)


class VerificationCodeField(BaseField):
    @staticmethod
    def generate_new():
        return VerificationCodeField(randint(10000, 99999))

    @classmethod
    def validate(cls, v):
        if isinstance(v, VerificationCodeField):
            return v
        if not isinstance(v, str):
            raise TypeError('string required')
        if not v.isnumeric() or len(v) != 5:
            raise ValueError(_('invalid verification code format'))
        return cls(v)


class CompanyDomainField(BaseField):

    domain_regex = re.compile(r'^[a-zA-Z0-9-]{3,32}$')

    @classmethod
    def validate(cls, v):
        if isinstance(v, CompanyCodeField):
            return v
        if not isinstance(v, str):
            raise TypeError('string required')
        m = cls.domain_regex.fullmatch(v)
        if not m:
            raise ValueError(_('invalid company domain format'))

        return cls(m.group(0))
