import unittest
from unittest.mock import patch
from ..user_service import UserService


class TestUserService(unittest.TestCase):
            @patch('Testing_Mocking.user_service.EmailService')
            def test_register_user_sends_welcome_email(self, MockEmailService):
                # MockEmailService is now a mock object
                # 1. Configure the mock's behavior (Stubbing)
                mock_instance = MockEmailService.return_value # Get the instance that would be created
                mock_instance.send_email.return_value = True # Stub send_email to return True

                # 2. Create the service under test
                user_service = UserService(mock_instance) # Pass the mock instance

                # 3. Call the method under test
                result = user_service.register_user("Alice", "alice@example.com")

                # 4. Verify outcome and interaction
                self.assertTrue(result)
                mock_instance.send_email.assert_called_once_with(
                    "alice@example.com", "Welcome!", "Hello Alice!"
                )