import unittest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import User,Role,BlacklistToken
from src.schemas import UserSchema,UserProfileSchema
from src.repository.users import get_user_by_email, edit_my_profile, create_user, update_token,get_users,get_user_profile,get_user_by_reset_token,get_user_by_user_id,get_user_by_username,confirm_email,ban_user,make_user_role,add_to_blacklist,is_blacklisted_token

class TestAsyncMethod(unittest.IsolatedAsyncioTestCase):

    def setUp(self):

        self.session = AsyncMock(spec=AsyncSession)
        self.body_data= UserSchema(
            username= "Corwin",
            email= "tests@gmail.com",
            password= "testpassword1",)
        self.new_user=User(id=3,username="Corwin",
    email="tests@gmail.com",
    created_at=datetime.now(),
    avatar='https://res.cloudinary.com/dqjbmzhfy/image/upload/c_fill,h_250,w_250/v1/Avatars/YEAH_ME',
    is_active=False,
    refresh_token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImNhbXlyYXkxOTkyQGdtYWlsLmNvbSIsImlhdCI6MTY5Mzg1NTIxMCwiZXhwIjoxNjk0NDYwMDEwLCJzY29wZSI6InJlZnJlc2hfdG9rZW4ifQ.YzY8Qp0PBgqx4x2Gc_DY4hZ84xCSXygcP0jDnTWsCaA'
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

        body_data= UserSchema(
            username= "Corwin2",
            email= "tessts@gmail.com",
            password= "testpassword1",)
        
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

        result = await get_user_by_email(self.body_data.email,self.session)

        self.assertEqual(result.username, "Corwin")
        self.assertEqual(result.email, "tests@gmail.com")
        self.assertEqual(result.role, Role.admin)

    # async def test_edit_my_profile(self):
    #     mock_result = MagicMock()
    #     mock_result.scalars.return_value.all.return_value = []
    #     self.session.execute.return_value = mock_result
    #     new_user = await create_user(self.body_data, self.session)

    #     mock_result = MagicMock()
    #     mock_result.scalar_one_or_none.return_value = new_user
    #     self.session.execute.return_value = mock_result
    #     file=MagicMock()
    #     file.filename = "example.jpg"
    #     file.content_type = "image/jpeg"
    #     file.read.return_value = b"fake_image_data"
    #     file_bytes = b"fake_image_data"
    #     new_des='YEess'
    #     new_username='Marlyn'

    #     result = await edit_my_profile(file_bytes,new_des,new_username,new_user,self.session)

    #     self.assertEqual(result.username, new_username)
    #     self.assertEqual(result.description, new_des)


    async def test_get_users(self):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        self.session.execute.return_value = mock_result
        new_user = await create_user(self.body_data, self.session)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [new_user]
        self.session.execute.return_value = mock_result

        result = await get_users(0,10,self.session)

        self.assertIsInstance(result, list)

        self.assertEqual(result[0].username, new_user.username)
        self.assertEqual(result[0].email, new_user.email)

    async def test_get_user_profile(self):

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.new_user
        self.session.execute.return_value = mock_result

        result = await get_user_profile(self.new_user.username,self.session)

        self.assertIsInstance(result, UserProfileSchema)

        self.assertEqual(result.username, self.new_user.username)
        self.assertEqual(result.email, self.new_user.email)

    async def test_get_user_by_reset_token(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.new_user
        self.session.execute.return_value = mock_result

        result = await get_user_by_reset_token(self.new_user.refresh_token,self.session)

        self.assertEqual(result.username, self.new_user.username)
        self.assertEqual(result.email, self.new_user.email)

    async def test_get_user_by_user_id(self):

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.new_user
        self.session.execute.return_value = mock_result

        result = await get_user_by_user_id(3,self.session)

        self.assertEqual(result.username, self.new_user.username)
        self.assertEqual(result.email, self.new_user.email)

    async def test_get_user_by_username(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.new_user
        self.session.execute.return_value = mock_result

        result = await get_user_by_username("Corwin",self.session)

        self.assertEqual(result.username, self.new_user.username)
        self.assertEqual(result.email, self.new_user.email)

    async def test_confirm_email(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.new_user
        self.session.execute.return_value = mock_result

        result = await confirm_email("tests@gmail.com",self.session)

        self.assertTrue(self.new_user.confirmed)


    async def test_ban_user(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.new_user
        self.session.execute.return_value = mock_result

        result = await ban_user("tests@gmail.com",self.session)

        self.assertFalse(self.new_user.is_active)


    async def test_make_user_role(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.new_user
        self.session.execute.return_value = mock_result

        result = await make_user_role("tests@gmail.com",Role.moder,self.session)

        self.assertEqual(self.new_user.role, Role.moder)


    # async def test_add_to_blacklist(self):
    #     token_to_blacklist = "your_test_token"
    #     mock_db_session = MagicMock()

    #     mock_execute = MagicMock()
    #     mock_db_session.execute = mock_execute


    #     mock_result = MagicMock()
    #     mock_execute.return_value = mock_result
    #     mock_result.scalar_one_or_none.return_value = None  


    #     await add_to_blacklist(token_to_blacklist, self.session)


    #     blacklist_query = mock_execute.select(BlacklistToken).filter(BlacklistToken.token == token_to_blacklist)
    #     result = mock_execute.execute(blacklist_query)
    #     blacklisted_token = result.scalar_one_or_none()


    #     self.assertIsNotNone(blacklisted_token)
    #     self.assertEqual(blacklisted_token.token, token_to_blacklist)
    #     self.assertIsInstance(blacklisted_token.blacklisted_on, datetime)


    # async def test_is_blacklisted_token(self):
    #     mock_result = MagicMock()
    #     mock_result.scalar_one_or_none.return_value = self.new_user
    #     self.session.execute.return_value = mock_result
    #     result = await create_user(body,self.session)

    #     self.assertEqual(result.username, body.username)
    #     self.assertEqual(result.email, body.email)


    
   
    async def test_update_token(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.new_user
        self.session.execute.return_value = mock_result
        new_token = "new_refresh_token"

        await update_token(self.new_user, new_token, self.session)

        self.assertEqual(new_token, self.new_user.refresh_token)




    

if __name__ == "__main__":
    unittest.main()