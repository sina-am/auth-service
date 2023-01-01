from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.role import UserRole
from app.models.base import MongoModel, PlatformSpecificationOut
from app.types.fields import ObjectIdField, UserTypeField


class JwtUser(MongoModel):
    id: ObjectIdField = Field(alias='_id')
    roles: List[UserRole]
    type: UserTypeField

    class Config:  
        use_enum_values = True

        
class JwtPayload(BaseModel):
    user: JwtUser
    current_platform: PlatformSpecificationOut
    expiration: datetime

    class Config:  
        use_enum_values = True


class AccessTokenOut(BaseModel):
    token: str
    type: str = 'bearer'
