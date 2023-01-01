from unittest import TestCase
from app.database.mongo import MongoDatabase
from app.models.province import Province, City
from bson import ObjectId 


class TestMongoProvinceStorage(TestCase):
    def setUp(self):
        self.storage = MongoDatabase()

    def test_create(self):
        province = Province(name='p1', cities=[
            City(name='c11', id=ObjectId()), 
            City(name='c12', id=ObjectId())
        ])

        self.storage.provinces.create(province)
        self.assertIsNotNone(province.id)


    def test_get_all(self): 
        province = Province(name='p1', cities=[
            City(name='c11', id=ObjectId()), 
            City(name='c12', id=ObjectId())
        ])
        self.storage.provinces.create(province)

        provinces = self.storage.provinces.get_all()
        self.assertEqual(province.id, provinces[0].id)

    def test_get_by_city_id(self):
        city = City(name='c12', id=ObjectId())
        province = Province(name='p1', cities=[
            City(name='c11', id=ObjectId()), 
            city 
        ])
        self.storage.provinces.create(province)

        province = self.storage.provinces.get_by_city_id(city.id)
        self.assertEqual(city, province.cities[0])

    def tearDown(self):
        self.storage.provinces.collection.delete_many({})
       