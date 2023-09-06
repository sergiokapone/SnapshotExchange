import unittest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
import sys
import os
from starlette import status
from starlette.exceptions import HTTPException  

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import Rating,Photo,User
from src.schemas import UserSchema
from src.repository.ratings import create_rating,get_rating,get_all_ratings,delete_all_ratings


class TestAsyncMethod(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.user= User(
            id=1,
            username= "Corwin",
            email= "tests@gmail.com",
            password= "testpassword1",)
        
    def tearDown(self):
        del self.session

    async def test_create_rathings(self):
        photo = Photo(user_id=self.user.id)
        self.session.execute.return_value.scalar.return_value = photo


        rating = await create_rating(5, 1, self.user, self.session)
        self.assertIsInstance(rating, Rating)
        self.assertEqual(rating.rating, 5)
        self.assertEqual(rating.user_id, self.user.id)
        self.assertEqual(rating.photo_id, 1)


        with self.assertRaises(HTTPException) as context:
            await create_rating(4, 1, self.user, self.session)
        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail, "ALREADY_LIKE")


        with self.assertRaises(HTTPException) as context:
            await create_rating(3, 2, self.user, self.session)
        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail, "YOUR_PHOTO")

    async def test_get_rating(self):

        pass

    async def test_get_all_ratings(self):

        pass

    async def test_delete_all_ratings(self):

        pass


if __name__ == "__main__":
    unittest.main()