from fastapi import HTTPException, status
from app.utils.translation import _


class HTTPNotFoundError(HTTPException):
    def __init__(self, error) -> None:
        status_code=status.HTTP_404_NOT_FOUND
        detail=str(error) or _("Item not found")
        super().__init__(status_code, detail)


class HTTPPermissionError(HTTPException):
    def __init__(self) -> None:
        status_code=status.HTTP_403_FORBIDDEN
        detail=_("User does not have permission to perform this action")
        super().__init__(status_code, detail)


class HTTPCredentialError(HTTPException):
    def __init__(self) -> None:
        status_code=status.HTTP_401_UNAUTHORIZED
        detail=_("Could not validate credentials")
        headers={"Authenticate": "Bearer"}
        super().__init__(status_code, detail, headers)


class HTTPInvalidVerificationCodeError(HTTPException):
    def __init__(self) -> None:
        status_code=status.HTTP_400_BAD_REQUEST
        detail=_("Verification code is invalid or expired")
        super().__init__(status_code, detail)


class HTTPUserAlreadyExistError(HTTPException):
    def __init__(self, error = None) -> None:
        status_code=status.HTTP_400_BAD_REQUEST
        detail= str(error) or _("User already exists")
        super().__init__(status_code, detail)
