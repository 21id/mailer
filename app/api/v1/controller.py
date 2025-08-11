from fastapi import HTTPException

from app.models.email import EmailRequest, EmailResponse
from app.core.mailer import Mailer


class MailerController:
    @staticmethod
    async def send_email(request: EmailRequest) -> EmailResponse:
        try:
            message = Mailer.generate_mail(
                to=request.to,
                subject=request.subject,
                template_name=request.template,
                context=request.context,
            )
            await Mailer.send_mail(message)
            return EmailResponse(status="ok")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
