from typing import Union
from fastapi import BackgroundTasks, Depends
from fastapi.routing import APIRouter
from app.models.response import StandardResponse
from app.apis.response import standard_response
from app.utils.translation import _
from app.models.verification import (
    LegalUserCodeVerificationIn, RealUserCodeVerificationIn,
    LegalUserSendSMSCodeIn, RealUserSendSMSCodeIn,
)
from app.services import AuthService, get_srv
from app.services.verification import VerificationCodeAlreadySendError


router = APIRouter(prefix='/verification', tags=['Verification'])


@router.post('/sms/send/', response_model=StandardResponse, summary="Send SMS Verification")
async def send_sms_code(
    v: Union[RealUserSendSMSCodeIn, LegalUserSendSMSCodeIn],
    service: AuthService = Depends(get_srv)
):
    """
    Verificates a user's phone number by sending a verification code to the given phone_number.

    This API validates the input in two different ways.
    If this is a new user that wants to register to the site,
    you must set the **verify_as** to **NEW_USER**.
    If this is a registered user that somehow wants to verify
    it's phone number again (for changing phone number or password for example),
    you must set the **verify_as** to **EXISTENT_USER**.

    NOTE: Default value for **verify_as** is **NEW_USER**.
    """
    try:
        await service.verification.send(v)
    except VerificationCodeAlreadySendError:
        return standard_response(_('already send'))

    return standard_response(_('sent'))


@router.post(
    '/sms/verify/',
    response_model=StandardResponse,
    responses={400: {'model': StandardResponse}}
)
async def verify_sms_code(
    v: Union[LegalUserCodeVerificationIn, RealUserCodeVerificationIn],
    service: AuthService = Depends(get_srv)
):
    await service.verification.verify(v)
    return standard_response(_('verified'))
