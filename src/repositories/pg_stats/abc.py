__all__ = ["AbstractPgStatRepository"]

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.schemas.pg_stats import ViewPgStatActivity, TerminatePgBackend


class AbstractPgStatRepository(metaclass=ABCMeta):
    # ----------------- CRUD ----------------- #

    @abstractmethod
    async def read_pg_stat_activity(self, limit: int) -> "ViewPgStatActivity":
        ...

    @abstractmethod
    async def terminate_pg_backend(self, pid: int) -> "TerminatePgBackend":
        ...
