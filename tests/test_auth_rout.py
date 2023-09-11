import unittest
from unittest.mock import AsyncMock,MagicMock,patch
from sqlalchemy.ext.asyncio import AsyncSession
import sys
import uvicorn
import os
import httpx
from fastapi import FastAPI,BackgroundTasks,Request,Depends
from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import Rating,Photo,User,Comment,QR_code,Tag,Role
from src.schemas import UserSchema,PhotosDb
from src.routes.auth import  signup, login, logout,refresh_token,confirmed_email,request_email,forgot_password,reset_password
from main import app
from src.repository import users

class TestAsyncMethod(unittest.IsolatedAsyncioTestCase):

    def asyncSetUp(self):
        self.client = TestClient(app)
        self.session = AsyncMock(spec=AsyncSession())

    def asyncTearDown(self):
        pass


    # async def test_signup_success(self):
    #     user_data = UserSchema(
    #     email="test@example.com",
    #     username="testuser",
    #     password="password123",
    # )
    #     scope = {"type": "http"}

    #     # Створіть об'єкт `Request` з цим контекстом
    #     request = Request(scope)

    #     background_tasks = BackgroundTasks()

    #     mock_result = MagicMock()
    #     mock_result.scalars.return_value.all.return_value = []
    #     self.session.execute.return_value = mock_result

    #     # Створюємо імітацію для методу create_user
    #     mock_create_user = AsyncMock()
    #     mock_create_user.return_value = {"user": {"email": "test@example.com", "username": "testuser"}}
    #     users.create_user = mock_create_user

    #     # Залишаємо решту коду незмінним

    #     response = await signup(user_data, background_tasks, request, db=self.session)

    #     assert "user" in response
    #     assert "email" in response["user"]
    #     assert "username" in response["user"]
    #     assert "detail" in response
    #     assert response["detail"] == "User successfully created. Check your email for confirmation"
        
    # @patch("src.routes.auth.get_db", create_test_session)
    # async def test_signup_duplicate_email(self):

    #     client = TestClient(app)

    #     existing_user_data = {
    #         "email": "existing@example.com",
    #         "username": "existinguser",
    #         "password": "password123",
    #     }
    #     await client.post("/signup", json=existing_user_data)

    #     duplicate_user_data = {
    #         "email": "existing@example.com",
    #         "username": "newuser",
    #         "password": "newpassword123",
    #     }
        

    #     response = await client.post("/signup", json=duplicate_user_data)
        

    #     self.assertEqual(response.status_code, 409)

    #     response_data = response.json()
    #     self.assertIn("detail", response_data)
    #     self.assertEqual(response_data["detail"], "ALREADY_EXISTS_EMAIL")


if __name__ == "__main__":
    unittest.main()