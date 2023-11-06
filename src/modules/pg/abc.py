__all__ = ["AbstractPgRepository"]

from abc import ABCMeta, abstractmethod
from typing import Optional, Any

from src.config import Target


class AbstractPgRepository(metaclass=ABCMeta):
    # ----------------- CRUD ----------------- #
    @abstractmethod
    async def execute_sql(self, sql: str, binds: dict[str, Any], target: Target) -> None:
        ...

    @abstractmethod
    async def execute_sql_select(
        self, sql: str, limit: int, offset: int, target: Target
    ) -> Optional[list[dict[str, Any]]]:
        ...

    @abstractmethod
    async def execute_ssh(self, command: str, binds: dict[str, Any], target: Target) -> str:
        ...

    @abstractmethod
    async def fetch_targets(self) -> list[str]:
        ...
