import pickle
from uvicorn.config import logger


from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends, Request
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
    NOT_VALIDATE_CREDENTIALS,
)

from src.conf.constants import TOKEN_LIFE_TIME, COOKIE_KEY_NAME
from src.conf.config import init_async_redis
from src.database.models import User


class Auth:
    """
    The `Auth` class provides authentication-related functionality for the application.

    It includes methods for password hashing, token creation and decoding, and user verification.

    Attributes:
        pwd_context (CryptContext): An instance of `CryptContext` for password hashing.
        SECRET_KEY (str): The secret key used for token generation and decoding.
        ALGORITHM (str): The algorithm used for token encoding and decoding.
        oauth2_scheme (OAuth2PasswordBearer): An instance of `OAuth2PasswordBearer` for OAuth2 authentication.

    Methods:
        verify_password(plain_password, hashed_password): Verify a plain password against a hashed password.
        get_password_hash(password): Generate a hashed password from a plain text password.
        create_access_token(data, expires_delta=None): Create an access token with an optional expiration time.
        create_refresh_token(data, expires_delta=None): Create a refresh token with an optional expiration time.
        create_email_token(data): Create an email verification token with a fixed expiration time.
        decode_token(token): Decode a JWT token and validate its scope.
        get_authenticated_user(token, db): Get the authenticated user based on the provided token.
        get_email_from_token(token): Get the email address from an email verification token.

    Example Usage:
        auth = Auth()
        hashed_password = auth.get_password_hash("my_password")
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    def __init__(self):
        """
        Initialize a new instance of the `Auth` class.

        This constructor initializes the `Auth` class and sets the `_redis_cache` attribute to `None`.

        :return: None
        """

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
        """
        Verify a plain password against a hashed password.

        :param str plain_password: The plain text password.
        :param str hashed_password: The hashed password to compare against.
        :return: True if the plain password matches the hashed password, False otherwise.
        :rtype: bool
        """

        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Generate a hashed password from a plain text password.

        :param str password: The plain text password.
        :return: The hashed password.
        :rtype: str
        """

        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: int | None = None):
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
        """
        Create an email verification token.

        This function generates an email verification token with an expiration time of 3 days.

        :param data: dict: The data to include in the token payload.
        :return: The encoded email verification token.
        :rtype: str
        """

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
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
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

    async def allow_rout(
        self, request: Request, db: AsyncSession = Depends(get_db)
    ) -> User:
        """
        Authenticate a user for accessing a private route.

        This method is used as a dependency to authenticate a user when accessing a private route.

        :param request: The request object, containing the user's access token in cookies.
        :type request: Request
        :param db: The asynchronous database session (Dependency).
        :type db: AsyncSession
        :return: The authenticated user.
        :rtype: User
        :raises HTTPException 401: Unauthorized if the user is not authenticated or the access token is missing.
        """

        try:
            token = request.cookies.get(COOKIE_KEY_NAME)
            print(token)
            user = await self.get_authenticated_user(token, db)
            return user
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No access token provided",
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

        except JWTError:
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
