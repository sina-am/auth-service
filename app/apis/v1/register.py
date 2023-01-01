from fastapi.routing import APIRouter
from app.models.user import LegalUserRegistrationIn, RealUserRegistrationIn
from app.models.response import StandardResponse
from app.apis.errors import HTTPInvalidVerificationCodeError 
from app.apis.response import standard_response
from app.services import verification  
from app.utils.translation import _
from app.database import storage


router = APIRouter(prefix='/registration', tags=['Registration'])


@router.post(
    '/real/',
    response_model=StandardResponse, 
    responses={400: {'model': StandardResponse}}
)
def register_real_user(user_in: RealUserRegistrationIn):
    if not verification.verify_code(user_in.verification, delete_code=True):
        raise HTTPInvalidVerificationCodeError()  

    user = user_in.to_model()
    storage.users.create(user)
    return standard_response(_('user created'))


@router.post(
    '/legal/', 
    response_model=StandardResponse, 
    responses={400: {'model': StandardResponse}}
)
def register_legal_user(user_in: LegalUserRegistrationIn):
    if not verification.verify_code(user_in.verification, delete_code=True):
        raise HTTPInvalidVerificationCodeError()  

    user = user_in.to_model()
    storage.users.create(user)
    return standard_response(_('user created'))
