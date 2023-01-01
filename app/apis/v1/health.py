from typing import Union
from fastapi.routing import APIRouter
from fastapi import Depends
from redis import Redis
from app.database import storage
from app.core.config import settings
from app.models.response import StandardResponse
from app.apis.response import standard_response
from app.apis.depends import get_current_admin_user
from app.services.rpc import client
from app.services.token import get_access_token
from app.models.user import RealUser, LegalUser


router = APIRouter(prefix="/health", tags=['Health Checks'])


@router.get("/mongodb/", response_model=StandardResponse)
def check_database_connection(
    admin: Union[RealUser, LegalUser] = Depends(get_current_admin_user)):   
    """ Checkes MongoDB connection using ping command. """
    try:
        storage.check_connection()
        return standard_response('ok')
    except Exception as e:
        return standard_response(str(e))


@router.get('/redis/', response_model=StandardResponse)
def check_redis_connection(
    admin: Union[RealUser, LegalUser] = Depends(get_current_admin_user)):
    """ Checks redis connection. """
    try:
        Redis(
            host=settings.redis.address.host, 
            port=settings.redis.address.port, 
            db=0,
            password=settings.redis.password
        )
        return standard_response('ok')
    except Exception as e:
        return standard_response(str(e))


@router.get('/rabbitmq/', response_model=StandardResponse)
async def check_rabitmq_connection(
    admin: Union[RealUser, LegalUser] = Depends(get_current_admin_user)):
    """ 
    Tries to authenticate the first user in the database
    using rcp client 
    """ 

    user = storage.users.get_first()
    try:
        response = await client.authenticate_rpc(
                get_access_token(
                    user,
                    user.roles[0].platform,
                    user.roles[0].names[0]
                )
            )
        return standard_response(response)
    except Exception as e:
        return standard_response(str(e))
