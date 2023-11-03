from typing import Annotated

from src.app.dependencies import DEPENDS_USER_REPOSITORY, DEPENDS_BOT, DEPENDS_PG_STAT_REPOSITORY
from src.app.pg import router
from src.exceptions import (
    IncorrectCredentialsException,
    NoCredentialsException,
)
from src.repositories.users import AbstractUserRepository
from src.repositories.pg_stats import AbstractPgStatRepository
from src.schemas.pg_stats import ViewPgStatActivity


@router.get(
    "/pg-stat-activity",
    responses={
        200: {"description": "Current database statistics"},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def get_statistics(
    # user_id: int,
    _verify_bot: Annotated[bool, DEPENDS_BOT],
    # user_repository: Annotated[AbstractUserRepository, DEPENDS_USER_REPOSITORY],
    pg_stats_repository: Annotated[AbstractPgStatRepository, DEPENDS_PG_STAT_REPOSITORY],
    limit: int = 20,
) -> list[ViewPgStatActivity]:
    # _user = await user_repository.read(user_id)
    pg_stat_activity = await pg_stats_repository.read_pg_stat_activity(limit=limit)
    pg_stat_activity: ViewPgStatActivity
    return pg_stat_activity


@router.get(
    "/kill-session",
    responses={
        200: {"description": "Kill session by pid"},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def kill_session(
    user_id: int,
    pid: int,  # noqa
    _verify_bot: Annotated[bool, DEPENDS_BOT],
    user_repository: Annotated[AbstractUserRepository, DEPENDS_USER_REPOSITORY],
):
    _user = await user_repository.read(user_id)
    # TODO: Add kill session
