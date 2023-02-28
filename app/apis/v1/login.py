from typing import Union
from fastapi.routing import APIRouter

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.models.auth import LegalUserAuthenticationIn, RealUserAuthenticationIn
from app.models.token import AccessTokenOut
from app.services.token import get_access_token
from app.services import get_srv, AuthService
from app.types.fields import CompanyCodeField, NationalCodeField
from app.models.base import PlatformSpecificationIn


router = APIRouter(tags=['Login'])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token/")


@router.post("/token/")
async def login_for_swagger(
    credentials: OAuth2PasswordRequestForm = Depends(),
    srv: AuthService = Depends(get_srv)
):
    """
    Authentication endpoint for users that want to use swagger documentation.
    This is an internal endpoint and should only be used internally for debugging purpose.
    """

    if len(credentials.username) == 10:
        cred = RealUserAuthenticationIn(
            national_code=NationalCodeField(credentials.username),
            password=credentials.password,
            current_platform=PlatformSpecificationIn(
                platform="*", role='admin')
        )

    else:
        cred = LegalUserAuthenticationIn(
            company_code=CompanyCodeField(credentials.username),
            password=credentials.password,
            current_platform=PlatformSpecificationIn(
                platform="*", role="admin")
        )

    user = srv.authenticate(cred)

    access_token = get_access_token(
        user,
        cred.current_platform.platform,
        cred.current_platform.role
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/", response_model=AccessTokenOut)
async def login_user(
    credentials: Union[RealUserAuthenticationIn, LegalUserAuthenticationIn],
    srv: AuthService = Depends(get_srv)
):
    """
    Authenticate users from different platforms

    **platform_name**: Platform that user came from:
    """
    user = srv.authenticate(credentials)

    access_token = get_access_token(
        user,
        credentials.current_platform.platform,
        credentials.current_platform.role
    )
    return AccessTokenOut(token=access_token)
