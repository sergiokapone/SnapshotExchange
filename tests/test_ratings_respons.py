import unittest
from unittest.mock import AsyncMock,MagicMock,patch
from sqlalchemy.ext.asyncio import AsyncSession
import sys
import os
from fastapi import  status,HTTPException


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import Rating,Photo,User
from src.schemas import UserSchema
from src.repository.ratings import create_rating,get_rating,get_all_ratings,delete_all_ratings
from src.conf.messages import YOUR_PHOTO, ALREADY_LIKE




class TestAsyncMethod(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession())

        
    def tearDown(self):
        del self.session

    
    # @patch('sqlalchemy.select')
    # @patch('fastapi.HTTPException')
    # async def test_create_rating(self, mock_http_exception, mock_select):
    #     # Створюємо мок об'єкт бази даних та результат запиту
    #     mock_select = MagicMock()
    #     mock_select.return_value.scalar.return_value = None
    #     mock_db = AsyncMock()
    #     mock_select.return_value.scalar.return_value = None

    #     # Параметри для тесту
    #     rating = 5
    #     photo_id = 1
    #     user = User(id=2, username="test_user")
        
    #     # Мокуємо функції db.execute та db.commit
    #     mock_db.execute.return_value = AsyncMock()
    #     mock_db.commit.return_value = None

    #     # Викликаємо функцію
    #     result = await create_rating(rating, photo_id, user, mock_db)

    #     # Перевірка, що функція взаємодіє з базою даних правильно
    #     mock_select.assert_called_once_with(Photo)
    #     mock_select.return_value.scalar.assert_called_once()
    #     mock_db.execute.assert_called_once()
    #     mock_db.commit.assert_called_once()
    #     mock_db.refresh.assert_called_once()

    #     # Перевірка, що результат є очікуваним об'єктом Rating
    #     self.assertIsInstance(result, Rating)
    #     self.assertEqual(result.rating, rating)
    #     self.assertEqual(result.user_id, user.id)
    #     self.assertEqual(result.photo_id, photo_id)

    # @patch('sqlalchemy.select')
    # @patch('fastapi.HTTPException')
    # async def test_create_rating_already_exists(self, mock_http_exception, mock_select):
    #     # Створюємо мок об'єкт бази даних та результат запиту, де вже існує рейтинг
    #     mock_db = AsyncMock()
    #     mock_select.return_value.scalar.return_value = Rating(rating=4, user_id=2, photo_id=1)

    #     # Параметри для тесту
    #     rating = 5
    #     photo_id = 1
    #     user = User(id=2, username="test_user")

    #     # Викликаємо функцію та очікуємо HTTPException з відповідним повідомленням
    #     with self.assertRaises(HTTPException) as context:
    #         await create_rating(rating, photo_id, user, mock_db)
    #     self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(context.exception.detail, ALREADY_LIKE)

    # @patch('sqlalchemy.select')
    # @patch('fastapi.HTTPException')
    # async def test_create_rating_own_photo(self, mock_http_exception, mock_select):
    #     # Створюємо мок об'єкт бази даних та результат запиту, де користувач є власником фото
    #     mock_db = AsyncMock()
    #     mock_select.return_value.scalar.return_value = Photo(id=1, user_id=2)

    #     # Параметри для тесту
    #     rating = 5
    #     photo_id = 1
    #     user = User(id=2, username="test_user")

    #     # Викликаємо функцію та очікуємо HTTPException з відповідним повідомленням
    #     with self.assertRaises(HTTPException) as context:
    #         await create_rating(rating, photo_id, user, mock_db)
    #     self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(context.exception.detail, YOUR_PHOTO)


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