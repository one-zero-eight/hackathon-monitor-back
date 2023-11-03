from enum import StrEnum
# from pathlib import Path
# from typing import Optional

from cryptography.hazmat.primitives import serialization
# from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
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

    # PostgreSQL database connection URL
    DB_URL: SecretStr

    # Security
    CORS_ALLOW_ORIGINS: list[str] = []

    # Authentication
    AUTH_COOKIE_NAME: str = "token"
    AUTH_COOKIE_DOMAIN: str = "innohassle.ru" if ENVIRONMENT == Environment.PRODUCTION else "localhost"
    AUTH_ALLOWED_DOMAINS: list[str] = ["innohassle.ru", "api.innohassle.ru", "localhost"]

    # SMTP server settings
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: SecretStr


settings = Settings()
