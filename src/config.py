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

    @model_validator(mode="before")
    def all_keys_to_upper(cls, values):
        return {key.upper(): value for key, value in values.items()}


class Prometheus(BaseModel):
    URL: str = "http://localhost:9090"
    ALERT_RULES_PATH: Path = Path("./prometheus/alert_rules.yml")

    @model_validator(mode="before")
    def all_keys_to_upper(cls, values):
        return {key.upper(): value for key, value in values.items()}


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
            # [11111,222222] -> [11111, 222222]
            import re

            # all numbers in string
            value = re.findall(r"\d+", value)
            return [int(v) for v in value]
        return value

    @model_validator(mode="before")
    def all_keys_to_upper(cls, values):
        return {key.upper(): value for key, value in values.items()}


class Smtp(BaseModel):
    SERVER: str = "mail.innopolis.ru"
    PORT: int = 587
    USERNAME: str
    PASSWORD: SecretStr

    @model_validator(mode="before")
    def all_keys_to_upper(cls, values):
        return {key.upper(): value for key, value in values.items()}


class Cookies(BaseModel):
    # Authentication
    NAME: str = "token"
    DOMAINS: str = "innohassle.ru"
    ALLOWED_DOMAINS: list[str] = ["innohassle.ru", "api.innohassle.ru", "localhost"]

    @model_validator(mode="before")
    def all_keys_to_upper(cls, values):
        return {key.upper(): value for key, value in values.items()}


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
    JWT_ENABLED: bool = False
    JWT: Optional[Jwt] = None
    # Target DB and SSH for monitoring
    TARGET: Target = Field(default_factory=Target)
    # Authentication
    COOKIE: Cookies = Field(default_factory=Cookies)
    # SMTP server settings
    SMTP_ENABLED: bool = False
    SMTP: Optional[Smtp] = None
    # Prometheus settings
    PROMETHEUS: Prometheus = Field(default_factory=Prometheus)
    # Security
    CORS_ALLOW_ORIGINS: list[str] = []

    # Monitoring
    ALERTS_CONFIG_PATH: Path = Path("alerts.yaml")
    ACTIONS_CONFIG_PATH: Path = Path("actions.yaml")
    VIEWS_CONFIG_PATH: Path = Path("views.yaml")

    def flatten(self):
        """
        Flatten settings to dict.
        """
        nested = self.model_dump(include={"JWT", "TARGET", "AUTH", "SMTP", "PROMETHEUS"})
        flattened = self.model_dump(exclude={"model_config", "JWT", "TARGET", "AUTH", "SMTP", "PROMETHEUS"})

        for key, value in nested.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    flattened[f"{key}__{k}"] = v
            else:
                flattened[key] = value

        return flattened


settings = Settings()
