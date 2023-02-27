from typing import Dict, Union
from datetime import timedelta
import json
from redis import Redis


class Cache:
    def get(self, key: str) -> Union[dict,None]: ...
    
    def set(self, key: str, value: dict, ttl: Union[float,timedelta]): ...

    def delete(self, key: str): ...
    
    def has(self, key: str) -> bool: ...
    
    def ping(self) -> bool: ...
        

class RedisCache(Cache):
    def __init__(self, host: str, port: int, db: int, password: str) -> None:
        self.redis = Redis(host, port, db, password)
    
    def get(self, key: str) -> Union[dict, None]: 
        value = self.redis.get(key)
        if not value:
            return None
        return json.loads(value)

    def set(self, key: str, value: dict, ttl: Union[float, timedelta]):
        self.redis.set(key, json.dumps(value), ttl)
    
    def delete(self, key: str):
        self.redis.delete(key)
    
    def has(self, key: str) -> bool:
        if self.redis.get(key):
            return True 
        return False
    
    def ping(self) -> bool:
        return self.redis.ping()


class MemoryCache(Cache):
    def __init__(self) -> None:
        self.cache: Dict[str, dict] = {} 

    def get(self, key: str) -> Union[dict, None]:
        return self.cache.get(key)
    
    def set(self, key: str, value: dict, ttl: Union[float, timedelta] = 0):
        self.cache.update({key: value})

    def delete(self, key: str):
        if self.cache.get(key):
            del self.cache[key]
    
    def has(self, key: str) -> bool:
        if self.cache.get(key):
            return True
        return False
    
    def ping(self) -> bool:
        return True
