from enum import StrEnum
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo

from src.config import settings as app_settings


class Alert(BaseModel):
    class Rule(BaseModel):
        annotations: dict[str, Any]
        expr: str
        for_: Optional[str] = Field(None, alias="for")

    title: str
    description: Optional[str] = ""
    severity: str

    rule: Rule

    suggested_actions: list[str]
    related_views: list[str]


class Argument(BaseModel):
    type: str
    default: Optional[Any] = "ellipsis"
    description: str = ""
    required: bool = True

    def field_info(self) -> FieldInfo:
        if self.default == "ellipsis":
            return FieldInfo(description=self.description)
        else:
            return FieldInfo(default=self.default, description=self.description)


class Action(BaseModel):
    class Step(BaseModel):
        class Type(StrEnum):
            sql = "sql"
            ssh = "ssh"

        type: Type
        query: str

    title: str
    description: Optional[str] = ""
    arguments: dict[str, Argument] = Field(default_factory=dict)
    steps: list[Step]


class View(BaseModel):
    title: str
    description: str
    sql: str


class MonitoringConfig(BaseModel):
    alerts: dict[str, Alert] = Field(default_factory=dict)
    actions: dict[str, Action] = Field(default_factory=dict)
    views: dict[str, View] = Field(default_factory=dict)

    @classmethod
    def from_yamls(cls, alert_path: Path, actions_path: Path, views_path: Path) -> "MonitoringConfig":
        with open(alert_path, "r", encoding="utf-8") as f:
            alerts_config = yaml.safe_load(f)

        with open(actions_path, "r", encoding="utf-8") as f:
            actions_config = yaml.safe_load(f)

        with open(views_path, "r", encoding="utf-8") as f:
            views_config = yaml.safe_load(f)

        return cls(alerts=alerts_config["alerts"], actions=actions_config["actions"], views=views_config["views"])


settings = MonitoringConfig.from_yamls(
    alert_path=app_settings.ALERTS_CONFIG_PATH,
    actions_path=app_settings.ACTIONS_CONFIG_PATH,
    views_path=app_settings.VIEWS_CONFIG_PATH,
)
