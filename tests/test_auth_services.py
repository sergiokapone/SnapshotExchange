import unittest
from unittest.mock import AsyncMock,MagicMock,patch
from sqlalchemy.ext.asyncio import AsyncSession
import sys
import os  
from datetime import date
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import HTTPException
from datetime import datetime, timedelta
from src.database.models import Rating,Photo,User,Tag
from src.schemas import UserSchema
from src.services.auth import Auth


class TestAuth(unittest.TestCase):
    
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

    def test_create_access_token(self):
        data = {"sub": "test@example.com"}
        expires_delta = 15
        access_token = self.auth.create_access_token(data, expires_delta)
        self.assertTrue(access_token)

    def test_create_refresh_token(self):
        data = {"sub": "test@example.com"}
        expires_delta = 3600
        refresh_token = self.auth.create_refresh_token(data, expires_delta)
        self.assertTrue(refresh_token)

    def test_create_email_token(self):
        data = {"sub": "test@example.com"}
        email_token = self.auth.create_email_token(data)
        self.assertTrue(email_token)

    async def test_decode_token_valid(self):
        data = {"sub": "test@example.com", "scope": "access_token"}
        token = self.auth.create_access_token(data)
        decoded_token = await self.auth.decode_token(token)
        self.assertEqual(decoded_token["sub"], "test@example.com")

    async def test_decode_token_invalid(self):
        invalid_token = "invalid_token"
        with self.assertRaises(HTTPException):
            await self.auth.decode_token(invalid_token)

    async def test_allow_rout_valid_token(self):
        data = {"sub": "test@example.com", "scope": "access_token"}
        token = self.auth.create_access_token(data)
        request = MagicMock()
        request.cookies.get.return_value = token
        db = AsyncMock()
        user = await self.auth.allow_rout(request, db)
        self.assertTrue(user)

    async def test_allow_rout_invalid_token(self):
        request = MagicMock()
        request.cookies.get.return_value = "invalid_token"
        db = AsyncMock()
        with self.assertRaises(HTTPException):
            await self.auth.allow_rout(request, db)

    async def test_get_authenticated_user_from_cache(self):
        data = {"sub": "test@example.com"}
        token = self.auth.create_access_token(data)
        request = MagicMock()
        request.cookies.get.return_value = token
        db = AsyncMock()
        with patch.object(self.auth, "_redis_cache") as redis_cache_mock:
            user = await self.auth.get_authenticated_user(token, db)
            self.assertTrue(user)
            self.assertTrue(redis_cache_mock.get.called)
            self.assertFalse(db.get_user_by_email.called)

    async def test_get_authenticated_user_from_db(self):
        data = {"sub": "test@example.com"}
        token = self.auth.create_access_token(data)
        request = MagicMock()
        request.cookies.get.return_value = token
        db = AsyncMock()
        db.get_user_by_email.return_value = {"sub": "test@example.com"}
        with patch.object(self.auth, "_redis_cache") as redis_cache_mock:
            user = await self.auth.get_authenticated_user(token, db)
            self.assertTrue(user)
            self.assertTrue(redis_cache_mock.get.called)
            self.assertTrue(db.get_user_by_email.called)

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

    async def test_get_email_from_token_valid(self):
        data = {"sub": "test@example.com", "scope": "email_token"}
        token = self.auth.create_email_token(data)
        email = await self.auth.get_email_from_token(token)
        self.assertEqual(email, "test@example.com")

if __name__ == "__main__":
    unittest.main()