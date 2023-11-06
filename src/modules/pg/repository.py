import datetime
from typing import Optional, Any

import jinja2
import paramiko
from paramiko.ssh_exception import SSHException
from sqlalchemy import Row
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text

from src.api.exceptions import SQLQueryError, SSHQueryError
from src.config import settings, Target
from src.modules.pg.abc import AbstractPgRepository
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

    async def execute_sql(self, sql: str, binds: dict[str, Any], target: Target) -> None:
        engine = create_async_engine(target.DB_URL.get_secret_value(), pool_recycle=3600)

        try:
            async with engine.connect() as session:
                statement = text(sql)
                # get all params from statement
                params = statement.compile().params
                binds = {k: v for k, v in binds.items() if k in params}
                statement = statement.bindparams(**binds)
                try:
                    await session.execute(statement)
                except DBAPIError as e:
                    raise SQLQueryError(str(e))
                await session.commit()
        except ConnectionRefusedError as e:
            raise SQLQueryError(str(e))

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
            try:
                r = await session.execute(statement)
            except DBAPIError as e:
                raise SQLQueryError(str(e))
            table_rows = r.fetchall()
            return table_rows_to_list_of_dicts(list(table_rows))

    async def execute_ssh(self, command: str, binds: dict[str, Any], target: Target) -> None:
        client = paramiko.client.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        command_template = jinja2.Environment(autoescape=True).from_string(command)
        target_db_url = target.DB_URL.get_secret_value()
        target_dict = {f"TARGET__{k}": v for k, v in target.model_dump().items()}
        target_dict["TARGET__DB_URL"] = target_db_url
        binds.update(**settings.flatten(), **target_dict)
        binded = command_template.render(**binds)
        try:
            client.connect(
                hostname=target.SSH_HOST,
                port=target.SSH_PORT,
                username=target.SSH_USERNAME,
                password=target.SSH_PASSWORD,
            )
        except paramiko.ssh_exception.AuthenticationException as e:
            raise SSHQueryError(str(e))
        # TODO: Think how to fetch responses better

        try:
            _stdin, _stdout, _stderr = client.exec_command(binded)
        except SSHException as e:
            print(e)
            raise SSHQueryError(str(e))

    async def fetch_targets(self) -> list[str]:
        return list(settings.TARGETS.keys())
