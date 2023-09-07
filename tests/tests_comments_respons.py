import unittest
from unittest.mock import AsyncMock,MagicMock,patch
from sqlalchemy.ext.asyncio import AsyncSession
import sys
import os
from starlette import status
from starlette.exceptions import HTTPException  

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import Rating,Photo,User,Comment,QR_code,Tag,Role
from src.schemas import UserSchema,PhotosDb
from src.repository.comments import create_comment,get_comment,update_comment,delete_comment,get_photo_comments,get_user_comments


class TestAsyncMethod(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession())
        self.user= User(
            id=1,
            username= "Corwin",
            email= "tests@gmail.com",
            password= "testpassword1", confirmed=True)
        
        
        self.session.execute.return_value.scalar.return_value = Photo(user_id=2)
    def tearDown(self):
        del self.session

    async def test_create_comment(self):
        pass

    async def test_get_comment(self):
        pass

    async def test_update_comment(self):
        pass

    async def test_delete_comment(self):
        pass

    async def test_get_photo_comments(self):
        pass

    async def test_get_user_comments(self):
        pass