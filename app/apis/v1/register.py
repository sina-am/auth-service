from typing import Union
from fastapi import Depends
from fastapi.routing import APIRouter
from app.models.user import LegalUserRegistrationIn, RealUserRegistrationIn
from app.models.response import StandardResponse
from app.apis.response import standard_response
from app.services import AuthService, get_srv 
from app.utils.translation import _


router = APIRouter(prefix='/registration', tags=['Registration'])

   
@router.post(
    '/', 
    response_model=StandardResponse, 
    responses={400: {'model': StandardResponse}}
)
async def register_legal_user(
    user_in: Union[RealUserRegistrationIn, LegalUserRegistrationIn],
    srv: AuthService = Depends(get_srv) 
    ):
    await srv.register(user_in)
    return standard_response(_('user created'))
