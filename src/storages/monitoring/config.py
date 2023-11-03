from enum import StrEnum
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field

from src.config import settings as app_settings


class Alert(BaseModel):
    class Rule(BaseModel):
        annotations: dict[str, Any]
        expr: str
        for_: Optional[str] = Field(None, alias="for")

    title: str
    description: str
    severity: int

    rule: Rule

    suggested_actions: list[str]
    related_graphs: list[str]


class Action(BaseModel):
    class Step(BaseModel):
        class Type(StrEnum):
            sql = "sql"
            ssh = "ssh"

        type: Type
        query: str

    class Argument(BaseModel):
        class Type(StrEnum):
            string = "string"
            int = "int"
            float = "float"
            bool = "bool"

        type: Type
        description: str = ""
        required: bool = True

    title: str
    description: str
    arguments: dict[str, Argument]
    steps: list[Step]

    # TODO: sqlalchemy check injection in text statement


class Graph(BaseModel):
    title: str
    graphana_url: str


class MonitoringConfig(BaseModel):
    alerts: dict[str, Alert] = Field(default_factory=dict)
    actions: dict[str, Action] = Field(default_factory=dict)
    graphs: dict[str, Graph] = Field(default_factory=dict)

    @classmethod
    def from_yamls(cls, alert_path: Path, actions_path: Path) -> "MonitoringConfig":
        with open(alert_path, "r") as f:
            alerts_config = yaml.safe_load(f)

        with open(actions_path, "r") as f:
            actions_config = yaml.safe_load(f)

        return cls(alerts=alerts_config["alerts"], actions=actions_config["actions"])


settings = MonitoringConfig.from_yamls(
    alert_path=app_settings.ALERTS_CONFIG_PATH,
    actions_path=app_settings.ACTIONS_CONFIG_PATH,
)
