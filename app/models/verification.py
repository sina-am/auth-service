from typing import Literal
from app.models.base import BaseModelIn
from app.types.fields import (
    NationalCodeField, PhoneNumberField,
    VerificationCodeField, CompanyCodeField
)


class RealUserSendSMSCodeIn(BaseModelIn):
    national_code: NationalCodeField
    phone_number: PhoneNumberField
    verify_as: Literal["EXISTENT_USER", "NEW_USER"] = "NEW_USER"


class LegalUserSendSMSCodeIn(BaseModelIn):
    company_code: CompanyCodeField
    phone_number: PhoneNumberField
    verify_as: Literal["EXISTENT_USER", "NEW_USER"] = "NEW_USER"


class RealUserCodeVerificationIn(RealUserSendSMSCodeIn):
    code: VerificationCodeField


class LegalUserCodeVerificationIn(LegalUserSendSMSCodeIn):
    code: VerificationCodeField
