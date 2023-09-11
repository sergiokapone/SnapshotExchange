import unittest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import Photo, User, QR_code, Tag
from src.repository.photos import (
    get_or_create_tag,
    get_photo_tags,
    get_my_photos,
    get_photos,
    get_photo_by_id,
    update_photo,
    get_URL_QR,
)


class TestAsyncMethod(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession())
        self.user = User(
            id=1,
            username="Corwin",
            email="tests@gmail.com",
            password="testpassword1",
            confirmed=True,
        )

        self.session.execute.return_value.scalar.return_value = Photo(user_id=2)

    def tearDown(self):
        del self.session

    async def test_get_or_create_tag(self):
        mock_query = MagicMock()
        mock_query.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mock_query

        result_tag = await get_or_create_tag("example_tag", self.session)

        self.assertIsInstance(result_tag, Tag)
        self.assertEqual(result_tag.name, "example_tag")

        self.session.add.assert_called_once_with(result_tag)
        self.session.commit.assert_called_once()

        existing_tag = Tag(name="example_tag")
        mock_query.scalar_one_or_none.return_value = existing_tag

        result_tag = await get_or_create_tag("example_tag", self.session)

        self.assertIsInstance(result_tag, Tag)
        self.assertEqual(result_tag.name, "example_tag")

    async def test_get_photo_tags(self):
        mock_query = MagicMock()
        mock_query.scalars().all.return_value = ["tag1", "tag2"]
        self.session.execute.return_value = mock_query

        photo_id = 1

        res = await get_photo_tags(photo_id, self.session)

        self.assertEqual(res, ["tag1", "tag2"])

        mock_query = MagicMock()
        mock_query.scalars().all.return_value = []
        self.session.execute.return_value = mock_query

        photo_id = 1

        res = await get_photo_tags(photo_id, self.session)

        self.assertEqual(res, None)

    async def test_get_my_photos(self):
        mock_query = MagicMock()

        mock_query.scalars().all.return_value = [
            Photo(id=1, user_id=1),
            Photo(id=2, user_id=1),
            Photo(id=3, user_id=1),
        ]
        self.session.execute.return_value = mock_query

        skip = 0
        limit = 10
        current_user = User(id=1, username="user1")
        db = self.session

        result = await get_my_photos(skip, limit, current_user, db)

        expected_result = [
            {"id": 1, "user_id": 1},
            {"id": 2, "user_id": 1},
            {"id": 3, "user_id": 1},
        ]

        result_attrs = [{"id": photo.id, "user_id": photo.user_id} for photo in result]

        self.assertEqual(result_attrs, expected_result)

    async def test_get_photos(self):
        mock_query = MagicMock()
        mock_query.scalars().all.return_value = [Photo(id=1), Photo(id=2), Photo(id=3)]
        self.session.execute.return_value = mock_query

        skip = 0
        limit = 3
        result = await get_photos(skip, limit, self.session)

        expected_result = [Photo(id=1), Photo(id=2), Photo(id=3)]
        self.assertCountEqual(
            [photo.id for photo in result], [photo.id for photo in expected_result]
        )

    async def test_get_photos_empty(self):
        mock_query = MagicMock()
        mock_query.scalars().all.return_value = []
        self.session.execute.return_value = mock_query

        skip = 0
        limit = 3
        result = await get_photos(skip, limit, self.session)

        self.assertEqual(result, [])

    async def test_get_photo_by_id(self):
        mock_query = MagicMock()
        mock_query.scalar_one_or_none.return_value = {
            "id": 1,
            "url": "photo_url",
            "user_id": 1,
        }
        self.session.execute.return_value = mock_query

        photo_id = 1

        result = await get_photo_by_id(photo_id, self.session)

        expected_result = {"id": 1, "url": "photo_url", "user_id": 1}
        self.assertEqual(result, expected_result)

        mock_query.scalar_one_or_none.return_value = None
        result = await get_photo_by_id(photo_id, self.session)
        self.assertIsNone(result)

    async def test_update_photo(self):
        mock_query = MagicMock()
        photo = Photo(id=1, url="photo_url", user_id=1, description="old_description")
        mock_query.scalar.return_value = photo
        self.session.execute.return_value = mock_query

        current_user = User(id=1, username="user1")
        photo_id = 1
        new_description = "new_description"

        result = await update_photo(
            current_user, photo_id, new_description, self.session
        )

        expected_result = Photo(
            id=1, url="photo_url", user_id=1, description="new_description"
        )
        self.assertEqual(result.id, expected_result.id)
        self.assertEqual(result.url, expected_result.url)
        self.assertEqual(result.user_id, expected_result.user_id)
        self.assertEqual(result.description, expected_result.description)

    async def test_get_URL_Qr(self):
        mock_query = MagicMock()
        photo = Photo(id=1, url="photo_url")
        qr = QR_code(url="qr_code_url", photo_id=1)
        mock_query.scalar.return_value = photo
        mock_query.scalar_one_or_none.return_value = qr
        self.session.execute.side_effect = [mock_query, mock_query]

        photo_id = 1
        result = await get_URL_QR(photo_id, self.session)

        expected_result = {"source_url": photo.url, "qr_code_url": qr.url}
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
