from unittest import TestCase
from app.cache import MemoryCache, RedisCache


class TestMemoryCache(TestCase):
    def setUp(self) -> None:
        self.cache = MemoryCache()

    def test_ping(self):
        assert self.cache.ping() is True

    def test_get_with_existent_key(self):
        data = {'test': 'test'}
        self.cache.set('key1', data, 10)

        cached_data = self.cache.get('key1')
        assert data == cached_data

    def test_get_with_none_existent_key(self):
        data = {'test': 'test'}
        self.cache.set('key1', data, 10)

        assert self.cache.get('key2') is None

    def test_has_with_existent_key(self):
        data = {'test': 'test'}
        self.cache.set('key1', data, 10)

        assert self.cache.has('key1') is True

    def test_has_with_none_existent_key(self):
        data = {'test': 'test'}
        self.cache.set('key1', data, 10)

        assert self.cache.has('key2') is False

    def test_delete_with_existent_key(self):
        data = {'test': 'test'}
        self.cache.set('key1', data, 10)

        assert self.cache.has('key1') is True
        self.cache.delete('key1')
        assert self.cache.has('key1') is False

    def test_delete_with_none_existent_key(self):
        assert self.cache.has('key1') is False
        self.cache.delete('key1')
        assert self.cache.has('key1') is False


class TestRedisCache(TestCase):
    def setUp(self) -> None:
        self.cache = RedisCache(
            host='localhost', port=6379, db=0, password="")

    def tearDown(self) -> None:
        self.cache.redis.delete('*')

    def test_ping(self):
        assert self.cache.ping() is True

    def test_get_with_existent_key(self):
        data = {'test': 'test'}
        self.cache.set('key1', data, 10)

        cached_data = self.cache.get('key1')
        assert data == cached_data

    def test_get_with_none_existent_key(self):
        data = {'test': 'test'}
        self.cache.set('key1', data, 10)

        assert self.cache.get('key2') is None

    def test_has_with_existent_key(self):
        data = {'test': 'test'}
        self.cache.set('key1', data, 10)

        assert self.cache.has('key1') is True

    def test_has_with_none_existent_key(self):
        data = {'test': 'test'}
        self.cache.set('key1', data, 10)

        assert self.cache.has('key2') is False

    def test_delete_with_existent_key(self):
        data = {'test': 'test'}
        self.cache.set('key1', data, 10)

        assert self.cache.has('key1') is True
        self.cache.delete('key1')
        assert self.cache.has('key1') is False

    def test_delete_with_none_existent_key(self):
        assert self.cache.has('key1') is False
        self.cache.delete('key1')
        assert self.cache.has('key1') is False
