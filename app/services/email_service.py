# Removed unnecessary builtins imports
from settings.config import settings
from app.utils.smtp_connection import SMTPClient
from app.utils.template_manager import TemplateManager
from app.models.user_model import User

class EmailService:
    def __init__(self, template_manager: TemplateManager):
        # Initialize the SMTP client using settings from the configuration.
        self.smtp_client = SMTPClient(
            server=settings.smtp_server,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password
        )
        self.template_manager = template_manager

    async def send_user_email(self, user_data: dict, email_type: str):
        subject_map = {
            'email_verification': "Verify Your Account",
            'password_reset': "Password Reset Instructions",
            'account_locked': "Account Locked Notification"
        }
        # Raise an error if the email type is not recognized.
        if email_type not in subject_map:
            raise ValueError("Invalid email type")
        # Render the email content using the template manager.
        html_content = self.template_manager.render_template(email_type, **user_data)
        # NOTE: The SMTP client sends email synchronously, which may block if the operation is slow.
        self.smtp_client.send_email(subject_map[email_type], html_content, user_data['email'])

    async def send_verification_email(self, user: User):
        # Construct the verification URL using the server base URL, user's id, and token.
        verification_url = f"{settings.server_base_url}verify-email/{user.id}/{user.verification_token}"
        # Call the send_user_email method with appropriate parameters.
        await self.send_user_email({
            "name": user.first_name,
            "verification_url": verification_url,
            "email": user.email
        }, 'email_verification')
