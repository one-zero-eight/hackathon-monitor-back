from pathlib import Path
from typing import Union

import yaml
from pydantic import BaseModel, Field, field_validator


class Alert(BaseModel):
    class Rule(BaseModel):
        alert: str
        expr: str
        for_: str

    title: str
    description: str
    severity: int

    rule: Rule

    suggested_actions: list[str]
    related_graphs: list[str]


class Action(BaseModel):
    class Step(BaseModel):
        type: str
        query: str

    title: str
    description: str
    arguments: dict[str, Union[str, int, float]]
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
