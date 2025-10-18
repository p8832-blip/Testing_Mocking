class EmailService:
    def send_email(self, to, subject, body):
        print(f"Sending email to {to}: {subject}")
        return True


class UserService:
    def __init__(self, email_service: EmailService):
        self.email_service = email_service

    def register_user(self, username, email):
        if not username or not email:
            return False
        success = self.email_service.send_email(email, "Welcome!", f"Hello {username}!")
        return success
