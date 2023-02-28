from typing import Union, List
from fastapi import Depends
from fastapi.routing import APIRouter
from fastapi.exceptions import HTTPException
from app.models.user import LegalUser, LegalUserCreationIn, RealUser, PasswordUpdateIn, PhoneNumberUpdateIn, UserUpdateIn, ProfileOut
from app.models.token import JwtPayload
from app.models.profile import (
    PictureIn, PictureOut)

from app.apis.depends import get_current_token, get_current_user, get_current_admin_user
from app.models.response import StandardResponse
from app.models.user import RealUser, LegalUser, RealUserCreationIn
from app.apis.response import standard_response
from app.models.verification import RealUserCodeVerificationIn
from app.utils.translation import _
from app.services import AuthService, get_srv


router = APIRouter(prefix="/users", tags=['Users'])


@router.post('/')
async def create_user(
    user_in: Union[RealUserCreationIn, LegalUserCreationIn],
    admin: Union[RealUser, LegalUser] = Depends(get_current_admin_user),
    srv: AuthService = Depends(get_srv)
):
    srv.database.users.create(user_in.to_model())
    return standard_response(_("user created"))


@router.get('/', response_model=List[ProfileOut])
async def get_users(
    admin: Union[RealUser, LegalUser] = Depends(get_current_admin_user),
    srv: AuthService = Depends(get_srv)
):
    return list(map(
        lambda user: ProfileOut.from_db(user),  # type: ignore
        srv.database.users.get_all()
    ))


@router.get("/me/", response_model=ProfileOut)
async def get_my_user(
    payload: JwtPayload = Depends(get_current_token),
    service: AuthService = Depends(get_srv)
):
    """
    Get login user's profile.

    - **legal_user**: If current user is a legal user this object will be populated.
    otherwise it's null.

    - **real_user**: same is legal_user

    - **current_platform**: are information about the platform
    that the user originally logged-in from.
    """
    user = service.database.users.get_by_id(payload.user.id)
    return ProfileOut.from_db(
        user=user, current_platform=payload.current_platform)


@router.put("/me/", response_model=StandardResponse)
async def update_my_user(
    user_in: UserUpdateIn,
    user: Union[RealUser, LegalUser] = Depends(get_current_user),
    service: AuthService = Depends(get_srv)
):
    """
    Update user's profile.
    This API accepts partial input.

    - **legal_user**: legal user specific info.
    If you're not updating a legal user profile,
    it's better to not send this field. But if you do, it'll be ignored.

    - **real_user**: same behaviour as legal_user

    - **contact_information**: This object is also optional.
    If you don't want to update it, don't send it.

    - - **address_information**: All field in this object are required.
    It means, you either have to send it completely, or not send it at all.
    """
    service.database.users.update(user_in.to_model(user))
    return standard_response(_('profile updated successfully'))


@router.post(
    '/me/change-password/',
    response_model=StandardResponse,
    responses={400: {'model': StandardResponse,
                     'description': 'Invalid or Expired Verification Code'}}
)
def change_password(
    password_in: PasswordUpdateIn,
    service: AuthService = Depends(get_srv)
):
    """ Change user password. """
    service.verification.verify(
        password_in.verification, delete_on_success=True)
    if isinstance(password_in.verification, RealUserCodeVerificationIn):
        user = service.database.users.get_by_national_code(
            password_in.verification.national_code)
    else:
        user = service.database.users.get_by_company_code(
            password_in.verification.company_code)

    user.set_password(password_in.password1)
    service.database.users.update(user)

    return standard_response(_("password successfully reset."))


@router.post(
    '/me/change-phone-number/',
    response_model=StandardResponse,
    responses={400: {'model': StandardResponse,
                     'description': 'Invalid or Expired Verification Code'}}
)
def change_phone_number(
    phone_number_in: PhoneNumberUpdateIn,
    user: Union[RealUser, LegalUser] = Depends(get_current_user),
    service: AuthService = Depends(get_srv)
):
    """
    Change phone number.

    When using send-sms API make sure user don't use the old phone number.
    Set the verify_as field to ***EXISTENT_USER***.
    """

    if phone_number_in.phone_number == user.phone_number:
        raise HTTPException(
            status_code=400, detail="can't use the same phone number")
    service.verification.verify(
        phone_number_in.verification, delete_on_success=True)

    user.phone_number = phone_number_in.phone_number
    service.database.users.update(user)
    return standard_response(_("phone number updated successfully."))


@router.post('/me/picture/', response_model=PictureOut)
def create_picture_url(
    picture_in: PictureIn,
    user: Union[RealUser, LegalUser] = Depends(get_current_user),
    service: AuthService = Depends(get_srv)
):
    """ Reserves an object in S3 and returns the presigend url. """

    signed_url = service.create_profile_picture_url(picture_in, str(user.id))
    return PictureOut(url=signed_url)
