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

    # async def test_create_comment(self):
    #         # Мокуємо об'єкт AsyncSession
    #         mock_db = AsyncMock()

    #         # Параметри для створення коментаря
    #         content = "This is a test comment"
    #         user_id = 1
    #         photo_id = 1

    #         expected_comment = Comment(
    #             text=content,
    #             user_id=user_id,
    #             photo_id=photo_id
    #         )

    #         # Мокуємо методи db.add, db.commit і db.refresh
    #         mock_db.add.return_value = None
    #         mock_db.commit.return_value = None
    #         mock_db.refresh.return_value = None

    #         # Викликаємо функцію create_comment з мокованими параметрами
    #         result = await create_comment(content, user_id, photo_id, mock_db)

    #         # Перевіряємо, чи були викликані методи db.add, db.commit і db.refresh
    #         mock_db.add.assert_called_once_with(expected_comment)
    #         mock_db.commit.assert_called_once()
    #         mock_db.refresh.assert_called_once_with(expected_comment)

    #         # Перевіряємо, чи повернутий результат співпадає з очікуваним коментарем
    #         self.assertEqual(result, expected_comment)

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

    # async def test_get_photo_comments(self):
    #     offset = 0
    #     limit = 10
    #     photo_id = 1
    
    #     # Моделюємо коментарі
    #     comments = [
    #         Comment(id=1, text="Comment 1"),
    #         Comment(id=2, text="Comment 2"),
    #         Comment(id=3, text="Comment 3"),
    #     ]

    #     # Створюємо моковий об'єкт для сесії бази даних
    #     db_session = AsyncMock(spec=AsyncSession)

    #     # Створюємо мок для execute
    #     mock_execute = AsyncMock()
    #     db_session.execute.return_value = mock_execute

    #     # Створюємо мок для результату execute (comments)
    #     mock_todos = MagicMock()
    #     mock_todos.scalars.return_value.all.return_value = comments
    #     mock_execute.scalars.return_value = mock_todos

    #     # Act
    #     result = await get_photo_comments(offset, limit, photo_id, db_session)

    #     # Assert
    #     self.assertEqual(result, comments)
    #     db_session.execute.assert_called_once()
    #     args, kwargs = db_session.execute.call_args
    #     self.assertEqual(len(args), 1)
    #     query = args[0]
    #     self.assertEqual(str(query), str(select(Comment).filter(Comment.photo_id == photo_id).offset(offset).limit(limit)))




    # async def test_get_user_comments(self):
    #     offset = 0
    #     limit = 10
    #     user_id = 1

    #     # Моделюємо коментарі
    #     comments = [
    #         Comment(id=1, text="Comment 1"),
    #         Comment(id=2, text="Comment 2"),
    #         Comment(id=3, text="Comment 3"),
    #     ]

    #     # Створюємо мок для результату execute (comments)
    #     mock_comments = MagicMock()
    #     mock_comments.scalars.return_value.all.return_value = comments
    #     self.session.scalars.return_value.all.return_value = mock_comments

    #     # Act
    #     result = await get_user_comments(offset, limit, user_id, self.session)

    #     # Assert
    #     self.assertEqual(result, comments)
    #     self.session.execute.assert_called_once()
    #     args, kwargs = self.session.execute.call_args
    #     self.assertEqual(len(args), 1)
    #     query = args[0]
    #     self.assertEqual(str(query), str(select(Comment).filter(Comment.user_id == user_id).offset(offset).limit(limit)))
    
if __name__ == "__main__":
    unittest.main()