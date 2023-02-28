from typing import List, Union
from fastapi.routing import APIRouter
from fastapi import Depends

from app.models.role import RoleCreationIn, Role
from app.database.errors import RoleDoesNotExist
from app.apis.errors import HTTPNotFoundError
from app.apis.response import standard_response
from app.models.response import StandardResponse
from app.types.fields import ObjectIdField
from app.apis.depends import get_current_admin_user
from app.models.user import RealUser, LegalUser
from app.utils.translation import _
from app.services import AuthService, get_srv


router = APIRouter(prefix="/roles", tags=['Roles'])


@router.post("/", response_model=Role)
async def create_role(
    role: RoleCreationIn,
    admin: Union[RealUser, LegalUser] = Depends(get_current_admin_user),
    srv: AuthService = Depends(get_srv)
):
    """ Create a new role or update one """

    return srv.database.roles.create(role.to_model())


@router.get("/", response_model=List[Role])
async def get_roles(
    admin: Union[RealUser, LegalUser] = Depends(get_current_admin_user),
    srv: AuthService = Depends(get_srv)
):
    """ Get all roles """

    return srv.database.roles.get_all()


@router.delete("/{role_id}/", response_model=StandardResponse)
async def delete_role(
    role_id: ObjectIdField,
    admin: Union[RealUser, LegalUser] = Depends(get_current_admin_user),
    srv: AuthService = Depends(get_srv)
):
    """ Delete role. """

    try:
        srv.database.roles.delete_by_id(role_id)
    except RoleDoesNotExist as e:
        raise HTTPNotFoundError(e)
    return standard_response(_("role deleted"))
