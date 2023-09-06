import unittest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import User,Role
from src.schemas import UserSchema
from src.repository.users import get_user_by_email, edit_my_profile, create_user, update_token,get_users,get_user_profile,get_user_by_reset_token,get_user_by_user_id,get_user_by_username,confirm_email,ban_user,make_user_role,add_to_blacklist,is_blacklisted_token

class TestAsyncMethod(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.body_data= UserSchema(
            username= "Corwin",
            email= "tests@gmail.com",
            password= "testpassword1",)
        
    def tearDown(self):
        del self.session

    async def test_create_user(self):

        new_user = await create_user(self.body_data, self.session)

        self.assertIsInstance(new_user, User)

        self.assertEqual(new_user.username, "Corwin")
        self.assertEqual(new_user.email, "tests@gmail.com")
        self.assertEqual(new_user.role, Role.user)

        body_data= UserSchema(
            username= "Corwin2",
            email= "tessts@gmail.com",
            password= "testpassword1",)
        second_user = await create_user(body_data, self.session)

        self.assertIsInstance(second_user, User)
        
        self.assertEqual(second_user.username, "Corwin2")
        self.assertEqual(second_user.email, "tessts@gmail.com")

    async def test_get_user_by_email(self):

        new_user = await create_user(self.body_data, self.session)

        self.session.execute.return_value.scalar_one_or_none.return_value = new_user

        result = await get_user_by_email(self.body_data.email,self.session)

        self.assertEqual(result.username, "Corwin")
        self.assertEqual(result.email, "tests@gmail.com")
        self.assertEqual(result.role, Role.user)

    async def test_edit_my_profile(self):
        new_user = await create_user(self.body_data, self.session)

        self.session.execute.return_value.scalar_one_or_none.return_value = new_user
        file='Bel_god.jpg'

        with open(file, 'rb') as f:
            file = MagicMock(file=f)
        new_des='YEess'
        new_username='Marlyn'

        result = await edit_my_profile(file,new_des,new_username,new_user,self.session)

        self.assertEqual(result.username, new_username)
        self.assertEqual(result.description, new_des)


    # async def test_get_users(self):
    #     body=UserSchema(username='Cor5win',email='test@example.com', password='qwer5ty')
    #     result = await create_user(body,self.session)

    #     self.assertEqual(result.username, body.username)
    #     self.assertEqual(result.email, body.email)

    #     self.assertTrue(hasattr(result, "id"))

    # async def test_get_user_profile(self):
    #     body=UserSchema(username='Cor5win',email='test@example.com', password='qwer5ty')
    #     result = await create_user(body,self.session)

    #     self.assertEqual(result.username, body.username)
    #     self.assertEqual(result.email, body.email)

    #     self.assertTrue(hasattr(result, "id"))

    # async def test_get_user_by_reset_token(self):
    #     body=UserSchema(username='Cor5win',email='test@example.com', password='qwer5ty')
    #     result = await create_user(body,self.session)

    #     self.assertEqual(result.username, body.username)
    #     self.assertEqual(result.email, body.email)

    #     self.assertTrue(hasattr(result, "id"))

    # async def test_get_user_by_user_id(self):
    #     body=UserSchema(username='Cor5win',email='test@example.com', password='qwer5ty')
    #     result = await create_user(body,self.session)

    #     self.assertEqual(result.username, body.username)
    #     self.assertEqual(result.email, body.email)

    #     self.assertTrue(hasattr(result, "id"))

    # async def test_get_user_by_username(self):
    #     body=UserSchema(username='Cor5win',email='test@example.com', password='qwer5ty')
    #     result = await create_user(body,self.session)

    #     self.assertEqual(result.username, body.username)
    #     self.assertEqual(result.email, body.email)

    #     self.assertTrue(hasattr(result, "id"))

    # async def test_confirm_email(self):
    #     body=UserSchema(username='Cor5win',email='test@example.com', password='qwer5ty')
    #     result = await create_user(body,self.session)

    #     self.assertEqual(result.username, body.username)
    #     self.assertEqual(result.email, body.email)

    #     self.assertTrue(hasattr(result, "id"))


    # async def test_ban_user(self):
    #     body=UserSchema(username='Cor5win',email='test@example.com', password='qwer5ty')
    #     result = await create_user(body,self.session)

    #     self.assertEqual(result.username, body.username)
    #     self.assertEqual(result.email, body.email)

    #     self.assertTrue(hasattr(result, "id"))

    # async def test_make_user_role(self):
    #     body=UserSchema(username='Cor5win',email='test@example.com', password='qwer5ty')
    #     result = await create_user(body,self.session)

    #     self.assertEqual(result.username, body.username)
    #     self.assertEqual(result.email, body.email)

    #     self.assertTrue(hasattr(result, "id"))

    # async def test_add_to_blacklist(self):
    #     body=UserSchema(username='Cor5win',email='test@example.com', password='qwer5ty')
    #     result = await create_user(body,self.session)

    #     self.assertEqual(result.username, body.username)
    #     self.assertEqual(result.email, body.email)

    #     self.assertTrue(hasattr(result, "id"))

    # async def test_is_blacklisted_token(self):
    #     body=UserSchema(username='Cor5win',email='test@example.com', password='qwer5ty')
    #     result = await create_user(body,self.session)

    #     self.assertEqual(result.username, body.username)
    #     self.assertEqual(result.email, body.email)

    #     self.assertTrue(hasattr(result, "id"))

    
   
    # async def test_update_token(self):
    #     result = await update_token(self.user,self.token,self.session)

    #     self.assertEqual(self.token, self.user.refresh_token)


    

if __name__ == "__main__":
    unittest.main()