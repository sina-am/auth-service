from unittest import TestCase
from app.database import MongoDatabase
from app.models.province import Province, City
from bson import ObjectId 


class TestMongoProvinceCollection(TestCase):
    def setUp(self):
        self.database = MongoDatabase("mongodb://localhost", "test_database")

    def test_create(self):
        province = Province(name='p1', cities=[
            City(name='c11', id=ObjectId()), 
            City(name='c12', id=ObjectId())
        ])

        self.database.provinces.create(province)
        self.assertIsNotNone(province.id)


    def test_get_all(self): 
        province = Province(name='p1', cities=[
            City(name='c11', id=ObjectId()), 
            City(name='c12', id=ObjectId())
        ])
        self.database.provinces.create(province)

        provinces = self.database.provinces.get_all()
        self.assertEqual(province.id, provinces[0].id)

    def test_get_by_city_id(self):
        city = City(name='c12', id=ObjectId())
        province = Province(name='p1', cities=[
            City(name='c11', id=ObjectId()), 
            city 
        ])
        self.database.provinces.create(province)

        province = self.database.provinces.get_by_city_id(city.id)
        self.assertEqual(city, province.cities[0])

    def tearDown(self):
        self.database.provinces.collection.delete_many({})
       