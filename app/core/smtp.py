from email.message import EmailMessage
from aiosmtplib import SMTP

from app.core.config import settings


class SMTPClient():
    def __init__(self):
        # Use STARTTLS for port 587, TLS for port 465
        use_tls = settings.smtp_use_tls and settings.smtp_port == 465
        use_starttls = settings.smtp_use_tls and settings.smtp_port == 587
        
        self.client = SMTP(
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            use_tls=use_tls,
            start_tls=use_starttls,
            validate_certs=settings.smtp_verify_cert,
        )

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.quit()

    async def connect(self):
        await self.client.connect()
        if settings.smtp_user and settings.smtp_password:
            await self.client.login(settings.smtp_user, settings.smtp_password)

    async def send_message(self, message: EmailMessage):
        await self.client.send_message(message)

    async def quit(self):
        await self.client.quit()
