from fastapi import HTTPException

from app.models.email import EmailRequest, EmailResponse
from app.core.mailer import Mailer
from app.core.logging import get_logger

logger = get_logger(__name__)

class MailerController:
    @staticmethod
    async def send_email(request: EmailRequest) -> EmailResponse:
        try:
            logger.debug(f"Sending email [{request.template}] to {request.to}")
            message = Mailer.generate_mail(
                to=request.to,
                subject=request.subject,
                template_name=request.template,
                context=request.context,
            )

            logger.debug("Email message generated, sending...")
            await Mailer.send_mail(message)
            logger.debug(f"Email to {request.to} sent successfully")
            return EmailResponse(status="ok")
        except Exception as e:
            logger.error(f"Failed to send email to {request.to}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
