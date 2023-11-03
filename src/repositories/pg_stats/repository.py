from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from src.schemas.pg_stats import ViewPgStatActivity
from src.repositories.pg_stats.abc import AbstractPgStatRepository
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
