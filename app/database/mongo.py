from app.models.role import Role
from app.models.user import RealUser, LegalUser
from app.models.province import Province, City
from typing import Any, List, Union
from gridfs import Collection, Database
from app.database import errors
from bson import ObjectId
from app.types.fields import CompanyCodeField, NationalCodeField, UserType
from datetime import datetime
from app.core.config import settings
from pymongo import MongoClient
from app.database.base import (
    BaseDatabase, BaseUserStorage, BaseProvinceStorage, BaseRoleStorage
)


class MongoRoleStorage(BaseRoleStorage):
    def __init__(self, db: Database):
        self.db = db
        self.collection = self.db.roles
    
    def create(self, role: Role) -> Role:
        if self.get_by_platform(role.platform):
            raise errors.RoleAlreadyExist("role already exist.")

        result = self.collection.insert_one(role.dict())
        role.id = result.inserted_id
        return role
        
    def get_all(self) -> List[Role]:
        return list(map(lambda d: Role(**d), self.collection.find())) 

    def get_by_platform(self, platform: str) -> Role:
        result = self.collection.find_one({"platform": platform})
        if result:
            return Role(**result)
        return None

    def __check_if_exists(self, role: Role) -> bool:
        result = self.collection.find_one({"$exists": {"platform": role.platform}})
        print("from __check_if_exists", result)
        if result:
            return True
        return False

    def delete_by_id(self, role_id: str):
        result = self.collection.delete_one({"_id": ObjectId(role_id)})
        if result.deleted_count == 1:
            return
        raise errors.RoleDoesNotExist(f"role id {role_id} not found")


class MongoUserStorage(BaseUserStorage):
    def __init__(self, db: Database):
        self.db = db
        self.collection = self.db.users
        self.required_fields = {
            '_id': 1, 
            'password': 1, 
            'roles': 1, 
            'type': 1, 
            'national_code': 1, 
            'company_code': 1,
            'phone_number': 1,
            'last_login': 1,
            'created_at': 1,
            'picture_url': 1,
            'contact_information': 1,
            # For real user
            'first_name': 1,
            'last_name': 1,
            'father_name': 1,
            'gender': 1,
            'birth_day': 1,
            # For legal user
            'company_name': 1,
            'domain': 1,
            'title': 1
        } 
    
    def __find_one(self, filters):
        """ Only fetchs required fields. """
        return self.collection.find_one(filters, self.required_fields)

    def __error_on_duplicate_key(self, user: Union[RealUser, LegalUser]):
        if isinstance(user, RealUser):
            document = self.__find_one({'national_code': user.national_code})
        elif isinstance(user, LegalUser):
            document = self.__find_one({'company_code': user.company_code})
        if document:
            raise errors.UserAlreadyExist("user already exists")

    def __error_on_invalid_roles(self, roles):
        # TODO: Use efficent query
        for user_role in roles:
            role = self.db.roles.find_one({"platform": user_role.platform})
            if not role:
                raise errors.RoleDoesNotExist(f"platform {user_role.platform} does not exists")

            for name in user_role.names:
                if name not in role["names"]:
                    raise errors.RoleDoesNotExist(
                        f"role {name} in platform {user_role.platform} does not exist")

    def __error_on_invalid_city(self, city_id):
        query = self.db.roles.find_one(
            {'cities._id': ObjectId(city_id)},
            {'name': 1, 'cities.$': 1}
        )
        if not query:
            raise errors.CityDoesNotExist(f"city with id {city_id} don't exist")

    def create(self, user: Union[RealUser, LegalUser]) -> Union[RealUser, LegalUser]:
        self.__error_on_invalid_roles(user.roles)
        self.__error_on_duplicate_key(user)

        document = user.dict(exclude_none=True)
        result = self.collection.insert_one(document) 
        user.id = result.inserted_id
        return user

    def update_last_login(self, user: Union[RealUser, LegalUser]):
        self.collection.update_one(
            {'_id': ObjectId(user.id)},
            {'$set': {'last_login': datetime.utcnow()}}
        )

    def map_to_model(self, document) -> Union[RealUser, LegalUser]:
        if document.get("type") == UserType.REAL:
            return RealUser(**document)
        elif document.get("type") == UserType.LEGAL:
            return LegalUser(**document)
        raise errors.InvalidDatabaseSchema(f"user {user_id} doesn't have a type field")

    def get_all(self) -> Union[RealUser, LegalUser]:
        return list(map(lambda d: self.map_to_model(d), self.collection.find())) 

    def get_by_national_code(self, national_code: NationalCodeField) -> RealUser:
        document = self.__find_one({"national_code": national_code})
        if not document:
            raise errors.UserDoesNotExist("user does not exist")
        return RealUser(**document)

    def get_by_company_code(self, company_code: CompanyCodeField) -> LegalUser:
        document = self.__find_one({"company_code": company_code})
        if not document:
            raise errors.UserDoesNotExist("user does not exist")
        return LegalUser(**document)

    def get_first(self) -> Union[RealUser, LegalUser]:
        document = self.__find_one({})
        if not document:
            raise errors.UserDoesNotExist("user does not exist")
        return self.map_to_model(document)

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

    def get_by_id(self, user_id: str) -> Union[RealUser, LegalUser, None]:
        document = self.__find_one({"_id": ObjectId(user_id)})
        if not document:
            raise errors.UserAlreadyExist("user does not exist")
        return self.map_to_model(document) 

    def update(self, user: Union[RealUser, LegalUser]):
        # TODO: Only update fields that are changed
        if user.contact_information:
            self.__error_on_invalid_city(
                user.contact_information.city_id) 

        query = user.dict(exclude_none=True)
        query.pop('id')

        if query.get("contact_information"):
            for field, value in query["contact_information"].items():
                query[f"contact_information.{field}"] = value
            query.pop("contact_information")

        self.collection.update_one(
            {'_id': ObjectId(user.id)},
            {"$set": query}
        )


class MongoProvinceStorage(BaseProvinceStorage):
    def __init__(self, db: Database):
        self.db = db
        self.collection = self.db.provinces

    def create(self, province: Province) -> Province:
        document = province.dict(exclude_none=True)
        # TODO: remove this
        for i in range(len(document['cities'])):
            document['cities'][i] = {
                "_id": document['cities'][i]["id"],
                "name": document['cities'][i]["name"] 
            }

        result = self.collection.insert_one(document)
        province.id = result.inserted_id
        return province 

    def get_all(self) -> List[Province]: 
        return list(map(lambda d: Province(**d), self.collection.find())) 

    def get_by_city_id(self, city_id: str) -> Province:
        """ only return one city with it's province """
        
        query = self.collection.find_one(
            {'cities._id': ObjectId(city_id)},
            {'name': 1, 'cities.$': 1}
        )
        if not query:
            raise errors.CityDoesNotExist(f"city with id {city_id} don't exist")
        return Province(**query) 

    def get_city_id_by_name(self, name: str):
        result = self.collection.find_one(
            {'cities.name': name},
            {'cities.$': 1}
        )
        if result:
            return result['cities'][0]['_id']
        return None


class MongoDatabase(BaseDatabase):
    def __init__(self):
        self.client = MongoClient(settings.mongodb.uri)
        self.db = self.client.get_database(settings.mongodb.database)
        self.roles = MongoRoleStorage(self.db)
        self.users = MongoUserStorage(self.db)
        self.provinces = MongoProvinceStorage(self.db)

    def check_connection(self):
        return self.db.command('ping')
    