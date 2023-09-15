import unittest
from unittest.mock import AsyncMock, MagicMock,patch
from sqlalchemy.ext.asyncio import AsyncSession
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import User, Role,BlacklistToken
from src.schemas import UserSchema, UserProfileSchema
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    get_users,
    get_user_profile,
    get_user_by_reset_token,
    get_user_by_user_id,
    get_user_by_username,
    confirm_email,
    ban_user,
    make_user_role,
    add_to_blacklist,
    edit_my_profile,
    is_blacklisted_token
)


class TestAsyncMethod(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.body_data = UserSchema(
            username="Corwin",
            email="tests@gmail.com",
            password="testpassword1",
        )
        self.new_user = User(
            id=3,
            username="Corwin",
            role=Role.user,
            email="tests@gmail.com",
            created_at=datetime.now(),
            avatar="https://res.cloudinary.com/dqjbmzhfy/image/upload/c_fill,h_250,w_250/v1/Avatars/YEAH_ME",
            is_active=False,
            refresh_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImNhbXlyYXkxOTkyQGdtYWlsLmNvbSIsImlhdCI6MTY5Mzg1NTIxMCwiZXhwIjoxNjk0NDYwMDEwLCJzY29wZSI6InJlZnJlc2hfdG9rZW4ifQ.YzY8Qp0PBgqx4x2Gc_DY4hZ84xCSXygcP0jDnTWsCaA",
        )

    def tearDown(self):
        del self.session

    async def test_create_user(self):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        self.session.execute.return_value = mock_result

        new_user = await create_user(self.body_data, self.session)

        self.assertIsInstance(new_user, User)

        self.assertEqual(new_user.username, "Corwin")
        self.assertEqual(new_user.email, "tests@gmail.com")
        self.assertEqual(new_user.role, Role.admin)

        body_data = UserSchema(
            username="Corwin2",
            email="tessts@gmail.com",
            password="testpassword1",
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [new_user]
        self.session.execute.return_value = mock_result

        second_user = await create_user(body_data, self.session)

        self.assertIsInstance(second_user, User)

        self.assertEqual(second_user.username, "Corwin2")
        self.assertEqual(second_user.email, "tessts@gmail.com")
        self.assertEqual(second_user.role, Role.user)

    async def test_get_user_by_email(self):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        self.session.execute.return_value = mock_result

        new_user = await create_user(self.body_data, self.session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = new_user
        self.session.execute.return_value = mock_result

        result = await get_user_by_email(self.body_data.email, self.session)

        self.assertEqual(result.username, "Corwin")
        self.assertEqual(result.email, "tests@gmail.com")
        self.assertEqual(result.role, Role.admin)

    @patch("src.conf.config.init_cloudinary")
    @patch("cloudinary.uploader.upload")
    async def test_edit_my_profile(self,mock_upload, mock_init_cloudinary):
        mock_db = AsyncMock(spec=AsyncSession())
        mock_file = MagicMock()
        new_description = "New description"
        new_username = "new_username"
        user_id = 1
        mock_user_1=MagicMock()
        mock_user = User(
            id=user_id,
            username="old_username",
            description="Old description",
            avatar="old_avatar_url",
        )
        mock_user_1.scalar_one_or_none.return_value= mock_user
        mock_db.execute.return_value = mock_user_1

        init_cloudinary = MagicMock()

        cloudinary_upload = MagicMock()
        cloudinary_url = "https://res.cloudinary.com/name/image/upload/c_fill,h_250,w_250/v1/Avatars/new_username"
        cloudinary_upload.return_value = {"url": cloudinary_url}

        result = await edit_my_profile(
            mock_file, new_description, new_username, mock_user, mock_db
        )

        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_user)

        self.assertEqual(result.id, user_id)
        self.assertEqual(result.username, new_username)
        self.assertEqual(result.description, new_description)
        self.assertEqual(result.avatar, cloudinary_url)

    async def test_get_users(self):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        self.session.execute.return_value = mock_result
        new_user = await create_user(self.body_data, self.session)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [new_user]
        self.session.execute.return_value = mock_result

        result = await get_users(0, 10, self.session)

        self.assertIsInstance(result, list)

        self.assertEqual(result[0].username, new_user.username)
        self.assertEqual(result[0].email, new_user.email)

    async def test_get_user_profile(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.new_user
        self.session.execute.return_value = mock_result

        result = await get_user_profile(self.new_user.username, self.session)

        self.assertIsInstance(result, UserProfileSchema)

        self.assertEqual(result.username, self.new_user.username)
        self.assertEqual(result.email, self.new_user.email)
        self.assertEqual(result.photos_count, 1)
        self.assertEqual(result.comments_count, 1)

    async def test_get_user_by_reset_token(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.new_user
        self.session.execute.return_value = mock_result

        result = await get_user_by_reset_token(
            self.new_user.refresh_token, self.session
        )

        self.assertEqual(result.username, self.new_user.username)
        self.assertEqual(result.email, self.new_user.email)

    async def test_get_user_by_user_id(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.new_user
        self.session.execute.return_value = mock_result

        result = await get_user_by_user_id(3, self.session)

        self.assertEqual(result.username, self.new_user.username)
        self.assertEqual(result.email, self.new_user.email)

    async def test_get_user_by_username(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.new_user
        self.session.execute.return_value = mock_result

        result = await get_user_by_username("Corwin", self.session)

        self.assertEqual(result.username, self.new_user.username)
        self.assertEqual(result.email, self.new_user.email)

    async def test_confirm_email(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.new_user
        self.session.execute.return_value = mock_result

        await confirm_email("tests@gmail.com", self.session)

        self.assertTrue(self.new_user.confirmed)

    async def test_ban_user(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.new_user
        self.session.execute.return_value = mock_result

        await ban_user("tests@gmail.com", self.session)

        self.assertFalse(self.new_user.is_active)

    async def test_make_user_role(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.new_user
        self.session.execute.return_value = mock_result

        await make_user_role("tests@gmail.com", Role.moder, self.session)

        self.assertEqual(self.new_user.role, Role.moder)

    async def test_add_to_blacklist(self):
        mock_db = MagicMock(spec=AsyncSession())
        token = "sample_token"

        await add_to_blacklist(token, mock_db)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    async def test_is_blacklisted_token(self):


        token = 'token'  # Токен для перевірки на чорний список
        blacklisted_token = BlacklistToken(token=token, blacklisted_on=datetime.now())

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = blacklisted_token
        self.session.execute.return_value = mock_result

        result = await is_blacklisted_token(token, self.session)
        self.assertTrue(result)  

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mock_result
        non_blacklisted_token = "non_blacklisted_token"
        result = await is_blacklisted_token(non_blacklisted_token, self.session)
        self.assertFalse(result)

    async def test_update_token(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.new_user
        self.session.execute.return_value = mock_result
        new_token = "new_refresh_token"

        await update_token(self.new_user, new_token, self.session)

        self.assertEqual(new_token, self.new_user.refresh_token)


if __name__ == "__main__":
    unittest.main()
