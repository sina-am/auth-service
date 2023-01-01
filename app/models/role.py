from typing import List, Optional
from app.models.base import MongoModel, BaseModelIn
from app.types.fields import ObjectIdField 
from pydantic import BaseModel, Field


class Role(MongoModel):
    id: Optional[ObjectIdField] = Field(alias='_id')
    platform: str 
    names: List[str]


class UserRole(BaseModel):
    """ Subset of Role model. """
    platform: str
    names: List[str]


class RoleCreationIn(BaseModelIn):
    platform: str 
    names: List[str]

    def to_model(self) -> Role:
        return Role(
            platform=self.platform,
            names=self.names
        )