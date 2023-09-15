import unittest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
import sys
import os
from fastapi import HTTPException

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import Rating,User,Photo
from src.repository.ratings import get_rating, get_all_ratings, delete_all_ratings,create_rating,NO_PHOTO_BY_ID, YOUR_PHOTO, ALREADY_LIKE


class TestAsyncMethod(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession())

    def tearDown(self):
        del self.session

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

    async def test_create_rating_valid(self):
        rating_value = 4  # По вашому вибору
        photo_id = 1  # ID фотографії, яку ви тестуєте

        db_mock = AsyncMock()
        user_mock = User(id=1)  # По вашому вибору
        photo_mock = Photo(id=photo_id, user_id=2)  # По вашому вибору

        mock_photo_1=MagicMock()
        mock_photo_1.scalar_one_or_none.return_value=photo_mock
        mock_photo_2=MagicMock()
        mock_photo_2.scalar_one_or_none.return_value=None

        db_mock.execute.side_effect = [mock_photo_1,
                                       mock_photo_2]

        created_rating = await create_rating(rating_value, photo_id, user_mock, db_mock)

        # Перевірка, чи функція повертає правильний рейтинг
        self.assertEqual(created_rating.rating, rating_value)
        self.assertEqual(created_rating.user_id, user_mock.id)
        self.assertEqual(created_rating.photo_id, photo_id)

    async def test_create_rating_invalid_value(self):
        # Підготовка даних для створення рейтингу з недійсним значенням
        invalid_rating_value = 6  # Недійсне значення рейтингу

        db_mock = AsyncMock()
        user_mock = User(id=1)  # По вашому вибору
        photo_id = 1  # ID фотографії, яку ви тестуєте

        # Виклик функції create_rating з недійсним значенням рейтингу
        with self.assertRaises(HTTPException) as context:
            await create_rating(invalid_rating_value, photo_id, user_mock, db_mock)

        # Перевірка, чи функція генерує правильний HTTPException з кодом статусу 400
        self.assertEqual(context.exception.status_code, 400)

    async def test_create_rating_no_photo(self):
        non_existent_photo_id = 123456789  

        db_mock = AsyncMock()
        user_mock = User(id=1)  

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None

        db_mock.execute.return_value = result_mock

        with self.assertRaises(HTTPException) as context:
            await create_rating(4, non_existent_photo_id, user_mock, db_mock)

        self.assertEqual(context.exception.status_code, 404)

if __name__ == "__main__":
    unittest.main()
