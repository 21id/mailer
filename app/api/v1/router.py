from fastapi import APIRouter, Depends

from app.api.v1.controller import MailerController
from app.core.security import verify_secret_key
from app.models.email import EmailRequest, EmailResponse

mailer_router = APIRouter(
    tags=["mailer/v1"],
)


@mailer_router.post(
    "/send",
    dependencies=[Depends(verify_secret_key)],
    response_model=EmailResponse,
    summary="Sends an email to the recipient",
)
async def send_email(request: EmailRequest):
    return await MailerController.send_email(request)
