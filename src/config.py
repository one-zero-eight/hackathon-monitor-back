__all__ = ["settings", "Settings", "Target"]

import os
from enum import StrEnum
from pathlib import Path
from typing import Optional

import yaml
from pydantic import SecretStr, model_validator, field_validator, BaseModel, Field, ConfigDict


class Environment(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class Prometheus(BaseModel):
    URL: str = "http://localhost:9090"
    ALERT_RULES_PATH: Path = Path("./prometheus/alert_rules.yml")
    PROMETHEUS_CONFIG_PATH: Path = Path("./prometheus/prometheus.yml")

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


class Settings(BaseModel):
    """
    Settings for the application. Get settings from .env file.
    """

    model_config = ConfigDict(extra="ignore")

    # Prefix for the API path (e.g. "/api/v0")
    APP_ROOT_PATH: str = ""
    # App environment
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    BOT_TOKEN: SecretStr
    # PostgreSQL database connection URL
    DB_URL: SecretStr
    # Target DB and SSH for monitoring
    TARGETS: dict[str, Target] = Field(default_factory=dict)
    # Authentication
    COOKIE: Cookies = Field(default_factory=Cookies)
    # SMTP server settings
    SMTP_ENABLED: bool = False
    SMTP: Optional[Smtp] = None
    # Prometheus settings
    PROMETHEUS: Prometheus = Field(default_factory=Prometheus)
    # Monitoring
    ALERTS_CONFIG_PATH: Path = Path("alerts.yaml")
    ACTIONS_CONFIG_PATH: Path = Path("actions.yaml")
    VIEWS_CONFIG_PATH: Path = Path("views.yaml")

    def flatten(self):
        """
        Flatten settings to dict.
        """
        nested = self.model_dump(include={"AUTH", "SMTP", "PROMETHEUS"})
        flattened = self.model_dump(exclude={"model_config", "AUTH", "SMTP", "PROMETHEUS"})

        for key, value in nested.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    flattened[f"{key}__{k}"] = v
            else:
                flattened[key] = value

        return flattened

    @model_validator(mode="before")
    def all_keys_to_upper(cls, values):
        return {key.upper(): value for key, value in values.items()}

    @classmethod
    def from_yaml(cls, path: Path) -> "Settings":
        with open(path, "r", encoding="utf-8") as f:
            yaml_config = yaml.safe_load(f)

        return cls.model_validate(yaml_config)


settings_path = os.getenv("SETTINGS_PATH")
if settings_path is None:
    settings_path = "settings.yaml"
settings = Settings.from_yaml(Path(settings_path))
