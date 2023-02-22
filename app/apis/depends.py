from fastapi import Depends
from app.apis.errors import HTTPCredentialError, HTTPPermissionError
from app.apis.v1.login import oauth2_scheme
from app.services.token import decode_access_token
from app.services import AuthenticationService, get_srv
from app.database import errors



async def get_current_token(
    token: str = Depends(oauth2_scheme),
    service: AuthenticationService = Depends(get_srv) 
    ):
    try:
        token_data = decode_access_token(token)
    except Exception:
        raise HTTPCredentialError()
    try:
        service.database.users.get_by_id(token_data.user.id)
    except errors.UserDoesNotExist:
        raise HTTPCredentialError()
    return token_data

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    service: AuthenticationService = Depends(get_srv) 
    ):
    try:
        token_data = decode_access_token(token)
    except Exception:
        raise HTTPCredentialError()

    try:
        return service.database.users.get_by_id(token_data.user.id)
    except errors.UserDoesNotExist:
        raise HTTPCredentialError()

async def get_current_admin_user(
    token: str = Depends(oauth2_scheme),
    service: AuthenticationService = Depends(get_srv) 
    ):
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPCredentialError()

    try:
        user = service.database.users.get_by_id(payload.user.id)
    except errors.UserDoesNotExist:
        raise HTTPCredentialError()
    
    if payload.current_platform.platform == "*":
        if payload.current_platform.role == "admin":
            if user.has_role(platform="*", role_name="admin"):
                return user
    raise HTTPPermissionError()