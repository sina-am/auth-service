from typing import Union

from app.cache import Cache
from app.core.security import verify_password
from app.models.profile import PictureIn
from app.models.role import Role, UserRole
from app.models.user import LegalUser, RealUser, RealUserRegistrationIn, LegalUserRegistrationIn
from app.models.auth import RealUserAuthenticationIn, LegalUserAuthenticationIn
from app.types.fields import NationalCodeField, PhoneNumberField
from app.database import errors as dberrors, Database
from app.services.s3 import S3Service
from app.services.broker import Broker
from app.services.verification import VerificationService
from app.core.errors import MyException


class UnAuthorizedError(MyException):
    pass


class AuthService:
    def __init__(self,
                 broker: Broker,
                 db: Database,
                 cache: Cache,
                 verification: VerificationService):

        self.broker = broker
        self.database = db
        self.verification = verification
        self.cache = cache
        self.s3 = S3Service('images/profile')

    def create_profile_picture_url(self, info: PictureIn, user_id: str) -> str:
        """ Create a object for profile picture and return the presigned url. """
        return self.s3.generate_presigned_url(
            user_id,
            info.content_type,
            info.content_length
        )

    def authenticate(self, credentials: Union[RealUserAuthenticationIn, LegalUserAuthenticationIn]) -> Union[RealUser, LegalUser]:
        try:
            if isinstance(credentials, RealUserAuthenticationIn):
                user = self.database.users.get_by_national_code(
                    credentials.national_code)
            else:
                user = self.database.users.get_by_company_code(
                    credentials.company_code)
        except dberrors.UserDoesNotExist:
            raise UnAuthorizedError("invalid credentials")

        if not verify_password(credentials.password, user.password):
            raise UnAuthorizedError("invalid credentials")

        if not user.has_role(credentials.current_platform.platform, credentials.current_platform.role):
            raise UnAuthorizedError(
                "you don't have this role in the given platform")

        self.database.users.update_last_login(user)
        return user

    async def register(self, u: Union[RealUserRegistrationIn, LegalUserRegistrationIn]):
        await self.verification.verify(u.verification, delete_on_success=True)

        new_user = self.database.users.create(u.to_model())
        await self.broker.publish(
            queue_name='registration',
            message=new_user.dict()
        )

    def create_admin(
            self,
            national_code: NationalCodeField,
            phone_number: PhoneNumberField,
            first_name: str,
            last_name: str,
            password: str
    ) -> RealUser:
        try:
            self.database.roles.get_by_platform("*")
        except dberrors.RoleDoesNotExist:
            self.database.roles.create(
                Role(platform='*', names=['admin']))  # type: ignore

        admin = RealUser.new_user(
            national_code,
            phone_number,
            first_name,
            last_name,
            password,
            [UserRole(platform='*', names=['admin'])]
        )

        return self.database.users.create(admin)  # type: ignore
