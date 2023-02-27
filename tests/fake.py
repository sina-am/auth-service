from app.models.user import RealUser, UserRole
from app.services.token import get_access_token
from app.cache import MemoryCache 
from app.database import MemoryDatabase
from app.services import AuthService, FakeSMSNotification, MemoryBroker, init_srv
from app.services.authentication import authentication_factory


def get_admin_token(admin: RealUser) -> str:
    return get_access_token(admin, '*', 'admin')

def fake_service() -> AuthService:
    return authentication_factory(
        db=MemoryDatabase(),
        cache=MemoryCache(),
        broker=MemoryBroker(delay=3),
        notification=FakeSMSNotification(),
    )

def fake_admin() -> RealUser:
    return RealUser.new_user(
        national_code='1111111111',
        phone_number='1111111111',
        first_name='test',
        last_name='test',
        plain_password='test',
        roles=[UserRole(platform='test.com', names=['admin'])]
    )

