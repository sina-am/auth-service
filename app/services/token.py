from datetime import timedelta, datetime

from pydantic import ValidationError
from app.core.config import settings
from app.core.serializer import JsonSerializer
from app.models.user import User
from app.models.token import AccessTokenOut, JwtPayload, JwtUser
import jwt

from app.models.base import PlatformSpecificationOut


class InvalidJwtTokenError(Exception):
    pass


class ExpiredJwtTokenError(Exception):
    pass


class InvalidSignatureError(Exception):
    pass


def check_token_expiration(expiration: datetime) -> bool:
    return datetime.utcnow() > expiration


def calculate_expiration_time() -> datetime:
    return datetime.utcnow() + timedelta(minutes=settings.access_token_expire_time)


def encode_access_token(data: JwtPayload) -> str:
    encoded_jwt = jwt.encode(
        data.dict(),
        settings.secret_key,
        algorithm=settings.algorithm,
        json_encoder=JsonSerializer)
    return encoded_jwt


def decode_access_token(token: str) -> JwtPayload:
    try:
        payload = jwt.decode(token, settings.secret_key, [settings.algorithm])
        jwt_payload = JwtPayload(**payload)

    except jwt.InvalidSignatureError as v:
        raise InvalidSignatureError(v)
    except ValidationError as v:
        raise InvalidJwtTokenError(v)

    if check_token_expiration(jwt_payload.expiration):
        raise ExpiredJwtTokenError()
    return jwt_payload


def get_access_token(user: User, platform: str, role: str) -> str:
    if not user.id:
        raise ValueError("user id is None")
    jwt_payload = JwtPayload(
        user=JwtUser(
            _id=user.id,
            roles=user.roles,
            type=user.type
        ),
        current_platform=PlatformSpecificationOut(
            platform=platform,
            role=role
        ),
        expiration=calculate_expiration_time()
    )
    return encode_access_token(jwt_payload)


def verify_access_token(access_token: AccessTokenOut) -> bool:
    try:
        decode_access_token(access_token.token)
    except Exception:
        return False
    return True
