from typing import Union
from fastapi.routing import APIRouter
from fastapi import Depends
from app.models.response import StandardResponse
from app.apis.response import standard_response
from app.apis.depends import get_current_admin_user
from app.services.rpc import client
from app.services.token import get_access_token
from app.cache import get_cache, Cache
from app.database import get_db, Database
from app.models.user import RealUser, LegalUser


router = APIRouter(prefix="/health", tags=['Health Checks'])


@router.get("/mongodb/", response_model=StandardResponse)
def check_mongodb_connection(
    admin: Union[RealUser, LegalUser] = Depends(get_current_admin_user),
    db: Database = Depends(get_db) 
    ):   
    """ Checkes MongoDB connection using ping command. """
    try:
        db.check_connection()
        return standard_response('ok')
    except Exception as e:
        return standard_response(str(e))


@router.get('/redis/', response_model=StandardResponse)
def check_redis_connection(
    admin: Union[RealUser, LegalUser] = Depends(get_current_admin_user),
    cache: Cache = Depends(get_cache) 
    ):
    """ Checks redis connection. """
    if cache.ping():
        return standard_response('ok')
    return standard_response("connection error")


# @router.get('/rabbitmq/', response_model=StandardResponse)
# async def check_rabitmq_connection(
#     # admin: Union[RealUser, LegalUser] = Depends(get_current_admin_user),
#     db: Database = Depends(get_db)
#     ):
#     """ 
#     Check rabbitMQ connection
#     """ 

#     try:
#         return standard_response(response)
#     except Exception as e:
#         return standard_response(str(e))
