from typing import List, Union
from fastapi.routing import APIRouter
from fastapi import Depends
from app.utils.translation import _
from app.models.province import Province, ProvinceIn
from app.models.user import RealUser, LegalUser
from app.database import Database, get_db
from app.apis.depends import get_current_admin_user


router = APIRouter(prefix="/info", tags=['Provinces'])

@router.get("/provinces/", response_model=List[Province])
async def get_provinces(
    db: Database = Depends(get_db)
    ):
    """ Get provinces list """

    return db.provinces.get_all()


@router.post("/provinces/", response_model=Province)
async def create_province(
    province_in: ProvinceIn,
    admin: Union[RealUser, LegalUser] = Depends(get_current_admin_user),
    db: Database = Depends(get_db)
    ):

    """ Create a new province with cities """
    
    return db.provinces.create(province_in.to_model())