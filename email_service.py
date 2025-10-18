class EmailService:
    def send_email(self, recipient, subject, body):
        # In real life, this would send an actual email
        print(f"Sending email to {recipient}: {subject}")
        return True