from pydantic import BaseModel, EmailStr, Field

class EmailRequest(BaseModel):
    """
    Request model for sending emails.
    """
    
    to: EmailStr = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Subject of the email")
    template: str = Field(..., description="Name of the template to use for rendering the email")
    context: dict = Field(..., description="Context data for template rendering")
    
    class Config:
        json_schema_extra = {
            "example": {
                "to": "kristana@students.21-school.ru",
                "subject": "Test Mail",
                "template": "test.html",
                "context": {
                    "username": "Kristana",
                    "verification_link": "https://21id.ru/verify?token=abc123"
                }
            }
        }
        
class EmailResponse(BaseModel):
    """
    Response model for sending emails.
    """
    
    status: str = Field(..., description="Status of the operation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok"
            }
        }