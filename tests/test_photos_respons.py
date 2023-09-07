import unittest
from unittest.mock import AsyncMock,MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
import sys
import os
from starlette import status
from starlette.exceptions import HTTPException  

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import Rating,Photo,User,Comment,QR_code
from src.schemas import UserSchema,PhotosDb
from src.repository.photos import get_or_create_tag,get_photo_tags,get_photo_comments,upload_photo,get_my_photos,get_photos,get_photo_by_id,update_photo,remove_photo,get_URL_Qr
from src.conf.messages import YOUR_PHOTO, ALREADY_LIKE


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

    async def test_create_rathings(self):

        pass
