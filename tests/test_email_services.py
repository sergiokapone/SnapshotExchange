import unittest
import sys
import os  
import asyncio
from unittest.mock import Mock, ANY,patch
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.email import send_email, reset_password_by_email

class TestEmailFunctions(unittest.TestCase):

    @patch('src.services.email.FastMail')
    async def test_send_email(self, mock_fastmail):
        email = "user@example.com"
        username = "testuser"
        host = "example.com"
        
        # Mock auth_service.create_email_token
        auth_service = Mock()
        auth_service.create_email_token.return_value = "test_token"

        # Create an instance of FastMail
        fm = mock_fastmail.return_value

        # Mock fm.send_message
        fm.send_message.side_effect = ConnectionError("Connection lost, check your credentials or email service configuration")

        with self.assertRaises(ConnectionError):
            await send_email(email, username, host, auth_service, fm)
        
        fm.send_message.assert_called_once()

    @patch('src.services.email.FastMail')
    async def test_reset_password_by_email(self, mock_fastmail):
        email = "user@example.com"
        username = "testuser"
        reset_token = "reset_token"
        host = "example.com"
        
        # Create an instance of FastMail
        fm = mock_fastmail.return_value
        
        # Mock fm.send_message
        fm.send_message.side_effect = ConnectionError("Connection lost, check your credentials or email service configuration")

        with self.assertRaises(ConnectionError):
            await reset_password_by_email(email, username, reset_token, host, fm)
        
        fm.send_message.assert_called_once()

if __name__ == "__main__":
    unittest.main()