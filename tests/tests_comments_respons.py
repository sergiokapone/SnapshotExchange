import unittest
from unittest.mock import AsyncMock,MagicMock,patch
from sqlalchemy.ext.asyncio import AsyncSession
import sys
import os
from sqlalchemy.future import select


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import Rating,Photo,User,Comment,QR_code,Tag,Role
from src.schemas import UserSchema,PhotosDb
from src.repository.comments import create_comment,get_comment,update_comment,delete_comment,get_photo_comments,get_user_comments


class TestAsyncMethod(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession())
        
    def tearDown(self):
        del self.session


    async def test_get_comment(self):
        comment_id = 1
        comment_text = "This is a test comment"
        mock_comment = Comment(id=comment_id, text=comment_text)
        self.session.get.return_value = mock_comment


        result = await get_comment(comment_id, self.session)


        self.assertEqual(result, mock_comment)
        self.session.get.assert_called_once_with(Comment, comment_id)

    async def test_update_comment(self):
        comment_id = 1
        new_comment_text = "Updated comment text"
        mock_comment = Comment(id=comment_id, text="Original comment text", update_status=False)
        self.session.get.return_value = mock_comment

        result = await update_comment(new_comment_text, comment_id, self.session)

        self.assertEqual(result.text, new_comment_text)
        self.assertEqual(result.update_status, True)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(mock_comment)

    async def test_delete_comment(self):
        comment_id = 1
        mock_comment = Comment(id=comment_id, text="Test comment")
        self.session.get.return_value = mock_comment

        result = await delete_comment(comment_id, self.session)

        self.assertEqual(result, mock_comment)
        self.session.delete.assert_called_once_with(mock_comment)
        self.session.commit.assert_called_once()

    
if __name__ == "__main__":
    unittest.main()