from enum import StrEnum
from pathlib import Path
from typing import Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from pydantic import SecretStr, model_validator, field_validator, BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class JWT(BaseModel):
    # Run 'openssl genrsa -out private.pem 2048' to generate keys
    PRIVATE_KEY_PATH: Path = Path("private.pem")
    # For existing key run 'openssl rsa -in private.pem -pubout -out public.pem'
    PUBLIC_KEY_PATH: Path = Path("public.pem")
    PRIVATE_KEY: Optional[RSAPrivateKey] = None
    PUBLIC_KEY: Optional[RSAPublicKey] = None

    @field_validator("PRIVATE_KEY_PATH", mode="before")
    @classmethod
    def parse_jwt_keys_private(cls, value):
        if isinstance(value, str):
            return serialization.load_pem_private_key(value.encode(), password=None)
        return value

    @field_validator("PUBLIC_KEY_PATH", mode="before")
    @classmethod
    def parse_jwt_keys_public(cls, value):
        if isinstance(value, str):
            return serialization.load_pem_public_key(value.encode())
        return value

    @model_validator(mode="after")
    def validate_jwt_keys(self):
        if self.PRIVATE_KEY is None:
            self.PRIVATE_KEY = serialization.load_pem_private_key(
                self.PRIVATE_KEY_PATH.read_bytes(), password=None
            )
        if self.PUBLIC_KEY is None:
            self.PUBLIC_KEY = serialization.load_pem_public_key(self.PUBLIC_KEY_PATH.read_bytes())


class TARGET(BaseModel):
    DB_URL: SecretStr
    SSH_HOST: str
    SSH_CREDENTIALS_USERNAME: str
    SSH_CREDENTIALS_PASSWORD: str


class SMTP(BaseModel):
    ENABLE: bool = False
    SERVER: str = "mail.innopolis.ru"
    PORT: int = 587
    USERNAME: str
    PASSWORD: SecretStr


class AUTH(BaseModel):
    # Authentication
    AUTH_COOKIE_NAME: str = "token"
    AUTH_COOKIE_DOMAIN: str = "innohassle.ru"
    AUTH_ALLOWED_DOMAINS: list[str] = ["innohassle.ru", "api.innohassle.ru", "localhost"]


class Settings(BaseSettings):
    """
    Settings for the application. Get settings from .env file.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore",
                                      env_nested_delimiter="__")

    # Prefix for the API path (e.g. "/api/v0")
    APP_ROOT_PATH: str = ""

    # App environment
    ENVIRONMENT: Environment = Environment.DEVELOPMENT

    # You can run 'openssl rand -hex 32' to generate keys
    SESSION_SECRET_KEY: SecretStr
    BOT_TOKEN: SecretStr

    # PostgreSQL database connection URL
    DB_URL: SecretStr

    # JWT settings
    JWT: JWT = Field(default_factory=JWT)
    # Target DB and SSH for monitoring
    TARGET: TARGET = Field(default_factory=TARGET)
    # Authentication
    AUTH: AUTH = Field(default_factory=AUTH)
    # SMTP server settings
    SMTP: SMTP = Field(default_factory=SMTP)

    # Security
    CORS_ALLOW_ORIGINS: list[str] = []

    # Monitoring
    ALERTS_CONFIG_PATH: Path = Path("alerts.yaml")
    ACTIONS_CONFIG_PATH: Path = Path("actions.yaml")


# class DbConfig(BaseModel):
#     host: str = Field(examples=["localhost"])
#     password: str = Field(examples=["mysecretpassword"])
#     user: str = Field(examples=["postgres"])
#     name: str = Field(examples=["postgres"])
#     port: str = Field(examples=["5432"])
#
#     @property
#     def database(self):
#         return self.name
#
#
# class TgBot(BaseModel):
#     token: str = Field(..., examples=["1234567890:ABCdefGhIJKlmnOpQrStUvWxYz-lr4zF0ZU"])
#     admin_id: int = Field(..., examples=[1234567890])
#     redis: Optional[str] = Field(None, examples=["redis://localhost:6379/0"])
#
#
# class Miscellaneous(BaseModel):
#     pay_token: Optional[str] = Field(None, examples=["test"])
#
#
# class CodeTest(BaseModel):
#     host: str = Field(examples=["localhost"])
#     port: str = Field(examples=["8000"])
#
#
# class EnvSettings(BaseSettings):
#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         env_nested_delimiter="__",
#     )
#
#     BOT: TgBot
#     DB: DbConfig
#     MISC: Miscellaneous
#     CODE_TEST: CodeTest
#
#     @property
#     def tg_bot(self):
#         return self.BOT
#
#     @property
#     def db(self):
#         return self.DB


settings = Settings()
