__all__ = ["AbstractPgStatRepository"]

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from sqlalchemy import RowMapping

if TYPE_CHECKING:
    from src.schemas.pg_stats import ViewPgStatActivitySummary, ViewPgStatDatabase, PgStat


class AbstractPgStatRepository(metaclass=ABCMeta):
    # ----------------- CRUD ----------------- #

    @abstractmethod
    async def read_pg_stat(self, pg_stat_name: "PgStat", limit: int) -> list[RowMapping]:
        ...

    @abstractmethod
    async def read_total_backends_count(self) -> int:
        ...

    @abstractmethod
    async def read_pg_stat_database(self) -> list["ViewPgStatDatabase"]:
        ...

    @abstractmethod
    async def terminate_pg_backend(self, pid: int) -> bool:
        ...

    @abstractmethod
    async def read_pg_stat_summary(self) -> "ViewPgStatActivitySummary":
        ...
