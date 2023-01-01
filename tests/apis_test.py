from unittest import TestCase
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import RealUser, RealUserCreationIn
from app.models.role import UserRole, Role
from app.database import storage
from app.services.token import get_access_token


class TestAPI(TestCase):
    def setUp(self):
        self.client = TestClient(app)
        storage.roles.create(Role(platform='*', names=['admin']))
        
        self.admin = RealUser.new_user(
            '0000000000', 
            '0000000000', 
            'admin', 
            'admin', 
            'adminpassword', 
            roles=[UserRole(platform='*', names=['admin'])]
        )
        storage.users.create(self.admin)


    def get_admin_token(self) -> str:
        return get_access_token(self.admin, '*', 'admin')

    def get_headers(self) -> str:
        return {'Authorization': f'bearer {self.get_admin_token()}'}

    def test_check_mongodb(self):
        response = self.client.get('/api/v1/health/mongodb/', headers=self.get_headers())
        self.assertEqual(response.status_code, 200)
        
    def test_create_user_invalid_platform(self):
        user = RealUserCreationIn(
            national_code="1111111111",
            phone_number="1111111111",
            roles=[UserRole(platform='test.com', names=['staff'])],
            first_name="test",
            last_name="test",
            password1="password",
            password2="password"
        ) 

        response = self.client.post('/api/v1/users/', json=user.dict(), headers=self.get_headers())

        self.assertEqual(response.status_code, 400)
    
    def test_create_user(self):
        storage.roles.create(Role(platform='test.com', names=['staff']))
        user = RealUserCreationIn(
            national_code="1111111111",
            phone_number="1111111111",
            roles=[UserRole(platform='test.com', names=['staff'])],
            first_name="test",
            last_name="test",
            password1="password",
            password2="password"
        ) 

        response = self.client.post('/api/v1/users/', json=user.dict(), headers=self.get_headers())

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(storage.users.get_by_national_code('1111111111'))

    def tearDown(self):
        storage.users.collection.delete_many({})
        storage.roles.collection.delete_many({})