import pickle

import redis
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends, Header
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connect_db import get_db
from src.repository import users as repository_users
from src.conf.config import settings
from src.conf.messages import (
    FAIL_EMAIL_VERIFICATION,
    INVALID_SCOPE,
    INVALID_TOKEN,
    NOT_VALIDATE_CREDENTIALS,
)

from src.conf.constants import TOKEN_LIFE_TIME

class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    redis_cache = redis.Redis(
        host=settings.redis_host,
        password=settings.redis_password,
        username=settings.redis_username,
        ssl=True,
        encoding="utf-8",
        # decode_responses=True
    )

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)

    # define a function to generate a new access token
    async def create_access_token(
        self, data: dict, expires_delta: int | None = None
    ):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(minutes=TOKEN_LIFE_TIME)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"}
        )
        encoded_access_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_access_token

    # define a function to generate a new refresh token
    async def create_refresh_token(
        self, data: dict, expires_delta: float | None = None
    ):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"}
        )
        encoded_refresh_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_refresh_token

    def create_email_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=3)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "email_token"}
        )
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def decode_refresh_token(self, refresh_token: str):
        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_SCOPE
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=NOT_VALIDATE_CREDENTIALS,
            )

    async def get_current_user(
        self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
    ):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=NOT_VALIDATE_CREDENTIALS
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "access_token":
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
            # check token in blacklist
            
            is_invalid_token = await repository_users.is_blacklisted_token(token, db)
            if is_invalid_token:
                raise credentials_exception

        except JWTError as e:
            raise credentials_exception

        # get user from redis_cache
        user = self.redis_cache.get(f"user:{email}")
        if user is None:
            print("--- USER POSTGRES ---")
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.redis_cache.set(f"user:{email}", pickle.dumps(user))
            self.redis_cache.expire(f"user:{email}", 900)
        else:
            print("--- USER CACHE ---")
            user = pickle.loads(user)
        return user

    async def get_email_from_token(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "email_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_SCOPE
            )
        except JWTError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=FAIL_EMAIL_VERIFICATION,
            )
            
    # Decorator for token verification
    async def is_token_valid(self, token: str = Header("Authorization")) -> bool:
        print("THIS IS TOKEN:", token)
        try:
            decoded_token = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])

            # Get the expiration time from the decoded token
            expiration_time = decoded_token["exp"]

            # Получаем текущее время            # Get the current time

            current_time = datetime.datetime.utcnow()

            # Comparing the current time with the expiration time
            if current_time < datetime.datetime.fromtimestamp(expiration_time):
                return True
            else:
                return False
        except jwt.ExpiredSignatureError:
            return False
        except jwt.DecodeError:
            return False
        except jwt.InvalidTokenError:
            return False

auth_service = Auth()
