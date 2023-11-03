from sqlalchemy import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from src.repositories.pg_stats.abc import AbstractPgStatRepository
from src.schemas.pg_stats import ViewPgStatActivity, ViewPgStatActivitySummary, PgStat
from src.storages.sqlalchemy import AbstractSQLAlchemyStorage


class PgStatRepository(AbstractPgStatRepository):
    def __init__(self, storage: AbstractSQLAlchemyStorage):
        self.storage = storage

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()

    async def read_pg_stat_activity(self, limit: int) -> list[ViewPgStatActivity]:
        async with self._create_session() as session:
            statement = text(f"""SELECT * FROM pg_catalog.pg_stat_activity LIMIT {limit}""")
            pg_stat_activity = (await session.execute(statement)).fetchall()

            if pg_stat_activity:
                return [ViewPgStatActivity.model_validate(r, from_attributes=True) for r in pg_stat_activity]

    async def read_pg_stat(self, pg_stat_name: PgStat, limit: int) -> list[RowMapping]:
        async with self._create_session() as session:
            statement = text(f"""SELECT * FROM pg_catalog.pg_stat_{pg_stat_name} LIMIT {limit}""")
            pg_stat = (await session.execute(statement)).fetchall()

            if pg_stat:
                return [r._mapping for r in pg_stat]

    async def read_total_backends_count(self) -> int:
        async with self._create_session() as session:
            statement = text(f"""SELECT COUNT(*) FROM pg_catalog.pg_stat_activity""")
            total_backends_count = (await session.execute(statement)).scalar()

            if total_backends_count:
                return total_backends_count

    async def read_pg_stat_database(self) -> list[ViewPgStatActivity]:
        async with self._create_session() as session:
            statement = text(f"""SELECT * FROM pg_catalog.pg_stat_database""")
            pg_stat_database = (await session.execute(statement)).fetchall()

            if pg_stat_database:
                return [ViewPgStatActivity.model_validate(r, from_attributes=True) for r in pg_stat_database]

    async def terminate_pg_backend(self, pid: int) -> bool:
        async with self._create_session() as session:
            statement = text(f"""SELECT pg_terminate_backend({pid}) FROM pg_stat_activity""")
            termination_result = (await session.execute(statement)).first()[0]
            return termination_result

    async def read_pg_stat_summary(self) -> ViewPgStatActivitySummary:
        async with self._create_session() as session:
            statement = text(f"""SELECT state, COUNT(*) as count FROM pg_stat_activity GROUP BY state;""")
            pg_stat_database = (await session.execute(statement)).fetchall()

            if pg_stat_database:
                # translate to python dict
                pg_stat_database = {r.state: r.count for r in pg_stat_database}
                pg_stat_database["no_state"] = pg_stat_database.pop(None)
                return ViewPgStatActivitySummary(**pg_stat_database)
