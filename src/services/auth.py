import pickle
from uvicorn.config import logger


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
from src.conf.config import init_async_redis

class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    
    def __init__(self):
        self._redis_cache = None

    @property
    async def redis_cache(self):
        """
        Get a Redis cache for storing user data.

        This property returns a Redis cache for storing user data if it's not already initialized.

        :return: The Redis cache.
        :rtype: aioredis.Redis
        """

        if self._redis_cache is None:
            self._redis_cache = await init_async_redis()
        return self._redis_cache

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)

    async def create_access_token(
        self, data: dict, expires_delta: int | None = None
    ):
        """
        Create an access token.

        This function generates an access token with an optional expiration time.

        :param data: dict: The data to include in the token payload.
        :param expires_delta: int | None: The token's expiration time (in minutes).
        :return: The encoded access token.
        :rtype: str
        """
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

    async def create_refresh_token(
        self, data: dict, expires_delta: float | None = None
    ):
        """
        Create a refresh token.

        This function generates a refresh token with an optional expiration time.

        :param data: dict: The data to include in the token payload.
        :param expires_delta: float | None: The token's expiration time (in seconds).
        :return: The encoded refresh token.
        :rtype: str
        """
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

    async def decode_token(self, token: str):
        """
        Decode a JWT token.

        This function decodes a JWT token and validates its scope.

        :param token: str: The JWT token to decode.
        :return: The payload of the decoded token.
        :rtype: dict
        :raises HTTPException: If the token is invalid.
        """
        try:
            payload = jwt.decode(
                token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if payload["scope"] == "refresh_token":
                email = payload["email"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_SCOPE
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=NOT_VALIDATE_CREDENTIALS,
            )

            
    async def get_authenticated_user(
        self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
    ):
        """
        Get the authenticated user.

        This function retrieves the currently authenticated user using the provided token.

        :param token: str: The JWT token representing the user's authentication.
        :param db: AsyncSession: The database session.
        :return: The authenticated user.
        :rtype: User
        :raises HTTPException: If the token is invalid or the user is not found.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=NOT_VALIDATE_CREDENTIALS
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "access_token":
                email = payload["email"]
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
        user = await (await self.redis_cache).get(f"user:{email}")
        if user is None:
            logger.info("--- Using Database ---")
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            await (await self.redis_cache).set(f"user:{email}", pickle.dumps(user))
            await (await self.redis_cache).expire(f"user:{email}", 900)
        else:
            logger.info("--- Using Redis Cache ---")
            user = pickle.loads(user)
        return user

    async def get_email_from_token(self, token: str):
        """
        Get the email address from an email verification token.

        This function decodes an email verification token and retrieves the email address from it.

        :param token: str: The JWT email verification token.
        :return: The email address.
        :rtype: str
        :raises HTTPException: If the token is invalid.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "email_token":
                email = payload["email"]
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
            
auth_service = Auth()