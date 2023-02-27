from unittest import TestCase
from fastapi.testclient import TestClient
from fastapi import status

from app.cache import MemoryCache, init_cache 
from app.database import MemoryDatabase, init_db
from app.models.role import UserRole 
from app.main import app
from app.apis.depends import get_current_admin_user
from app.models.province import CityIn, City, Province, ProvinceIn
from app.models.user import RealUser, LegalUser, RealUserCreationIn, LegalUserCreationIn, ProfileOut
from app.models.response import StandardResponse


def fake_admin() -> RealUser:
    return RealUser.new_user(
        national_code='1111111111',
        phone_number='1111111111',
        first_name='test',
        last_name='test',
        plain_password='test',
        roles=[UserRole(platform='test.com', names=['admin'])]
    )


class TestHealthAPIs(TestCase):
    def setUp(self) -> None:
        self.db = MemoryDatabase()
        init_db(self.db)

        self.cache = MemoryCache()
        init_cache(self.cache)

        app.dependency_overrides[get_current_admin_user] = lambda: fake_admin() 
        self.client = TestClient(app)

    def test_check_database_connection(self):
        res = self.client.get('api/v1/health/mongodb/')
        assert res.status_code == 200

    def test_check_redis_connection(self):
        res = self.client.get('api/v1/health/redis/')
        assert res.status_code == 200

    # def test_check_rabbitmq_connection(self):
    #     res = self.client.get('api/v1/health/rabbitmq/')
    #     assert res.status_code == 200


class TestInformationAPIs(TestCase):
    def setUp(self) -> None:
        self.db = MemoryDatabase()
        init_db(self.db)

        app.dependency_overrides[get_current_admin_user] = lambda: fake_admin() 
        self.client = TestClient(app)

    def test_get_provinces(self):
        p = Province(
            # type: ignore
            name='test_province',
            cities=[
                City(name='test_city_1'), # type: ignore
                City(name='test_city_2'), # type: ignore
                City(name='test_city_3'), # type: ignore
            ]
        )
        p_db = self.db.provinces.create(p)

        res = self.client.get('api/v1/info/provinces/')

        assert res.status_code == 200
        assert Province(**res.json()[0]) == p_db

    def test_create_province(self):
        p_in = ProvinceIn(
            name='test_province',
            cities=[
                CityIn(name='test_city_1'),
                CityIn(name='test_city_2'),
                CityIn(name='test_city_3'),
            ]
        )

        res = self.client.post('api/v1/info/provinces/', json=p_in.dict())
        assert res.status_code == 200
        assert Province(**res.json()).id != None 
        assert ProvinceIn(**res.json()) == p_in


class TestUserAPIs(TestCase):
    def setUp(self) -> None:
        self.db = MemoryDatabase()
        init_db(self.db)

        app.dependency_overrides[get_current_admin_user] = lambda: fake_admin() 
        self.client = TestClient(app)

    def test_create_user_valid(self):
        user_in = {
           'first_name': 'test',
           'last_name': 'test',
           'national_code': '1111111111',
           'phone_number': '1111111111',
           'roles': [
                {
                    'platform': 'test.com', 
                    'names': ['simple']
                }
            ],
           'password1': '1234',
           'password2': '1234',
        }
        res = self.client.post('api/v1/users/', json=user_in)
        assert res.status_code == 200
        assert StandardResponse(**res.json()).message.en == 'user created'

        assert self.db.users.get_by_national_code('1111111111') != None

    def test_create_user_invalid_national_code(self):
        user_in = {
           'first_name': 'test',
           'last_name': 'test',
           'national_code': '1111',
           'phone_number': '1111111111',
           'roles': [
                {
                    'platform': 'test.com', 
                    'names': ['simple']
                }
            ],
           'password1': '1234',
           'password2': '1234',
        }
        res = self.client.post('api/v1/users/', json=user_in)
        assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert 'national code' in StandardResponse(**res.json()).message.en.lower()

    def test_create_user_invalid_phone_number(self):
        user_in = {
           'first_name': 'test',
           'last_name': 'test',
           'national_code': '1111111111',
           'phone_number': '1111',
           'roles': [
                {
                    'platform': 'test.com', 
                    'names': ['simple']
                }
            ],
           'password1': '1234',
           'password2': '1234',
        }
        res = self.client.post('api/v1/users/', json=user_in)
        assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert 'phone number' in StandardResponse(**res.json()).message.en.lower()

    def test_create_user_different_passwords(self):
        user_in = {
           'first_name': 'test',
           'last_name': 'test',
           'national_code': '1111111111',
           'phone_number': '1111111111',
           'roles': [
                {
                    'platform': 'test.com', 
                    'names': ['simple']
                }
            ],
           'password1': '1234',
           'password2': '12345',
        }
        res = self.client.post('api/v1/users/', json=user_in)
        assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert 'password' in StandardResponse(**res.json()).message.en.lower()

    def test_get_users(self):
        users = [
            RealUser.new_user(
                '11111111111', 
                '11111111111', 
                'first_name', 
                'last_name', 
                'password', 
                [
                    UserRole(
                        platform='platform.com', 
                        names=['role_name']
                    )
                ]
            ),
            LegalUser.new_user(
                '11111111111', 
                '11111111111', 
                'company_name', 
                'domain', 
                'password', 
                [
                    UserRole(
                        platform='platform.com', 
                        names=['role_name']
                    )
                ]
            )
        ]
        for user in users:
            self.db.users.create(user)

        res = self.client.get('api/v1/users/')
        assert res.status_code == status.HTTP_200_OK
        users_db = res.json()
        assert ProfileOut(**users_db[0]).real_user
        assert ProfileOut(**users_db[1]).legal_user


# class TestAPI(TestCase):
#     def setUp(self):
#         self.client = TestClient(app)
#         database.roles.create(Role(platform='*', names=['admin']))
        
#         self.admin = RealUser.new_user(
#             '0000000000', 
#             '0000000000', 
#             'admin', 
#             'admin', 
#             'adminpassword', 
#             roles=[UserRole(platform='*', names=['admin'])]
#         )
#         database.users.create(self.admin)


#     def get_admin_token(self) -> str:
#         return get_access_token(self.admin, '*', 'admin')

#     def get_headers(self) -> str:
#         return {'Authorization': f'bearer {self.get_admin_token()}'}

#     def test_check_mongodb(self):
#         response = self.client.get('/api/v1/health/mongodb/', headers=self.get_headers())
#         self.assertEqual(response.status_code, 200)
        
#     def test_create_user_invalid_platform(self):
#         user = RealUserCreationIn(
#             national_code="1111111111",
#             phone_number="1111111111",
#             roles=[UserRole(platform='test.com', names=['staff'])],
#             first_name="test",
#             last_name="test",
#             password1="password",
#             password2="password"
#         ) 

#         response = self.client.post('/api/v1/users/', json=user.dict(), headers=self.get_headers())

#         self.assertEqual(response.status_code, 400)
    
#     def test_create_user(self):
#         database.roles.create(Role(platform='test.com', names=['staff']))
#         user = RealUserCreationIn(
#             national_code="1111111111",
#             phone_number="1111111111",
#             roles=[UserRole(platform='test.com', names=['staff'])],
#             first_name="test",
#             last_name="test",
#             password1="password",
#             password2="password"
#         ) 

#         response = self.client.post('/api/v1/users/', json=user.dict(), headers=self.get_headers())

#         self.assertEqual(response.status_code, 200)
#         self.assertIsNotNone(database.users.get_by_national_code('1111111111'))

#     def tearDown(self):
#         database.users.collection.delete_many({})
#         database.roles.collection.delete_many({})


# class ProvinceAPIsTest(TestCase):
#     def setUp(self, mock_service) -> None:
#         app.dependency_overrides[get_srv] = fake_get_srv() # type: ignore
#         self.client = TestClient(app)
#         service = fake_get_srv()
#         self.admin = service.create_admin(
#             national_code='0000000000', 
#             phone_number='0000000000', 
#             first_name='admin', 
#             last_name='admin', 
#             password='adminpassword' 
#         )
#         self.headers = {'Authorization': f'bearer {get_admin_token(self.admin)}'}

#     def test_create_province_api(self):
#         p_in = ProvinceIn(
#             name="test", 
#             cities=[
#                 CityIn(name="test1"), 
#                 CityIn(name="test2")
#             ]
#         )

#         res = self.client.post("/api/v1/info/provinces/", json=p_in.dict(), headers=self.headers)
#         self.assertEqual(res.status_code, 200)

