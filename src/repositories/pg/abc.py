__all__ = ["AbstractPgRepository"]

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Optional, Any

if TYPE_CHECKING:
    from src.schemas.pg_stats import ViewPgStatActivitySummary


class AbstractPgRepository(metaclass=ABCMeta):
    # ----------------- CRUD ----------------- #

    @abstractmethod
    async def read_pg_stat_summary(self) -> "ViewPgStatActivitySummary":
        ...

    @abstractmethod
    async def execute_sql(self, sql: str, binds: dict[str, Any]) -> None:
        ...

    @abstractmethod
    async def execute_sql_select(self, sql: str, limit: int, offset: int) -> Optional[list[dict[str, Any]]]:
        ...

    @abstractmethod
    async def execute_ssh(self, command: str, binds: dict[str, Any]) -> str:
        ...
