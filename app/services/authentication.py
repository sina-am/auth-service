from typing import Union 

from app.core.security import verify_password
from app.models.user import LegalUser, RealUser 
from app.models.auth import RealUserAuthenticationIn, LegalUserAuthenticationIn
from app.database import storage, errors
from app.core.errors import MyException


class UnAuthorizedError(MyException):
    pass


def authenticate(credentials: Union[RealUserAuthenticationIn, LegalUserAuthenticationIn]):
    if hasattr(credentials, 'national_code'):
        try:
            user = storage.users.get_by_national_code(credentials.national_code)
        except errors.UserDoesNotExist:
            raise UnAuthorizedError("invalid credentials")

    elif hasattr(credentials, 'company_code'):
        try:
            user = storage.users.get_by_company_code(credentials.company_code)
        except errors.UserDoesNotExist:
            raise UnAuthorizedError("invalid credentials")

    if not verify_password(credentials.password, user.password):
        raise UnAuthorizedError("invalid credentials")

    if not user.has_role(credentials.current_platform.platform, credentials.current_platform.role):
        raise UnAuthorizedError("you don't have this role in the given platform")

    storage.users.update_last_login(user)
    return user