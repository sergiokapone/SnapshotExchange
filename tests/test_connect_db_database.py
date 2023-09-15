import unittest
import sys
import os
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connect_db import get_db,DatabaseSessionManager


class TestRstToHtml(unittest.IsolatedAsyncioTestCase):
    
    def test_database_session_manager(self):
        test_db_url = "sqlite+aiosqlite:///:memory:"
        database_session_manager = DatabaseSessionManager(test_db_url)

        session = database_session_manager.session()

        self.assertIsNotNone(session)

    async def test_get_db(self):
        res= get_db()
        self.assertIsNotNone(res)




if __name__ == "__main__":
    unittest.main()
