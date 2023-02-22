from pydantic import Field, validator
from typing import List, Optional
from app.models.base import MongoModel, BaseModelIn
from app.types.fields import ObjectIdField
from bson import ObjectId

   
class City(MongoModel):
    id: Optional[ObjectIdField] = Field(alias='_id')
    name: str
 
    @validator("id", pre=True, always=True)
    def generate_id_if_none(cls, v: ObjectId):
        return ObjectId() if not v else v 
        

class Province(MongoModel):
    id: Optional[ObjectIdField] = Field(alias='_id')
    name: str
    cities: List[City]



class CityIn(BaseModelIn):
    name: str

    def to_model(self) -> City:
        return City(
            name=self.name # type: ignore
        )


class ProvinceIn(BaseModelIn):
    name: str
    cities: List[CityIn]

    def to_model(self) -> Province:
        return Province(    # type: ignore
            name=self.name,
            cities=[city.to_model() for city in self.cities]
        )