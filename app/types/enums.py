from enum import Enum


class StrEnum(str, Enum):
    pass


class UserType(StrEnum):
    LEGAL = "LEGAL"
    REAL = "REAL"


class Gender(StrEnum):
    male = "MALE"
    female = "FEMALE"
