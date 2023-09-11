import unittest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
import sys
import os
from fastapi.testclient import TestClient


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


class TestAsyncMethod(unittest.IsolatedAsyncioTestCase):
    def asyncSetUp(self):
        self.client = TestClient(app)
        self.session = AsyncMock(spec=AsyncSession())

    def asyncTearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
