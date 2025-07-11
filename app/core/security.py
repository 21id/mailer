from fastapi import Header, HTTPException, status
from app.core.config import settings


def verify_secret_key(x_secret_key: str = Header(...)):
    if x_secret_key != settings.secret_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid secret key"
        )
