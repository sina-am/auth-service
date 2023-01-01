from typing import Optional
from pydantic import BaseSettings, RedisDsn, BaseModel


class MelipayamakSettings(BaseModel):
    username: Optional[str]
    password: Optional[str]
    phone: Optional[str]


class S3Settings(BaseModel):
    endpoint_url: str
    aws_access_key_id: str
    aws_secret_access_key: str
    bucket_name: str


class RabitMQSettings(BaseModel):
    address: str
    port: int = 5672
    username: Optional[str]
    password: Optional[str]


class MongoDBSettings(BaseModel):
    uri: str
    database: str = 'users'
    

class RedisSettings(BaseModel):
    address: RedisDsn
    password: Optional[str]


class GlobalSettings(BaseSettings):
    debug: bool = True
    mongodb: MongoDBSettings
    rabbitmq: RabitMQSettings
    s3: S3Settings
    melipayamak: Optional[MelipayamakSettings]
    redis: RedisSettings
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_time: int = 30
    datetime_format = '%Y-%m-%d %H:%M:%S'
    user_max_failed_attempt: int = 5
    
    class Config:
        env_nested_delimiter = '__'
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = GlobalSettings()
