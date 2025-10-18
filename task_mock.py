from unittest.mock import Mock

class EmailService:
    def send_email(self, to, subject, body):
        pass  # في الحقيقة ترسل البريد

class RegistrationService:
    def __init__(self, email_service):
        self.email_service = email_service

    def register(self, user):
        # تسجيل المستخدم...
        self.email_service.send_email(user['email'], 'Welcome!', 'Hello!')
        return True

# الاختبار
def test_register_sends_email():
    mock_email = Mock()
    service = RegistrationService(mock_email)
    service.register({'email': 'alice@example.com'})
    mock_email.send_email.assert_called_once_with('alice@example.com', 'Welcome!', 'Hello!')
