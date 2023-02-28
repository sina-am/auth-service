from bson import ObjectId
from app.database.base import Database, ProvinceDatabase, RoleCollection, UserCollection
from app.models.role import Role
from app.models.user import RealUser, LegalUser
from app.models.province import Province
from typing import Any, Dict, List, Union
from app.database import errors
from app.types.fields import CompanyCodeField, NationalCodeField, ObjectIdField


class MemoryRoleDatabase(RoleCollection):
    def __init__(self, db):
        self.db = db

    def create(self, role: Role) -> Role:
        role.id = ObjectId()  # type: ignore
        self.db["roles"].append(role)
        return role

    def get_all(self) -> List[Role]:
        return self.db["roles"]

    def get_by_platform(self, platform: str) -> Role:
        for role in self.db["roles"]:
            if role.platform == platform:
                return role
        raise errors.RoleDoesNotExist(
            f"role with platform {platform} doesn't exist")

    def delete_by_id(self, role_id: str):
        for i in range(len(self.db["roles"])):
            if self.db["roles"][i].id == role_id:
                del self.db["roles"][i]


class MemoryUserDatabase(UserCollection):
    def __init__(self, db):
        self.db = db

    def create(self, user: Union[RealUser, LegalUser]) -> Union[RealUser, LegalUser]:
        user.id = ObjectId()  # type: ignore
        self.db["users"].append(user)
        return user

    def update_last_login(self, user: Union[RealUser, LegalUser]):
        return

    def get_all(self) -> Union[RealUser, LegalUser]:
        return self.db["users"]

    def get_by_national_code(self, national_code: NationalCodeField) -> RealUser:
        for user in self.db["users"]:
            if isinstance(user, RealUser) and user.national_code == national_code:
                return user
        raise errors.UserDoesNotExist()

    def get_by_company_code(self, company_code: CompanyCodeField) -> LegalUser:
        for user in self.db["users"]:
            if isinstance(user, LegalUser) and user.company_code == company_code:
                return user
        raise errors.UserDoesNotExist()

    def get_first(self) -> Union[RealUser, LegalUser]:
        if len(self.db["users"]) == 0:
            raise errors.UserDoesNotExist()
        return self.db["users"][0]

    def check_by_national_code(self, national_code: NationalCodeField) -> bool:
        try:
            self.get_by_national_code(national_code)
            return True
        except errors.UserDoesNotExist:
            return False

    def check_by_company_code(self, company_code: CompanyCodeField) -> bool:
        try:
            self.get_by_company_code(company_code)
            return True
        except errors.UserDoesNotExist:
            return False

    def get_by_id(self, user_id: str) -> Union[RealUser, LegalUser]:
        for user in self.db["users"]:
            if user.id == user_id:
                return user
        raise errors.UserDoesNotExist()

    def update(self, user: Union[RealUser, LegalUser]):
        ...


class MemoryProvinceDatabase(ProvinceDatabase):
    def __init__(self, db: Dict[str, List[Any]]):
        self.db = db
        self.provinces: List[Province] = db["provinces"]

    def create(self, province: Province) -> Province:
        province.id = ObjectId()  # type: ignore
        self.provinces.append(province)
        return province

    def get_all(self) -> List[Province]:
        return self.provinces

    def get_by_city_id(self, city_id: str) -> Province:
        for province in self.provinces:
            for city in province.cities:
                if city.id == city_id:
                    return province
        raise errors.CityDoesNotExist(f"city {city_id} doesn't exist")


class MemoryDatabase(Database):
    """ Base Database Interface. """

    def __init__(self) -> None:
        db: Dict[str, List[Any]] = {
            "provinces": [],
            "users": [],
            "roles": []
        }
        self.roles = MemoryRoleDatabase(db)
        self.users = MemoryUserDatabase(db)
        self.provinces = MemoryProvinceDatabase(db)

    def check_connection(self):
        raise errors.DatabaseConnectionError("database is not initiated.")

    def drop(self):
        self.db = {}
