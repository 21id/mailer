from email.message import EmailMessage

from app.core.config import settings
from app.core.smtp import SMTPClient
from app.templates.templater import Templater


class Mailer:
    @staticmethod
    def generate_mail(
        to: str,
        subject: str,
        template_name: str,
        context: dict,
    ):
        html_content, plain_content = Templater.render_template(template_name, context)
        message = EmailMessage()
        message["From"] = settings.smtp_from or "no-reply@sdvg.dev"
        message["To"] = to
        message["Subject"] = subject
        message.set_content(plain_content)
        message.add_alternative(html_content, subtype="html")
        return message

    @staticmethod
    async def send_mail(mail: EmailMessage):
        async with SMTPClient() as smtp:
            await smtp.send_message(mail)
