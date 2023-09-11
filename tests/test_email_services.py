import unittest
import sys
import os
from unittest.mock import AsyncMock, patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.email import send_email, reset_password_by_email


class TestEmailFunctions(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.auth_service = MagicMock()
        self.fm = AsyncMock()

    def tearDown(self):
        self.auth_service = None
        self.fm = None

    @patch("src.services.email.FastMail")
    async def test_send_email(self, mock_fastmail):
        email = "user@example.com"
        username = "testuser"
        host = "example.com"

        fm = mock_fastmail.return_value

        fm.send_message.side_effect = ConnectionError(
            "Connection lost, check your credentials or email service configuration"
        )

        with self.assertRaises(ConnectionError):
            await send_email(email, username, host)

        fm.send_message.assert_called_once()

    @patch("src.services.email.FastMail")
    async def test_reset_password_by_email(self, mock_fastmail):
        email = "user@example.com"
        username = "testuser"
        reset_token = "reset_token"
        host = "example.com"

        fm = mock_fastmail.return_value

        fm.send_message.side_effect = ConnectionError(
            "Connection lost, check your credentials or email service configuration"
        )

        with self.assertRaises(ConnectionError):
            await reset_password_by_email(email, username, reset_token, host)

        fm.send_message.assert_called_once()


if __name__ == "__main__":
    unittest.main()
