import unittest
from unittest.mock import AsyncMock,MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
import sys
import os
from starlette import status
from starlette.exceptions import HTTPException  

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import Rating,Photo,User
from src.schemas import UserSchema
from src.repository.ratings import create_rating,get_rating,get_all_ratings,delete_all_ratings
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
        fake_user = User(id=1, username="fake_user")
        fake_photo = Photo(id=1, user_id=2)

        mock_query_photo = MagicMock()
        mock_query_photo.scalar.return_value = fake_photo

        mock_query_rating = MagicMock()
        mock_query_rating.scalar_one_or_none.return_value = []

        mock_execute = MagicMock()
        mock_execute.side_effect = [mock_query_photo, mock_query_rating]
        self.session.execute.return_value = mock_execute


        result = await create_rating(5, 1, fake_user, self.session)

        self.assertIsInstance(result, Rating)


        self.session.add.assert_called_once()
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()

        with self.assertRaises(HTTPException) as context:
            await create_rating(5, 1, fake_user, self.session)
        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail, YOUR_PHOTO)


        with self.assertRaises(HTTPException) as context:
            await create_rating(5, 1, fake_user, self.session)
        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail, ALREADY_LIKE)
        

    async def test_get_rating(self):
        fake_ratings = [Rating(rating=4), Rating(rating=5), Rating(rating=3)]

        mock_todos = MagicMock()
        mock_todos.scalars.return_value.all.return_value = fake_ratings
        self.session.execute.return_value = mock_todos

        average_rating = await get_rating(1, self.session)

        self.assertEqual(average_rating, 4.0)

    async def test_get_rating_no_ratings(self):
        fake_ratings = []
        
        mock_todos = MagicMock()
        mock_todos.scalars.return_value.all.return_value = fake_ratings
        self.session.execute.return_value = mock_todos
        average_rating = await get_rating(1, self.session)


        self.assertEqual(average_rating, 0)

    async def test_get_all_ratings(self):
        fake_ratings = [Rating(rating=4), Rating(rating=5), Rating(rating=3)]

        mock_todos = MagicMock()
        mock_todos.scalars.return_value.all.return_value = fake_ratings
        self.session.execute.return_value = mock_todos

        photo_id = 1
        all_ratings = await get_all_ratings(photo_id, self.session)


        self.assertEqual(len(all_ratings), len(fake_ratings))


        for i, rating in enumerate(all_ratings):
            self.assertEqual(rating.rating, fake_ratings[i].rating)
        

    async def test_delete_all_ratings(self):
        photo_id = 1  
        user_id = 2  
        
        fake_rating = Rating(rating=4, photo_id=photo_id, user_id=user_id)



        mock_todos = MagicMock()
        mock_todos.scalars.return_value.all.return_value = fake_rating
        self.session.execute.return_value = mock_todos

        result = await delete_all_ratings(photo_id, user_id, self.session)


        self.assertEqual(result, {"message": "Rating delete"})




if __name__ == "__main__":
    unittest.main()