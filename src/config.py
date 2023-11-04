from enum import StrEnum
from pathlib import Path
from typing import Optional

from pydantic import SecretStr, model_validator, field_validator, BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class Jwt(BaseModel):
    # Run 'openssl genrsa -out private.pem 2048' to generate keys
    PRIVATE_KEY_PATH: Path = Path("private.pem")
    # For existing key run 'openssl rsa -in private.pem -pubout -out public.pem'
    PUBLIC_KEY_PATH: Path = Path("public.pem")
    PRIVATE_KEY: Optional[bytes] = None
    PUBLIC_KEY: Optional[bytes] = None

    @field_validator("PUBLIC_KEY", "PRIVATE_KEY", mode="before")
    @classmethod
    def parse_jwt_keys_private(cls, value):
        if isinstance(value, str):
            return value.encode()
        return value

    @model_validator(mode="after")
    def validate_jwt_keys(self):
        if self.PRIVATE_KEY is None:
            self.PRIVATE_KEY = self.PRIVATE_KEY_PATH.read_bytes()
        if self.PUBLIC_KEY is None:
            self.PUBLIC_KEY = self.PUBLIC_KEY_PATH.read_bytes()


class Prometheus(BaseModel):
    URL: str = "http://localhost:9090"
    ALERT_RULES_PATH: Path = Path("./prometheus/alert_rules.yml")


class Target(BaseModel):
    DB_URL: SecretStr
    SSH_HOST: str
    SSH_PORT: int = 22
    SSH_USERNAME: str
    SSH_PASSWORD: str
    RECEIVERS: list[int] = Field(default_factory=list)

    @field_validator("RECEIVERS", mode="before")
    @classmethod
    def parse_receivers(cls, value):
        if isinstance(value, str):
            return [int(i) for i in value.split()]
        return value


class Smtp(BaseModel):
    ENABLE: bool = False
    SERVER: str = "mail.innopolis.ru"
    PORT: int = 587
    USERNAME: str
    PASSWORD: SecretStr


class Auth(BaseModel):
    # Authentication
    COOKIE_NAME: str = "token"
    COOKIE_DOMAIN: str = "innohassle.ru"
    ALLOWED_DOMAINS: list[str] = ["innohassle.ru", "api.innohassle.ru", "localhost"]


class Settings(BaseSettings):
    """
    Settings for the application. Get settings from .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", env_nested_delimiter="__"
    )

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
    JWT: Jwt = Field(default_factory=Jwt)
    # Target DB and SSH for monitoring
    TARGET: Target = Field(default_factory=Target)
    # Authentication
    AUTH: Auth = Field(default_factory=Auth)
    # SMTP server settings
    SMTP: Smtp = Field(default_factory=Smtp)
    # Prometheus settings
    PROMETHEUS: Prometheus = Field(default_factory=Prometheus)
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
