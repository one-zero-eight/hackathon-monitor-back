__all__ = ["AbstractAlertRepository"]

from abc import ABCMeta, abstractmethod

from src.schemas.alerts import AlertDB, MappedAlert, AlertDeliveryScheme


class AbstractAlertRepository(metaclass=ABCMeta):
    @abstractmethod
    async def create_alert(self, alert: "AlertDB") -> "MappedAlert":
        ...

    @abstractmethod
    async def get_alert(self, alert_id: int) -> "MappedAlert":
        ...

    @abstractmethod
    async def start_delivery(self, alert_id: int, receivers: list[int]) -> list[int]:
        ...

    @abstractmethod
    async def stop_delivery(self, alert_id: int, receivers: list[int]):
        ...

    @abstractmethod
    async def check_delivery(self) -> list["AlertDeliveryScheme"]:
        ...
