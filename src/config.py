from enum import StrEnum
from pathlib import Path
from typing import Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from pydantic import SecretStr, model_validator, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class Settings(BaseSettings):
    """
    Settings for the application. Get settings from .env file.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Prefix for the API path (e.g. "/api/v0")
    APP_ROOT_PATH: str = ""

    # App environment
    ENVIRONMENT: Environment = Environment.DEVELOPMENT

    # You can run 'openssl rand -hex 32' to generate keys
    SESSION_SECRET_KEY: SecretStr
    BOT_TOKEN: SecretStr

    # Run 'openssl genrsa -out private.pem 2048' to generate keys
    JWT_PRIVATE_KEY_PATH: Path = Path("private.pem")
    JWT_PRIVATE_KEY: Optional[RSAPrivateKey] = None
    # For existing key run 'openssl rsa -in private.pem -pubout -out public.pem'
    JWT_PUBLIC_KEY_PATH: Path = Path("public.pem")
    JWT_PUBLIC_KEY: Optional[RSAPublicKey] = None

    # PostgreSQL database connection URL
    DB_URL: SecretStr

    # Target DB for monitoring
    TARGET_DB_URL: SecretStr

    # Security
    CORS_ALLOW_ORIGINS: list[str] = []

    # Authentication
    AUTH_COOKIE_NAME: str = "token"
    AUTH_COOKIE_DOMAIN: str = "innohassle.ru" if ENVIRONMENT == Environment.PRODUCTION else "localhost"
    AUTH_ALLOWED_DOMAINS: list[str] = ["innohassle.ru", "api.innohassle.ru", "localhost"]

    # SMTP server settings
    SMTP_ENABLE: bool = False
    SMTP_SERVER: str = "mail.innopolis.ru"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: SecretStr

    @field_validator("JWT_PRIVATE_KEY", mode="before")
    @classmethod
    def parse_jwt_keys_private(cls, value):
        if isinstance(value, str):
            return serialization.load_pem_private_key(value.encode(), password=None)
        return value

    @field_validator("JWT_PUBLIC_KEY", mode="before")
    @classmethod
    def parse_jwt_keys_public(cls, value):
        if isinstance(value, str):
            return serialization.load_pem_public_key(value.encode())
        return value

    @model_validator(mode="after")
    def validate_jwt_keys(self):
        if self.JWT_PRIVATE_KEY is None:
            self.JWT_PRIVATE_KEY = serialization.load_pem_private_key(
                self.JWT_PRIVATE_KEY_PATH.read_bytes(), password=None
            )
        if self.JWT_PUBLIC_KEY is None:
            self.JWT_PUBLIC_KEY = serialization.load_pem_public_key(self.JWT_PUBLIC_KEY_PATH.read_bytes())


settings = Settings()
