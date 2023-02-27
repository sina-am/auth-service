from typing import Union
from fastapi.routing import APIRouter
from fastapi import Depends
from app.models.response import StandardResponse
from app.apis.response import standard_response
from app.apis.depends import get_current_admin_user
from app.models.user import RealUser, LegalUser
from app.services import AuthService, get_srv


router = APIRouter(prefix="/health", tags=['Health Checks'])


@router.get("/mongodb/", response_model=StandardResponse)
def check_mongodb_connection(
    admin: Union[RealUser, LegalUser] = Depends(get_current_admin_user),
    srv: AuthService = Depends(get_srv) 
    ):   
    """ Checkes MongoDB connection using ping command. """
    try:
        srv.database.check_connection()
        return standard_response('ok')
    except Exception as e:
        return standard_response(str(e))


@router.get('/redis/', response_model=StandardResponse)
def check_redis_connection(
    admin: Union[RealUser, LegalUser] = Depends(get_current_admin_user),
    srv: AuthService = Depends(get_srv) 
    ):
    """ Checks redis connection. """
    if srv.cache.ping():
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
