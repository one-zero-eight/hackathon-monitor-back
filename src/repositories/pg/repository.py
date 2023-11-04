import datetime
from typing import Optional, Any

import jinja2
import paramiko
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from src.config import settings
from src.repositories.pg.abc import AbstractPgRepository
from src.schemas.pg_stats import ViewPgStatActivity, ViewPgStatActivitySummary, PgStat
from src.storages.sqlalchemy import AbstractSQLAlchemyStorage


class PgRepository(AbstractPgRepository):
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

    async def read_pg_stat(self, pg_stat_name: PgStat, limit: int, offset: int) -> Optional[list[dict[str, Any]]]:
        async with self._create_session() as session:
            statement = text(f"""SELECT * FROM pg_catalog.pg_stat_{pg_stat_name} LIMIT {limit} OFFSET {offset}""")
            pg_stat = (await session.execute(statement)).fetchall()

            if pg_stat:
                return table_rows_to_list_of_dicts(list(pg_stat))

    async def read_total_backends_count(self) -> int:
        async with self._create_session() as session:
            statement = text("""SELECT COUNT(*) FROM pg_catalog.pg_stat_activity""")
            total_backends_count = (await session.execute(statement)).scalar()

            if total_backends_count:
                return total_backends_count

    async def terminate_pg_backend(self, pid: int) -> bool:
        async with self._create_session() as session:
            statement = text("""SELECT pg_terminate_backend(:pid)""")
            # get all params from statement
            params = statement.compile().params
            binds = {"pid": pid, "test": "test"}
            binds = {k: v for k, v in binds.items() if k in params}
            statement = statement.bindparams(**binds)
            termination_result = (await session.execute(statement)).first()[0]
            return termination_result

    async def read_pg_stat_summary(self) -> ViewPgStatActivitySummary:
        async with self._create_session() as session:
            statement = text("""SELECT state, COUNT(*) as count FROM pg_stat_activity GROUP BY state;""")
            pg_stat_database = (await session.execute(statement)).fetchall()

            if pg_stat_database:
                # translate to python dict
                pg_stat_database = {r.state: r.count for r in pg_stat_database}
                pg_stat_database["no_state"] = pg_stat_database.pop(None)
                return ViewPgStatActivitySummary(**pg_stat_database)

    async def execute_sql(self, sql: str, fetchall: bool = False, /, **binds) -> Optional[list[dict[str, Any]]]:
        async with self._create_session() as session:
            statement = text(sql)
            # get all params from statement
            params = statement.compile().params
            binds = {k: v for k, v in binds.items() if k in params}
            statement = statement.bindparams(**binds)
            r = await session.execute(statement)
            if fetchall:
                table_rows = r.fetchall()
                return table_rows_to_list_of_dicts(list(table_rows))

    async def execute_ssh(self, command: str, /, **binds) -> str:
        client = paramiko.client.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        command_template = jinja2.Environment(autoescape=True).from_string(command)

        binds.update(**settings.flatten())
        binded = command_template.render(**binds)
        client.connect(
            hostname=settings.TARGET.SSH_HOST,
            port=settings.TARGET.SSH_PORT,
            username=settings.TARGET.SSH_USERNAME,
            password=settings.TARGET.SSH_PASSWORD,
        )
        _stdin, _stdout, _stderr = client.exec_command(binded)

        # # TODO: add schema for stdin/stdout
        # if _stderr:
        #     return _stderr.read(256).decode()
        # return _stdout.read(256).decode()


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
