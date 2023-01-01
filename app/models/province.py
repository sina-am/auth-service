from pydantic import Field
from typing import List, Optional
from app.models.base import MongoModel, BaseModelOut, BaseModelIn
from app.types.fields import ObjectIdField
from bson import ObjectId

   
class City(MongoModel):
    id: ObjectIdField = Field(alias='_id')
    name: str
 

class Province(MongoModel):
    id: Optional[ObjectIdField] = Field(alias='_id')
    name: str
    cities: List[City]


class CityOut(BaseModelOut):
    id: ObjectIdField = Field(alias='_id')
    name: str

    @classmethod
    def from_db(cls, city: City):
        return cls(
            id=city.id,
            name=city.name
        )


class ProvinceOut(BaseModelOut):
    id: ObjectIdField = Field(alias='_id')
    name: str
    cities: List[CityOut]

    @classmethod
    def from_db(cls, province: Province):
        return cls(
            id=province.id,
            name=province.name,
            cities=province.cities
        )


class CityIn(BaseModelIn):
    name: str

    def to_model(self) -> City:
        return City(
            id=ObjectId(),
            name=self.name
        )


class ProvinceIn(BaseModelIn):
    name: str
    cities: List[CityIn]

    def to_model(self) -> Province:
        return Province(
            name=self.name,
            cities=[city.to_model() for city in self.cities]
        )