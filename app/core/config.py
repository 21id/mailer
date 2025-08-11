from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings, extra="ignore"):
    # SMTP settings
    smtp_host: str = Field(..., env="SMTP_HOST")
    smtp_port: int = Field(..., env="SMTP_PORT")
    smtp_from: Optional[str] = Field(None, env="SMTP_FROM")
    smtp_user: Optional[str] = Field(None, env="SMTP_USER")
    smtp_password: Optional[str] = Field(None, env="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=True, env="SMTP_USE_TLS")
    smtp_verify_cert: bool = Field(default=True, env="SMTP_VERIFY_CERT")

    # AMQP settings
    amqp_host: str = Field(..., env="AMQP_HOST")
    amqp_port: int = Field(..., env="AMQP_PORT")
    amqp_user: Optional[str] = Field(None, env="AMQP_USER")
    amqp_password: Optional[str] = Field(None, env="AMQP_PASSWORD")
    amqp_vhost: Optional[str] = Field(None, env="AMQP_VHOST")
    amqp_queue: Optional[str] = Field(None, env="AMQP_QUEUE")

    # API Secret Key
    secret_key: str = Field(..., env="SECRET_KEY")
    
    # Version
    version: str = Field(..., env="VERSION")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
