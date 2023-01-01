import json

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


def request_handler(request: bytes) -> bytes:
    try:
        json_request: dict = json.loads(request)
    except json.JSONDecodeError as v:
        return json.dumps({'error': 'invalid json format'}).encode('utf-8')

    response = call_service(json_request)
    return json.dumps(response).encode('utf-8')
