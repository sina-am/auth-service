from datetime import date
import mimetypes
from pydantic import EmailStr, Field, validator, HttpUrl
from typing import List, Optional, Union
from app.models.base import MongoModel, BaseModelIn, BaseModelOut
from app.types.fields import ObjectIdField, PhoneNumberField, PostCodeField
from app.utils.translation import _


class Location(MongoModel):
    lat: float
    long: float


class SocialMedia(MongoModel):
    url: str
    name: str


class ContactInformation(MongoModel):
    city_id: Optional[ObjectIdField]
    post_code: Optional[PostCodeField]
    phone_number: Optional[PhoneNumberField]
    email: Optional[EmailStr]
    address: Optional[str]
    location: Optional[Location]
    fax: Optional[str]
    video_call_link: Optional[str]
    social_media_links: Optional[List[SocialMedia]]


class ContactInformationOut(BaseModelOut):
    city_id: Optional[ObjectIdField]
    post_code: Optional[PostCodeField]
    address: Optional[str]
    location: Optional[Location]
    phone_number: Optional[PhoneNumberField]
    email: Optional[EmailStr]
    video_call_link: Optional[str]
    social_media_links: Optional[List[SocialMedia]]
    fax: Optional[str]

    @classmethod
    def from_db(cls, contact: ContactInformation):
        if not contact:
            return cls()

        return cls(
            city_id=contact.city_id,
            post_code=contact.post_code,
            address=contact.address,
            location=contact.location,
            phone_number=contact.phone_number,
            email=contact.email,
            video_call_link=contact.video_call_link,
            social_media_links=contact.social_media_links,
            fax=contact.fax
        )


class ContactInformationIn(BaseModelIn):
    city_id: Optional[ObjectIdField]
    post_code: Optional[PostCodeField]
    address: Optional[str]
    location: Optional[Location]
    phone_number: Optional[PhoneNumberField]
    email: Optional[EmailStr]
    video_call_link: Optional[str]
    social_media_links: Optional[List[SocialMedia]]
    fax: Optional[str]

    def to_model(self) -> ContactInformation:
        return ContactInformation(
            city_id=self.city_id,
            post_code=self.post_code,
            address=self.address,
            location=self.location,
            phone_number=self.phone_number,
            email=self.email,
            video_call_link=self.video_call_link,
            social_media_links=self.social_media_links,
            fax=self.fax
        )


class PictureIn(BaseModelIn):
    content_type: str = Field(description='Standard mime type')
    content_length: int = Field(
        description='File size in byte', gt=100, lt=52428800)

    @validator('content_type')
    def image_media_type_validation(cls, v):
        if mimetypes.guess_extension(v):
            if v.split('/')[0] == 'image':
                return v
        raise ValueError('invalid mime type for image')


class PictureOut(BaseModelOut):
    url: str
