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


router = APIRouter(prefix='/verification', tags=['Verification'])


@router.post('/sms/send/', response_model=StandardResponse, summary="Send SMS Verification")
def send_sms_code(
    v: Union[RealUserSendSMSCodeIn, LegalUserSendSMSCodeIn],
    background_tasks: BackgroundTasks,
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
    if service.verification.check_already_exist(v):
        return standard_response(_('already sent'))

    background_tasks.add_task(service.verification.send, v)
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
    service.verification.verify(v)
    return standard_response(_('verified'))
