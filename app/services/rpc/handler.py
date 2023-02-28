from pydantic import ValidationError
from app.models.token import AccessTokenOut
from app.services.token import verify_access_token


def call_service(request: dict) -> dict:
    if request.get('service_name') == 'jwt_verification':
        try:
            access_token = AccessTokenOut(**request)
        except ValidationError as err:
            return {'message': err.errors()}

        return {'message': verify_access_token(access_token)}
    else:
        return {'error': 'invalid service name'}
