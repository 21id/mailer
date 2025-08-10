from typing import Optional
from pydantic import EmailStr, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings, extra="ignore"):
    smtp_host: str = Field(..., env="SMTP_HOST")
    smtp_port: int = Field(..., env="SMTP_PORT")
    
    smtp_from: Optional[str] = Field(None, env="SMTP_FROM")
    smtp_user: Optional[str] = Field(None, env="SMTP_USER")
    smtp_password: Optional[str] = Field(None, env="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=True, env="SMTP_USE_TLS")
    smtp_verify_cert: bool = Field(default=True, env="SMTP_VERIFY_CERT")

    mqtt_broker: str = Field(..., env="MQTT_BROKER")
    mqtt_port: int = Field(default=1883, env="MQTT_PORT")
    mqtt_username: Optional[str] = Field(None, env="MQTT_USERNAME")
    mqtt_password: Optional[str] = Field(None, env="MQTT_PASSWORD")
    mqtt_topic: str = Field(default="mailer/requests", env="MQTT_TOPIC")
    mqtt_client_id: str = Field(default="mailer_service", env="MQTT_CLIENT_ID")
    mqtt_keepalive: int = Field(default=60, env="MQTT_KEEPALIVE")

    log_level: str = Field(default="DEBUG", env="LOG_LEVEL")
    log_file: Optional[str] = Field(None, env="LOG_FILE")

    secret_key: str = Field(..., env="SECRET_KEY")
    
    version: str = Field(..., env="VERSION")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
