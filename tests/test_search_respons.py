import unittest
from unittest.mock import AsyncMock,MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
import sys
import os  
from datetime import date
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import Rating,Photo,User,Tag
from src.schemas import UserSchema
from src.repository.search import search,search_admin


class TestAsyncMethod(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession())
        
    def tearDown(self):
        del self.session


    
    
    async def test_search_photos_by_tag_and_rating(self):
        # Підготовка моків
        tag_name = "nature"
        rating_low = 3.0
        rating_high = 5.0
        start_date = date(2023, 1, 1)
        end_date = date(2023, 12, 31)

        rating1 = Rating(rating=4.0)
        rating2 = Rating(rating=5.0)
        rating3 = Rating(rating=2.0)

        tag = Tag(name=tag_name)
        photo1 = Photo(description="Nature photo 1",ratings=rating1)
        photo2 = Photo(description="Nature photo 2",ratings=rating2)
        photo3 = Photo(description="Nature photo 3",ratings=rating3)

        photo1.tags.append(tag)
        photo2.tags.append(tag)
        photo3.tags.append(tag)

        fake_results = [photo1, photo2,photo3]
        mock_tag_query = MagicMock()
        mock_tag_query.scalar.return_value = tag
        self.session.execute.return_value = mock_tag_query

        mock_photos_query = MagicMock()
        mock_photos_query.scalars.return_value.all.return_value = [photo1, photo2, photo3]
        self.session.execute.side_effect = [mock_tag_query, mock_photos_query]

        result = await search(tag_name, rating_low, rating_high, start_date, end_date, self.session)

        self.assertEqual(result, fake_results)

    async def test_search_photos_admin(self):
        tag_name = "nature"
        user_id = 1
        rating_low = 3.0
        rating_high = 5.0
        start_date = date(2023, 1, 1)
        end_date = date(2023, 12, 31)
        
        tag = Tag(name=tag_name)
        photo1 = Photo(description="Nature photo 1", ratings=Rating(rating=4.0), user_id=user_id, created_at=start_date)
        photo2 = Photo(description="Nature photo 2", ratings=Rating(rating=5.0), user_id=user_id, created_at=start_date)
        photo3 = Photo(description="Nature photo 3", ratings=Rating(rating=2.0), user_id=user_id, created_at=start_date)

        photo1.tags.append(tag)
        photo2.tags.append(tag)
        photo3.tags.append(tag)

        fake_results = [photo1, photo2,photo3]

        mock_tag_query = MagicMock()
        mock_tag_query.scalar.return_value = tag
        self.session.execute.return_value = mock_tag_query

        mock_photos_query = MagicMock()
        mock_photos_query.scalars.return_value.all.return_value = [photo1, photo2, photo3]
        self.session.execute.side_effect = [mock_tag_query, mock_photos_query]

        result = await search_admin(tag_name, user_id, rating_low, rating_high, start_date, end_date, self.session)

        self.assertEqual(result, fake_results)

if __name__ == "__main__":
    unittest.main()