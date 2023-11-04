__all__ = ["AbstractPgRepository"]

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from sqlalchemy import RowMapping

if TYPE_CHECKING:
    from src.schemas.pg_stats import ViewPgStatActivitySummary, PgStat


class AbstractPgRepository(metaclass=ABCMeta):
    # ----------------- CRUD ----------------- #

    @abstractmethod
    async def read_pg_stat(self, pg_stat_name: "PgStat", limit: int, offset: int) -> list[RowMapping]:
        ...

    @abstractmethod
    async def read_total_backends_count(self) -> int:
        ...

    @abstractmethod
    async def terminate_pg_backend(self, pid: int) -> bool:
        ...

    @abstractmethod
    async def read_pg_stat_summary(self) -> "ViewPgStatActivitySummary":
        ...

    @abstractmethod
    async def execute_sql(self, sql: str, /, **binds) -> None:
        ...

    @abstractmethod
    async def execute_ssh(self, command: str, /, **binds) -> str:
        ...
