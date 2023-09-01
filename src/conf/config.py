import cloudinary
from pydantic_settings import BaseSettings
import redis
import redis.asyncio


def init_cloudinary():
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )

async def init_async_redis():
    return redis.asyncio.Redis(
        host=settings.redis_host,
        password=settings.redis_password,
        username=settings.redis_username,
        ssl=True,
        encoding="utf-8",
        # decode_responses=True
    )
    
class Settings(BaseSettings):
    sqlalchemy_database_url: str = (
        "postgresql+psycopg2://user:password@localhost:5432/postgres"
    )
    secret_key: str = "secretkey"
    algorithm: str = "HS256"
    mail_username: str = "example@meta.ua"
    mail_password: str = "secretPassword"
    mail_from: str = "example@meta.ua"
    mail_port: int = 465
    mail_server: str = "smtp.meta.ua"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_username: str = ""
    cloudinary_name: str = "name"
    cloudinary_api_key: str = "1234567890"
    cloudinary_api_secret: str = "secret"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
