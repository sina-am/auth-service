from unittest import TestCase
from app.cache import MemoryCache


class TestMemoryCache(TestCase):
    def setUp(self) -> None:
        self.cache = MemoryCache()

    def test_set_and_get(self):
        data = {'key': 'value'}
        self.cache.set('key1', data)
        assert data == self.cache.get('key1')
