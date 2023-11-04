import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field


class AlertDB(BaseModel):
    target_alias: str
    alias: str
    timestamp: datetime.datetime
    value: dict[str, Any]


class MappedAlert(BaseModel):
    id: int
    status: Optional[str] = None
    alias: str
    target_alias: str
    value: dict[str, Any]
    timestamp: datetime.datetime
    # --- Mapped --- #
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    suggested_actions: list[str] = Field(default_factory=list)
    related_views: list[str] = Field(default_factory=list)


class AlertDeliveryScheme(BaseModel):
    alert_id: int
    receiver_id: int
    delivered: bool = False
