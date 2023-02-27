from unittest import TestCase, IsolatedAsyncioTestCase
from tests.fake import fake_admin, fake_service

from app.models.auth import RealUserAuthenticationIn, LegalUserAuthenticationIn
from app.models.verification import RealUserCodeVerificationIn, RealUserSendSMSCodeIn
from app.models.base import PlatformSpecificationIn
from app.models.province import Province, City
from app.models.role import Role, UserRole
from app.models.user import RealUser, LegalUser
from app.database import MemoryDatabase, errors
from app.cache import MemoryCache
from app.types.fields import ObjectId, ObjectIdField
from app.services.authentication import UnAuthorizedError
from app.services.verification import SMSVerificationService 
from app.services.notification import FakeSMSNotification, SMSNotification


class TestAuthService(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.service = fake_service()
        self.province = Province(
            _id=ObjectIdField(ObjectId()),
            name='p1', 
            cities=[
                City(_id=ObjectIdField(ObjectId()), name='c11'), 
                City(_id=ObjectIdField(ObjectId()), name='c12')
            ]
        )
        self.service.database.provinces.create(self.province)
    
        role = Role(
            _id=ObjectIdField(ObjectId()),
            platform="*",
            names=['admin', 'staff']
        )
        self.service.database.roles.create(role)

    def tearDown(self) -> None:
        self.service.database.drop()

    def test_authenticate_unknown_user(self):
        try:
            self.service.authenticate(
                RealUserAuthenticationIn(
                    national_code='1111111111',
                    password='test',
                    current_platform=PlatformSpecificationIn(
                        platform='*', 
                        role='admin'
                    )
                ))
            assert False
        except Exception as exc:
            assert isinstance(exc, UnAuthorizedError)
            assert str(exc) == "invalid credentials"

    def test_authenticate_wrong_password(self):
        user = RealUser.new_user(
            national_code='1111111111',
            first_name='first_name',
            last_name='last_name',
            phone_number='1111111111',
            plain_password='plain_password',
            roles=[
                UserRole(platform='*', names=['admin'])
            ],
        )
        self.service.database.users.create(user)

        try:
            self.service.authenticate(
                RealUserAuthenticationIn(
                    national_code=user.national_code,
                    password='test',
                    current_platform=PlatformSpecificationIn(
                        platform='*', 
                        role='admin'
                    )
                )
            )
            assert False
        except Exception as exc:
            assert isinstance(exc, UnAuthorizedError)
            assert str(exc) == "invalid credentials"

    def test_authenticate_none_existent_platform(self):
        user = RealUser.new_user(
            national_code='1111111111',
            first_name='first_name',
            last_name='last_name',
            phone_number='1111111111',
            plain_password='plain_password',
            roles=[
                UserRole(platform='*', names=['admin'])
            ],
        )
        self.service.database.users.create(user)

        try:
            self.service.authenticate(
                RealUserAuthenticationIn(
                    national_code=user.national_code,
                    password='plain_password',
                    current_platform=PlatformSpecificationIn(
                        platform='invalid', 
                        role='admin'
                    )
                )
            )
            assert False
        except Exception as exc:
            assert isinstance(exc, UnAuthorizedError)
            assert str(exc) == "you don't have this role in the given platform"

    def test_authenticate_with_correct_credentials(self):
        user = RealUser.new_user(
            national_code='1111111111',
            first_name='first_name',
            last_name='last_name',
            phone_number='1111111111',
            plain_password='plain_password',
            roles=[
                UserRole(platform='*', names=['admin'])
            ],
        )
        self.service.database.users.create(user)

        db_user = self.service.authenticate(
            RealUserAuthenticationIn(
                national_code=user.national_code,
                password='plain_password',
                current_platform=PlatformSpecificationIn(
                    platform='*', 
                    role='admin'
                )
            )
        )

        assert user == db_user
    
    def test_create_user(self):
        pass


class TestVerification(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.service = SMSVerificationService(
            notification=FakeSMSNotification(),
            cache=MemoryCache(),
            db=MemoryDatabase()
        )
        self.province = Province(
            _id=ObjectIdField(ObjectId()),
            name='p1', 
            cities=[
                City(_id=ObjectIdField(ObjectId()), name='c11'), 
                City(_id=ObjectIdField(ObjectId()), name='c12')
            ]
        )
        self.service.database.provinces.create(self.province)
    
        role = Role(
            _id=ObjectIdField(ObjectId()),
            platform="*",
            names=['admin', 'staff']
        )
        self.service.database.roles.create(role)

    def tearDown(self) -> None:
        self.service.database.drop()

    def test_verify_as_new_user_first_message(self):
        assert self.service.check_already_exist(
            RealUserSendSMSCodeIn(
                national_code='1111111111',
                phone_number='1111111111',
                verify_as='NEW_USER'
            )
        ) == False

    def test_verify_as_new_user_second_message(self):
        v = RealUserSendSMSCodeIn(
            national_code='1111111111',
            phone_number='1111111111',
            verify_as='NEW_USER'
        )
        self.service.send(v)

        assert self.service.check_already_exist(v) == True 

    def test_verify_as_new_with_already_registered_user(self):
        user = RealUser.new_user(
            national_code='1111111111',
            first_name='first_name',
            last_name='last_name',
            phone_number='1111111111',
            plain_password='plain_password',
            roles=[
                UserRole(platform='*', names=['admin'])
            ],
        )
        self.service.database.users.create(user)


        try:
            self.service.check_already_exist(
                RealUserSendSMSCodeIn(
                    national_code='1111111111',
                    phone_number='1111111111',
                    verify_as='NEW_USER'
                )
            ) 
            assert False
        except Exception as exc:
            assert isinstance(exc, errors.UserAlreadyExist)


    def test_verify_none_existent_user(self):
        try:
            self.service.check_already_exist(
                RealUserSendSMSCodeIn(
                    national_code='1111111111',
                    phone_number='1111111111',
                    verify_as='EXISTENT_USER'
                )
            )
            assert False
        except Exception as exc:
            assert isinstance(exc, errors.UserDoesNotExist)
