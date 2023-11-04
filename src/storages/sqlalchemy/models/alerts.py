import datetime
from typing import Any

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey

from src.storages.sqlalchemy.models.__mixin__ import IdMixin
from src.storages.sqlalchemy.models.base import Base


class Alert(Base, IdMixin):
    __tablename__ = "alerts"

    alias: Mapped[str] = mapped_column(nullable=False)
    timestamp: Mapped[datetime.datetime] = mapped_column(nullable=False)
    value: Mapped[dict[str, Any]] = mapped_column(nullable=False)


class AlertDelivery(Base, IdMixin):
    __tablename__ = "alert_deliveries"

    alert_id: Mapped[int] = mapped_column(ForeignKey(Alert.id), nullable=False)
    receiver_id: Mapped[int] = mapped_column(nullable=False)

    delivered: Mapped[bool] = mapped_column(default=False)
