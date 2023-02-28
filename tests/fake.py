from app.models.user import RealUser, UserRole
from app.services.token import get_access_token
from app.cache import MemoryCache
from app.database import MemoryDatabase
from app.services import AuthService, FakeSMSNotification, MemoryBroker
from app.services import authentication_factory
from app.types.fields import NationalCodeField, PhoneNumberField


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
        national_code=NationalCodeField('1111111111'),
        phone_number=PhoneNumberField('1111111111'),
        first_name='test',
        last_name='test',
        plain_password='test',
        roles=[UserRole(platform='test.com', names=['admin'])]
    )
