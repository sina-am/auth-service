from typing import Any
from pydantic import BaseModel, validator, BaseConfig
from app.types.fields import UserType
from datetime import datetime
from bson import ObjectId


class MongoModel(BaseModel):
    """
    Base model for mapping pydantic objects to mongo compatible dictionary.
    Stolen from: https://lightrun.com/answers/tiangolo-fastapi-question-fastapi--mongodb---the-full-guide
    """
    class Config(BaseConfig):
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            ObjectId: lambda oid: str(oid),
        }


class BaseModelOut(MongoModel):
    """ Base class for mapping database schemas to output models. """

    @classmethod
    def from_db(cls, schema: Any):
        raise NotImplementedError()


class BaseModelIn(MongoModel):
    """ Base class for map input data into database schemas. """

    def to_model(self) -> Any:
        raise NotImplementedError()


class PlatformSpecificationOut(BaseModel):
    platform: str
    role: str


class PlatformSpecificationIn(PlatformSpecificationOut):
    ...
