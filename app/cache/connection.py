from redis import ConnectionPool
from app.core.config import settings


redis_connection_pool = ConnectionPool(
    host=settings.redis.address.host, 
    port=settings.redis.address.port, 
    db=0,
    password=settings.redis.password
)