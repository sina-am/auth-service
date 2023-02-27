from datetime import datetime, date
from typing import List, Optional, Union
from app.models.base import MongoModel, BaseModelOut
from app.models.role import UserRole
from app.types.enums import UserType 
from app.types.fields import ObjectIdField, CompanyCodeField, CompanyDomainField, GenderField ,\
     NationalCodeField, PhoneNumberField, PostCodeField, UserTypeField

from app.core.security import get_password_hash 
from pydantic import BaseModel, EmailStr, Field, validator, HttpUrl
from app.models.verification import LegalUserCodeVerificationIn, RealUserCodeVerificationIn
from app.models.base import BaseModelIn, PlatformSpecificationIn, PlatformSpecificationOut 
from app.models.profile import ContactInformation, ContactInformationIn, ContactInformationOut
from app.utils.translation import _
from app.utils import path 
from app.utils.utils import date_to_datetime


class User(MongoModel):
    """ Common fields for both real users and legal users. """
    id: Optional[ObjectIdField] = Field(alias='_id')
    password: str
    phone_number: str 
    roles: List[UserRole]
    type: UserTypeField
    last_login: datetime
    created_at: datetime
    
    picture_url: str
    contact_information: Optional[ContactInformation]

    def set_password(self, plain_password: str):
        self.password = get_password_hash(plain_password) 
        
    def has_role(self, platform: str, role_name: str) -> bool:
        for role in self.roles:
            if role.platform == platform:
                if role_name in role.names:
                    return True
                return False
        return False

    def is_real(self):
        return self.type == UserType.REAL

    def is_legal(self):
        return self.type == UserType.LEGAL
        
    class Config:
        use_enum_values = True


class RealUser(User):
    """ real user fields. """
    type: Optional[UserTypeField] = UserType.REAL
    national_code: str 
    first_name: str
    last_name: str
    
    father_name: Optional[str]
    gender: Optional[GenderField]
    birth_day: Optional[datetime]

    @staticmethod
    def new_user(
        national_code: str, 
        phone_number: str,
        first_name: str, 
        last_name: str,
        plain_password: str,
        roles: List[UserRole]
    ) -> "RealUser":

        return RealUser(
            national_code=national_code,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            password=get_password_hash(plain_password), 
            roles=roles,
            last_login=datetime.utcnow(),
            created_at=datetime.utcnow(),
            picture_url=path.get_default_profile_picture_url()
        )


class RealUserOut(BaseModelOut):
    """ Real user representation through APIs. """
    national_code: str 
    first_name: str
    last_name: str
    father_name: Optional[str]
    gender: Optional[GenderField]
    birth_day: Optional[date]

    @classmethod
    def from_db(cls, user: RealUser):
        return cls(
            national_code=user.national_code,
            first_name=user.first_name,
            last_name=user.last_name,
            father_name=user.father_name,
            gender=user.gender,
            birth_day=user.birth_day
        )


class RealUserCreationIn(BaseModelIn):
    """ Model for creating a new real user. """
    national_code: NationalCodeField
    phone_number: PhoneNumberField
    roles: List[UserRole]
    first_name: str
    last_name: str
    password1: str
    password2: str

    def to_model(self) -> RealUser:
        return RealUser.new_user(
            national_code=self.national_code, 
            phone_number=self.phone_number,
            first_name=self.first_name, 
            last_name=self.last_name, 
            plain_password=self.password1, 
            roles=self.roles
        )
        
    @validator('password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'password1' in values and v != values['password1']:
            raise ValueError(_('passwords do not match'))
        return v


class RealUserRegistrationIn(BaseModelIn):
    """ Model for creating a new user using verification code. """
    verification: RealUserCodeVerificationIn
    current_platform: PlatformSpecificationIn
    first_name: str
    last_name: str
    password1: str
    password2: str

    @validator('verification')
    def check_if_verify_as_is_correct(cls, v: RealUserCodeVerificationIn):
        if v.verify_as == "NEW_USER":
            return v
        raise ValueError(_("verify_as should be NEW_USER"))

    @validator('password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'password1' in values and v != values['password1']:
            raise ValueError(_('passwords do not match'))
        return v

    def to_model(self) -> RealUser:
        return RealUser.new_user(
            national_code=self.verification.national_code, 
            phone_number=self.verification.phone_number,
            first_name=self.first_name, 
            last_name=self.last_name, 
            plain_password=self.password1, 
            roles=[
                UserRole(
                    platform=self.current_platform.platform, 
                    names=[self.current_platform.role]
                )
            ]
        )


class LegalUser(User):
    """ Legal user fields. """
    type: Optional[UserTypeField] = UserType.LEGAL
    company_code: str 
    company_name: str
    domain: str 
    title: Optional[str]

    @staticmethod
    def new_user(
        company_code: str, 
        phone_number: str,
        company_name: str,
        domain: str,
        plain_password: str,
        roles: List[UserRole],
    ) -> "LegalUser":

        return LegalUser(
            company_code=company_code,
            phone_number=phone_number,
            company_name=company_name,
            domain=domain,
            password=get_password_hash(plain_password), 
            roles=roles,
            last_login=datetime.utcnow(),
            created_at=datetime.utcnow(),
            picture_url=path.get_default_profile_picture_url()
        )


class LegalUserOut(BaseModelOut):
    company_code: str 
    name: str
    domain: str
    title: Optional[str]

    @classmethod
    def from_db(cls, user: LegalUser):
        return cls(
            company_code=user.company_code,
            name=user.company_name,
            domain=user.domain,
            title=user.title
        )


class LegalUserCreationIn(BaseModelIn):
    """ Model for creating a new legal user. """
    company_code: CompanyCodeField 
    phone_number: PhoneNumberField
    roles: List[UserRole]
    company_name: str
    domain: CompanyDomainField
    password1: str
    password2: str

    def to_model(self) -> LegalUser:
        return LegalUser.new_user(
            company_code=self.company_code, 
            phone_number=self.phone_number,
            company_name=self.company_name, 
            domain=self.domain, 
            plain_password=self.password1, 
            roles=self.roles
        )
        
    @validator('password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'password1' in values and v != values['password1']:
            raise ValueError(_('passwords do not match'))
        return v


class LegalUserRegistrationIn(BaseModelIn):
    verification: LegalUserCodeVerificationIn
    current_platform: PlatformSpecificationIn
    company_name: str
    domain: CompanyDomainField
    password1: str
    password2: str

    @validator('verification')
    def check_if_verify_as_is_correct(cls, v: RealUserCodeVerificationIn):
        if v.verify_as == "NEW_USER":
            return v
        raise ValueError(_("verify_as should be NEW_USER"))

    @validator('password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'password1' in values and v != values['password1']:
            raise ValueError(_('passwords do not match'))
        return v

    def to_model(self) -> LegalUser:
        return LegalUser.new_user(
            company_code=self.verification.company_code, 
            phone_number=self.verification.phone_number, 
            company_name=self.company_name, 
            domain=self.domain, 
            plain_password=self.password1, 
            roles=[
                UserRole(
                    platform=self.current_platform.platform, 
                    names=[self.current_platform.role]
                )
            ]
        )
 

class ProfileOut(BaseModelOut):
    id: Optional[ObjectIdField] = Field(alias='_id')
    phone_number: Optional[str]
    type: Optional[UserTypeField]
    legal_user: Optional[LegalUserOut]
    real_user: Optional[RealUserOut]
    roles: Optional[List[UserRole]]
    current_platform: Optional[PlatformSpecificationOut]
    contact_information: Optional[ContactInformationOut]
    picture_url: Optional[str]

    @classmethod
    def from_db(cls, 
        user: Union[RealUser, LegalUser], 
        current_platform: Union[PlatformSpecificationOut, None] = None) -> "ProfileOut":

        return cls(
            _id=user.id,
            phone_number=user.phone_number,
            type=user.type,
            legal_user=LegalUserOut.from_db(user) if user.is_legal() else None,
            real_user=RealUserOut.from_db(user) if user.is_real() else None,
            roles=user.roles,
            current_platform=current_platform,
            contact_information=ContactInformationOut.from_db(user.contact_information),
            picture_url=path.get_full_url(user.picture_url)
        )
        
    class Config:
        use_enum_values = True


class UserUpdateIn(BaseModelIn):
    """ Model for updating user data. """
    class RealUserIn(BaseModelIn):
        """ Model for updating real user data. """
        first_name: Optional[str]
        last_name: Optional[str]
        father_name: Optional[str]
        gender: Optional[GenderField]
        birth_day: Optional[date]

        class Config:
            use_enum_values = True

    class LegalUserIn(BaseModel):
        """ Model for updating legal user data. """
        name: Optional[str]
        domain: Optional[str]
        title: Optional[str]


    legal_user: Optional[LegalUserIn]
    real_user: Optional[RealUserIn]
    contact_information: Optional[ContactInformationIn]
    picture_url: Optional[HttpUrl]

    @validator('picture_url')
    def validate_hostname(cls, v):
        if path.host_validation(v):
            return path.trim_domain(v)
        raise ValueError('invalid domain')

    def to_model(self, user: Union[RealUser, LegalUser]) -> Union[RealUser, LegalUser]:
        user.picture_url = self.picture_url 

        if user.type == UserType.REAL and self.real_user:
            user.first_name = self.real_user.first_name
            user.last_name = self.real_user.last_name
            user.father_name = self.real_user.father_name
            user.gender = self.real_user.gender
            user.birth_day = date_to_datetime(self.real_user.birth_day) if self.real_user.birth_day else user.birth_day  
        elif user.type == UserType.LEGAL and self.legal_user:
            user.domain = self.legal_user.domain
            user.company_name = self.legal_user.name
            user.title = self.legal_user.title

        if self.contact_information:
            user.contact_information = self.contact_information.to_model() 
        return user


class PasswordUpdateIn(BaseModel):
    verification: Union[RealUserCodeVerificationIn, LegalUserCodeVerificationIn]
    password1: str
    password2: str

    @validator('password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'password1' in values and v != values['password1']:
            raise ValueError(_('passwords do not match'))
        return v

    @validator('verification')
    def check_if_verify_as_is_correct(cls, v: RealUserCodeVerificationIn):
        if v.verify_as == "EXISTENT_USER":
            return v
        raise ValueError(_("verify_as should be EXISTENT_USER"))


class PhoneNumberUpdateIn(BaseModel):
    verification: Union[RealUserCodeVerificationIn, LegalUserCodeVerificationIn]
    phone_number: PhoneNumberField = Field(
        description='This should always be equal to the verfication.phone_number')

    @validator('verification')
    def check_if_verify_as_is_correct(cls, v: RealUserCodeVerificationIn):
        if v.verify_as == "EXISTENT_USER":
            return v
        raise ValueError(_("verify_as should be EXISTENT_USER"))

    @validator('phone_number')
    def check_if_match(cls, v: PhoneNumberField, values):
        if values.get('verification') and v == values['verification'].phone_number:
            return v
        raise ValueError(_("phone_number should be eqaul to the verification.phone_number"))
        