import pytest
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager

# For testing purposes, you need to provide an instance of EmailService.
# This fixture can be defined in your conftest.py or here directly.
@pytest.fixture
def email_service():
    template_manager = TemplateManager()
    return EmailService(template_manager=template_manager)

@pytest.mark.asyncio
async def test_send_markdown_email(email_service: EmailService):
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "verification_url": "http://example.com/verify?token=abc123"
    }
    # Call send_user_email asynchronously.
    await email_service.send_user_email(user_data, 'email_verification')
    # Manual verification in Mailtrap or your SMTP server should confirm that email was sent.
