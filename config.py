from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    DATABASE_URL: str = "sqlite:///./marta.db"
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    class Config:
        env_file = ".env"

settings = Settings()