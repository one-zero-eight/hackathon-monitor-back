import datetime
from typing import Optional, Any

import jinja2
import paramiko
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.config import settings, Target
from src.repositories.pg.abc import AbstractPgRepository
from src.schemas.pg_stats import ViewPgStatActivitySummary
from src.storages.sqlalchemy import AbstractSQLAlchemyStorage


def table_rows_to_list_of_dicts(table_rows: list[Row], /) -> list[dict[str, Any]]:
    rows = []
    for table_row in table_rows:
        r = table_row._mapping
        row = dict()
        # translate to dict[str, str]
        for k, v in r.items():
            key = str(k)
            if v is None:
                row[key] = None
            elif isinstance(v, (bool, int, float, str, datetime.datetime, datetime.date)):
                row[key] = v
            else:
                row[key] = str(v)
        rows.append(row)
    return rows


class PgRepository(AbstractPgRepository):
    def __init__(self, storage: AbstractSQLAlchemyStorage):
        self.storage = storage

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()

    async def read_pg_stat_summary(self, target: Target) -> ViewPgStatActivitySummary:
        engine = create_async_engine(target.DB_URL.get_secret_value(), pool_recycle=3600)

        async with engine.connect() as session:
            statement = text("""SELECT state, COUNT(*) as count FROM pg_stat_activity GROUP BY state;""")
            pg_stat_database = (await session.execute(statement)).fetchall()

            if pg_stat_database:
                # translate to python dict
                pg_stat_database = {r.state: r.count for r in pg_stat_database}
                pg_stat_database["no_state"] = pg_stat_database.pop(None)
                return ViewPgStatActivitySummary(**pg_stat_database)

    async def execute_sql(self, sql: str, binds: dict[str, Any], target: Target) -> None:
        engine = create_async_engine(target.DB_URL.get_secret_value(), pool_recycle=3600)

        async with engine.connect() as session:
            statement = text(sql)
            # get all params from statement
            params = statement.compile().params
            binds = {k: v for k, v in binds.items() if k in params}
            statement = statement.bindparams(**binds)
            await session.execute(statement)
            await session.commit()

    async def execute_sql_select(
        self, sql: str, limit: int, offset: int, target: Target
    ) -> Optional[list[dict[str, Any]]]:
        engine = create_async_engine(target.DB_URL.get_secret_value(), pool_recycle=3600)

        async with engine.connect() as session:
            statement = text(sql)
            # get all params from statement
            params = statement.compile().params
            binds = dict(limit=limit, offset=offset)
            binds = {k: v for k, v in binds.items() if k in params}
            statement = statement.bindparams(**binds)
            r = await session.execute(statement)
            table_rows = r.fetchall()
            return table_rows_to_list_of_dicts(list(table_rows))

    async def execute_ssh(self, command: str, binds: dict[str, Any], target: Target) -> None:
        client = paramiko.client.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        command_template = jinja2.Environment(autoescape=True).from_string(command)
        target.DB_URL = target.DB_URL.get_secret_value()
        target_dict = {f"TARGET__{k}": v for k, v in target.model_dump().items()}
        binds.update(**settings.flatten(), **target_dict)
        binded = command_template.render(**binds)
        client.connect(
            hostname=target.SSH_HOST,
            port=target.SSH_PORT,
            username=target.SSH_USERNAME,
            password=target.SSH_PASSWORD,
        )
        # TODO: Think how to fetch responses better
        _stdin, _stdout, _stderr = client.exec_command(binded)

    async def fetch_targets(self) -> list[str]:
        return list(settings.TARGETS.keys())
