from app.models.role import Role
from app.models.user import RealUser, LegalUser
from app.models.province import Province
from typing import List, Union
from app.database import errors
from app.types.fields import CompanyCodeField, NationalCodeField


class RoleCollection:
    def __init__(self, db): ...

    def create(self, role: Role) -> Role: ...

    def get_all(self) -> List[Role]: ...

    def get_by_platform(self, platform: str) -> Role: ...

    def delete_by_id(self, role_id: str): ...


class UserCollection:
    def __init__(self, db): ...

    def create(self,
               user: Union[RealUser, LegalUser]) -> Union[RealUser, LegalUser]: ...

    def update_last_login(self, user: Union[RealUser, LegalUser]): ...

    def get_all(self) -> List[Union[RealUser, LegalUser]]: ...

    def get_by_national_code(
        self, national_code: NationalCodeField) -> RealUser: ...

    def get_by_company_code(
        self, company_code: CompanyCodeField) -> LegalUser: ...

    def get_first(self) -> Union[RealUser, LegalUser]: ...

    def check_by_national_code(
        self, national_code: NationalCodeField) -> bool: ...

    def check_by_company_code(
        self, company_code: CompanyCodeField) -> bool: ...

    def get_by_id(self, user_id: str) -> Union[RealUser, LegalUser]: ...

    def update(self, user: Union[RealUser, LegalUser]): ...


class ProvinceDatabase:
    def __init__(self, db): ...

    def create(self, province: Province) -> Province: ...

    def get_all(self) -> List[Province]: ...

    def get_by_city_id(self, city_id: str) -> Province: ...


class Database:
    """ Base Database Interface. """
    roles: RoleCollection
    users: UserCollection
    provinces: ProvinceDatabase

    def check_connection(self) -> bool: ...
    def drop(self) -> None: ...
