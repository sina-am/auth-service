from typing import List, Union
from fastapi.routing import APIRouter
from fastapi import Depends
from app.utils.translation import _
from app.models.province import ProvinceOut, ProvinceIn
from app.models.user import RealUser, LegalUser
from app.database import storage
from app.apis.depends import get_current_admin_user


router = APIRouter(prefix="/info", tags=['Provinces'])

@router.get("/provinces/", response_model=List[ProvinceOut])
async def get_provinces():
    """ Get provinces list """

    return list(map(lambda p: ProvinceOut.from_db(p), storage.provinces.get_all()))


@router.post("/provinces/", response_model=ProvinceOut)
async def create_province(
    province_in: ProvinceIn,
    admin: Union[RealUser, LegalUser] = Depends(get_current_admin_user)
    ):

    """ Create a new province with cities """
    
    return storage.provinces.create(province_in.to_model())