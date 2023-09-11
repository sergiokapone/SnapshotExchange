import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os
from fastapi import HTTPException, status

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import HTTPException
from src.database.models import User
from src.services.auth import Auth


class TestAuth(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.auth = Auth()

    def tearDown(self):
        self.auth._redis_cache = None

    def test_verify_password(self):
        hashed_password = self.auth.get_password_hash("my_password")
        result = self.auth.verify_password("my_password", hashed_password)
        self.assertTrue(result)

    def test_get_password_hash(self):
        hashed_password = self.auth.get_password_hash("my_password")
        self.assertTrue(hashed_password)

    async def test_create_access_token(self):
        data = {"sub": "test@example.com"}
        expires_delta = 15
        access_token = await self.auth.create_access_token(data, expires_delta)
        self.assertTrue(access_token)

    async def test_create_refresh_token(self):
        data = {"sub": "test@example.com"}
        expires_delta = 3600
        refresh_token = await self.auth.create_refresh_token(data, expires_delta)
        self.assertTrue(refresh_token)

    def test_create_email_token(self):
        data = {"sub": "test@example.com"}
        email_token = self.auth.create_email_token(data)
        self.assertTrue(email_token)

    @patch("src.services.auth.jwt.decode")
    async def test_decode_token_valid(self, mock_decode):
        token = "valid_token"
        mock_decode.return_value = {
            "scope": "refresh_token",
            "email": "test@example.com",
        }

        decoded_email = await self.auth.decode_token(token)

        mock_decode.assert_called_once_with(
            token, self.auth.SECRET_KEY, algorithms=[self.auth.ALGORITHM]
        )

        self.assertEqual(decoded_email, "test@example.com")

    async def test_decode_token_invalid(self):
        invalid_token = "invalid_token"
        with self.assertRaises(HTTPException):
            await self.auth.decode_token(invalid_token)

    async def test_allow_rout_authenticated(self):
        request = MagicMock()
        db = AsyncMock()
        access_token = "valid_access_token"

        user = User(id=1, username="test_user")
        self.auth.get_authenticated_user = AsyncMock(return_value=user)

        request.cookies.get.return_value = access_token

        result = await self.auth.allow_rout(request, db)

        self.auth.get_authenticated_user.assert_called_once_with(access_token, db)

        self.assertIsInstance(result, User)
        self.assertEqual(result.id, user.id)
        self.assertEqual(result.username, user.username)

    async def test_allow_rout_unauthenticated(self):
        request = MagicMock()
        db = AsyncMock()

        request.cookies.get.return_value = None

        self.auth.get_authenticated_user = AsyncMock(
            side_effect=HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No access token provided",
            )
        )

        with self.assertRaises(HTTPException) as context:
            await self.auth.allow_rout(request, db)

        self.auth.get_authenticated_user.assert_called_once_with(None, db)

        self.assertEqual(context.exception.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(context.exception.detail, "No access token provided")

    async def test_get_authenticated_user_invalid_token(self):
        invalid_token = "invalid_token"
        request = MagicMock()
        request.cookies.get.return_value = invalid_token
        db = AsyncMock()
        with self.assertRaises(HTTPException):
            await self.auth.get_authenticated_user(invalid_token, db)

    async def test_get_email_from_token_invalid(self):
        invalid_token = "invalid_token"
        with self.assertRaises(HTTPException):
            await self.auth.get_email_from_token(invalid_token)

    async def test_get_email_from_valid_token(self):
        data = {
            "sub": "test@example.com",
            "scope": "email_token",
            "email": "test@example.com",
        }
        token = self.auth.create_email_token(data)

        email = await self.auth.get_email_from_token(token)
        self.assertEqual(email, "test@example.com")


if __name__ == "__main__":
    unittest.main()
