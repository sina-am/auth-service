from unittest import IsolatedAsyncioTestCase

from app.models.auth import RealUserAuthenticationIn
from app.models.verification import RealUserCodeVerificationIn, RealUserSendSMSCodeIn
from app.models.base import PlatformSpecificationIn
from app.models.province import Province, City
from app.models.role import Role, UserRole
from app.models.user import RealUser, RealUserRegistrationIn
from app.database import MemoryDatabase, errors
from app.cache import MemoryCache
from app.types.fields import NationalCodeField, ObjectId, ObjectIdField, PhoneNumberField, VerificationCodeField
from app.services import MemoryBroker, FakeVerificationService
from app.services.authentication import UnAuthorizedError, AuthService
from app.services.verification import SMSVerificationService, VerificationCodeAlreadySendError, InvalidVerificationCodeError
from app.services.notification import FakeSMSNotification, SMSNotification


class TestAuthService(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.service = AuthService(
            broker=MemoryBroker(delay=0.1),
            db=MemoryDatabase(),
            cache=MemoryCache(),
            verification=FakeVerificationService()
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

    def test_authenticate_unknown_user(self):
        try:
            self.service.authenticate(
                RealUserAuthenticationIn(
                    national_code=NationalCodeField('1111111111'),
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
            national_code=NationalCodeField('1111111111'),
            first_name='first_name',
            last_name='last_name',
            phone_number=PhoneNumberField('1111111111'),
            plain_password='plain_password',
            roles=[
                UserRole(platform='*', names=['admin'])
            ],
        )
        self.service.database.users.create(user)

        try:
            self.service.authenticate(
                RealUserAuthenticationIn(
                    national_code=NationalCodeField(user.national_code),
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
            national_code=NationalCodeField('1111111111'),
            first_name='first_name',
            last_name='last_name',
            phone_number=PhoneNumberField('1111111111'),
            plain_password='plain_password',
            roles=[
                UserRole(platform='*', names=['admin'])
            ],
        )
        self.service.database.users.create(user)

        try:
            self.service.authenticate(
                RealUserAuthenticationIn(
                    national_code=NationalCodeField(user.national_code),
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
            national_code=NationalCodeField('1111111111'),
            first_name='first_name',
            last_name='last_name',
            phone_number=PhoneNumberField('1111111111'),
            plain_password='plain_password',
            roles=[
                UserRole(platform='*', names=['admin'])
            ],
        )
        self.service.database.users.create(user)

        db_user = self.service.authenticate(
            RealUserAuthenticationIn(
                national_code=NationalCodeField(user.national_code),
                password='plain_password',
                current_platform=PlatformSpecificationIn(
                    platform='*',
                    role='admin'
                )
            )
        )

        assert user == db_user

    async def test_register_real_user(self):
        user = RealUser.new_user(
            national_code=NationalCodeField('1111111111'),
            first_name='first_name',
            last_name='last_name',
            phone_number=PhoneNumberField('1111111111'),
            plain_password='plain_password',
            roles=[
                UserRole(platform='*', names=['admin'])
            ],
        )

        await self.service.register(
            RealUserRegistrationIn(
                verification=RealUserCodeVerificationIn(
                    code=VerificationCodeField(),
                    national_code=NationalCodeField(user.national_code),
                    phone_number=PhoneNumberField(user.phone_number),
                    verify_as='NEW_USER',
                ),
                current_platform=PlatformSpecificationIn(
                    platform='*',
                    role='admin'
                ),
                first_name=user.first_name,
                last_name=user.last_name,
                password1='plain_password',
                password2='plain_password',
            )
        )

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

    async def test_verify_as_new_user_first_message(self):
        await self.service.send(
            RealUserSendSMSCodeIn(
                national_code=NationalCodeField('1111111111'),
                phone_number=PhoneNumberField('1111111111'),
                verify_as='NEW_USER'
            )
        )
        assert self.service.cache.get('1111111111')

    async def test_verify_as_new_user_second_message(self):
        await self.service.send(
            RealUserSendSMSCodeIn(
                national_code=NationalCodeField('1111111111'),
                phone_number=PhoneNumberField('1111111111'),
                verify_as='NEW_USER'
            )
        )

        try:
            await self.service.send(
                RealUserSendSMSCodeIn(
                    national_code=NationalCodeField('1111111111'),
                    phone_number=PhoneNumberField('1111111111'),
                    verify_as='NEW_USER'
                )
            )
            assert False
        except Exception as exc:
            assert isinstance(exc, VerificationCodeAlreadySendError)

    async def test_verify_as_new_with_already_registered_user(self):
        user = RealUser.new_user(
            national_code=NationalCodeField('1111111111'),
            first_name='first_name',
            last_name='last_name',
            phone_number=PhoneNumberField('1111111111'),
            plain_password='plain_password',
            roles=[
                UserRole(platform='*', names=['admin'])
            ],
        )
        self.service.database.users.create(user)

        try:
            await self.service.send(
                RealUserSendSMSCodeIn(
                    national_code=NationalCodeField('1111111111'),
                    phone_number=PhoneNumberField('1111111111'),
                    verify_as='NEW_USER'
                )
            )
            assert False
        except Exception as exc:
            assert isinstance(exc, errors.UserAlreadyExist)

    async def test_verify_none_existent_user(self):
        try:
            await self.service.send(
                RealUserSendSMSCodeIn(
                    national_code=NationalCodeField('1111111111'),
                    phone_number=PhoneNumberField('1111111111'),
                    verify_as='EXISTENT_USER'
                )
            )
            assert False
        except Exception as exc:
            assert isinstance(exc, errors.UserDoesNotExist)

    async def test_verify_code_with_wrong_code(self):
        await self.service.send(
            RealUserSendSMSCodeIn(
                national_code=NationalCodeField('1111111111'),
                phone_number=PhoneNumberField('1111111111'),
                verify_as='NEW_USER'
            )
        )

        info = self.service.cache.get('1111111111')
        assert info
        correct_code = info.get('code')
        assert correct_code

        with self.assertRaises(InvalidVerificationCodeError):
            await self.service.verify(
                RealUserCodeVerificationIn(
                    national_code=NationalCodeField('1111111111'),
                    phone_number=PhoneNumberField('1111111111'),
                    verify_as='NEW_USER',
                    code=VerificationCodeField(int(correct_code) - 1)
                )
            )

    async def test_verify_code_with_correct_code(self):
        await self.service.send(
            RealUserSendSMSCodeIn(
                national_code=NationalCodeField('1111111111'),
                phone_number=PhoneNumberField('1111111111'),
                verify_as='NEW_USER'
            )
        )

        info = self.service.cache.get('1111111111')
        assert info
        correct_code = info.get('code')
        assert correct_code

        await self.service.verify(
            RealUserCodeVerificationIn(
                national_code=NationalCodeField('1111111111'),
                phone_number=PhoneNumberField('1111111111'),
                verify_as='NEW_USER',
                code=VerificationCodeField(correct_code)
            )
        )
