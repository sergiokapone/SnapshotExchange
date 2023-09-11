import unittest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
import sys
import os
from datetime import date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.repository.search import search_by_tag, search_by_description


class TestAsyncMethod(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession())

    def tearDown(self):
        del self.session

    async def test_search_by_tag(self):
        db = AsyncMock()
        query = MagicMock()
        query.filter.return_value = query
        query.scalar.return_value = ["nature"]
        db.execute.return_value = query

        tag = "nature"
        rating_low = 3.0
        rating_high = 5.0
        start_date = date(2023, 1, 1)
        end_date = date(2023, 12, 31)

        result = await search_by_tag(
            tag, rating_low, rating_high, start_date, end_date, db
        )

        self.assertEqual(len(result), 0)

    async def test_search_by_description(self):
        db = AsyncMock()
        query = MagicMock()
        query.filter.return_value = query
        query.scalar.return_value = ["description"]
        db.execute.return_value = query

        text = "description"
        rating_low = 3.0
        rating_high = 5.0
        start_date = date(2023, 1, 1)
        end_date = date(2023, 12, 31)

        result = await search_by_description(
            text, rating_low, rating_high, start_date, end_date, db
        )

        self.assertEqual(len(result), 0)

    # async def test_search_by_username(self):

    #     fake_user = User(username="testuser", photos=[Photo(id=1), Photo(id=2)])
    #     fake_result = MagicMock()
    #     fake_result.scalar = AsyncMock(return_value=fake_user)
    #     self.session.execute = AsyncMock(return_value=fake_result)

    #     # Викликаємо функцію search_by_username з мокованими параметрами
    #     username = "testuser"

    #     # Очікуємо, що функція search_by_username поверне об'єкт user з фейковим списком фото
    #     result = await search_by_username(username, self.session)

    #     # Перевірка результату
    #     self.assertEqual(result, fake_user)

    # async def test_search_photos_admin(self):
    #     tag_name = "nature"
    #     user_id = 1
    #     rating_low = 3.0
    #     rating_high = 5.0
    #     start_date = date(2023, 1, 1)
    #     end_date = date(2023, 12, 31)

    #     tag = Tag(name=tag_name)
    #     photo1 = Photo(description="Nature photo 1", ratings=Rating(rating=4.0), user_id=user_id, created_at=start_date)
    #     photo2 = Photo(description="Nature photo 2", ratings=Rating(rating=5.0), user_id=user_id, created_at=start_date)
    #     photo3 = Photo(description="Nature photo 3", ratings=Rating(rating=2.0), user_id=user_id, created_at=start_date)

    #     photo1.tags.append(tag)
    #     photo2.tags.append(tag)
    #     photo3.tags.append(tag)

    #     fake_results = [photo1, photo2, photo3]

    #     mock_user_query = MagicMock()
    #     self.session.scalar.return_value = None
    #     self.session.execute.return_value = mock_user_query

    #     mock_photos_query = MagicMock()
    #     self.session.scalars.return_value.all.return_value = fake_results
    #     self.session.execute.return_value =  mock_photos_query

    #     result = await search_admin(user_id, tag_name, rating_low, rating_high, start_date, end_date, self.session)

    #     # Перевірка атрибутів об'єктів, а не порівняння об'єктів напряму
    #     self.assertEqual(result[0].description, "Nature photo 1")
    #     self.assertEqual(result[0].ratings.rating, 4.0)
    #     self.assertEqual(result[1].description, "Nature photo 2")
    #     self.assertEqual(result[1].ratings.rating, 5.0)
    #     self.assertEqual(result[2].description, "Nature photo 3")
    #     self.assertEqual(result[2].ratings.rating, 2.0)


if __name__ == "__main__":
    unittest.main()
