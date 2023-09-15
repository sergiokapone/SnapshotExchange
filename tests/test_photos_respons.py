import unittest
from unittest.mock import AsyncMock, MagicMock,patch
from sqlalchemy.ext.asyncio import AsyncSession
import sys
import os
from typing import List, Union
from fastapi import HTTPException, status
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.conf.config import init_cloudinary
from src.services.photos import validate_crop_mode

from src.database.models import Photo, User, QR_code, Tag,Comment,Rating,Role
from src.repository.photos import (
    get_or_create_tag,
    get_photo_tags,
    get_photo_info,
    get_my_photos,
    get_photos,
    get_photo_by_id,
    update_photo,
    get_URL_QR,
    upload_photo,
    remove_photo,
)


class TestAsyncMethod(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession())
        self.user  = User(
            id=1,
            username="Corwin",
            email="tests@gmail.com",
            password="testpassword1",
            confirmed=True,
            role=Role.admin
        )
        self.current_user  = User(
            id=1,
            username="Corwin",
            email="tests@gmail.com",
            password="testpassword1",
            confirmed=True,
        )



        self.photo_file = AsyncMock()
        self.photo_description = "A beautiful landscape"
        self.db_session = AsyncMock(spec=AsyncSession)
        self.width = 800
        self.height = 600
        self.crop_mode = "pad"
        self.rounding = 10
        self.background_color = "white"
        self.rotation_angle = 90
        self.tags = ["nature", "scenic"]

        self.photo = Photo(
            id=1,
            url="photo_url",
            description="A beautiful landscape",
            user=self.user,
            created_at=datetime(2023, 9, 7, 12, 0, 0),
            tags=[Tag(name="nature"), Tag(name="scenic")],
            
        )
        self.photo2 = Photo(
            id=1,
            url="photo_url",
            description="A beautiful landscape",
            user=self.user,
            created_at=datetime(2023, 9, 7, 12, 0, 0),
            tags=[Tag(name="nature"), Tag(name="scenic")],
            user_id=self.user.id,
            cloud_public_id="photo_url"
            
        )

    def tearDown(self):
        del self.session

    
    @patch("src.repository.photos.get_URL_QR")
    @patch("src.repository.ratings.get_rating")
    async def test_get_photo_info(self, mock_get_rating, mock_get_URL_QR):
        mock_query = MagicMock()
        # Підготовка моків та їх поверненням значень
        mock_get_rating.return_value = 4.5
        mock_get_URL_QR.return_value = {"qr_code_url": "qr_url"}
        mock_query.scalar_one.return_value = self.photo
        self.session.execute.return_value = mock_query
        # self.session.execute.return_value.scalar_one.return_value = self.photo


        result = await get_photo_info(self.photo, self.session)

        expected_result = {
            "id": 1,
            "url": "photo_url",
            "QR": "qr_url",
            "description": "A beautiful landscape",
            "username": "Corwin",
            "created_at": "2023-09-07 12:00:00",
            "comments": [],
            "tags": ["nature", "scenic"],
            "rating": 4.5,
        }

        self.assertEqual(result, expected_result)

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

    @patch("src.services.photos.validate_crop_mode", return_value=False)
    async def test_upload_photo_invalid_crop_mode(self, mock_validate_crop_mode):
        # Перевіряємо, як функція веде себе, коли crop_mode неправильний
        # Тут викликана функція validate_crop_mode буде завжди повертати False

        # Викликаємо функцію upload_photo з неправильним crop_mode
        with self.assertRaises(HTTPException) as context:
            await upload_photo(
                self.current_user,
                self.photo_file,
                self.photo_description,
                self.db_session,
                self.width,
                self.height,
                "invalid_crop_mode",  # Неправильний crop_mode
                self.rounding,
                self.background_color,
                self.rotation_angle,
                self.tags,
            )

        # Перевіряємо, що функція спрацювала з помилкою HTTPException
        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)

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

    async def test_get_URL_Qr_None(self):
        mock_query = MagicMock()
        photo = Photo(id=1, url="photo_url")
        qr = QR_code(url="qr_code_url", photo_id=1)
        mock_query.scalar.return_value = None
        mock_query.scalar_one_or_none.return_value = qr
        self.session.execute.side_effect = [mock_query, mock_query]

        photo_id = 10
        with self.assertRaises(HTTPException) as context:
            await get_URL_QR(photo_id, self.session)

        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)


    @patch("src.conf.config.init_cloudinary")
    @patch("cloudinary.uploader.destroy")
    async def test_remove_photo_success(self, mock_destroy, mock_init_cloudinary):
        db_mock = AsyncMock()
        photo_id = self.photo2.id
        user_id = self.user


        mock_query = MagicMock()
        mock_query.scalar_one_or_none.return_value = self.photo2
        db_mock.execute.return_value=mock_query



        result = await remove_photo(photo_id, user_id, db_mock)

        mock_destroy.assert_called_once_with("photo_url")


        db_mock.delete.assert_called_once_with(self.photo2)
        db_mock.commit.assert_called_once()

        self.assertTrue(result)

    async def test_remove_photo_not_found(self):

        db_mock = AsyncMock()
        photo_id = 50
        user_id = self.user


        mock_query = MagicMock()
        mock_query.scalar_one_or_none.return_value = None
        db_mock.execute.return_value=mock_query

        result = await remove_photo(photo_id, user_id, db_mock)


        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
