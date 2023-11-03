from typing import Annotated, Optional

from src.app.dependencies import DEPENDS_BOT, DEPENDS_PG_STAT_REPOSITORY
from src.app.pg import router
from src.exceptions import (
    IncorrectCredentialsException,
    NoCredentialsException,
)
from src.repositories.pg import AbstractPgRepository
from src.schemas.pg_stats import ViewPgStatActivity, ViewPgStatActivitySummary, PgStat

from pydantic import BaseModel, ConfigDict


class PgStatActivityResult(BaseModel):
    class Meta(BaseModel):
        total_backends_count: int

    meta: Meta
    backends: list[ViewPgStatActivity]


class PgTerminateSessionResult(BaseModel):
    success: bool
    detail: str = None


class PgStatActivitySummaryResult(BaseModel):
    model_config = ConfigDict()

    success: bool
    detail: str = None
    process_count_by_state: Optional[ViewPgStatActivitySummary] = None


@router.get(
    "/terminate-session",
    responses={
        200: {"description": "Terminate session by pid"},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def terminate_session(
    # user_id: int,
    pid: int,
    _verify_bot: Annotated[bool, DEPENDS_BOT],
    # user_repository: Annotated[AbstractUserRepository, DEPENDS_USER_REPOSITORY],
    pg_repository: Annotated[AbstractPgRepository, DEPENDS_PG_STAT_REPOSITORY],
) -> PgTerminateSessionResult:
    # _user = await user_repository.read(user_id)
    success = await pg_repository.terminate_pg_backend(pid)

    if not success:
        return PgTerminateSessionResult(success=success, detail=f"Impossible to kill session with PID {pid}.")
    return PgTerminateSessionResult(success=success)


@router.get(
    "/stat-summary",
    responses={
        200: {"description": "Current database statistics summary"},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def get_statistics_summary(
    # user_id: int,
    _verify_bot: Annotated[bool, DEPENDS_BOT],
    # user_repository: Annotated[AbstractUserRepository, DEPENDS_USER_REPOSITORY],
    pg_repository: Annotated[AbstractPgRepository, DEPENDS_PG_STAT_REPOSITORY],
) -> PgStatActivitySummaryResult:
    # _user = await user_repository.read(user_id)
    pg_stat_activity = await pg_repository.read_pg_stat_summary()

    if pg_stat_activity:
        return PgStatActivitySummaryResult(success=True, process_count_by_state=pg_stat_activity)

    return PgStatActivitySummaryResult(success=False, detail="No data found")


@router.get(
    "/stat-{stat_name}",
    responses={
        200: {"description": "Current database statistics by name"},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def get_statistics(
    # user_id: int,
    _verify_bot: Annotated[bool, DEPENDS_BOT],
    # user_repository: Annotated[AbstractUserRepository, DEPENDS_USER_REPOSITORY],
    pg_repository: Annotated[AbstractPgRepository, DEPENDS_PG_STAT_REPOSITORY],
    limit: int = 20,
    stat_name: PgStat = PgStat.pg_stat_activity,
) -> list[dict]:
    """
    Return rows from pg_stat view

    See more about views:
    https://www.postgresql.org/docs/current/monitoring-stats.html#MONITORING-PG-STAT-ACTIVITY-VIEW
    """
    # _user = await user_repository.read(user_id)
    pg_stat_activity = await pg_repository.read_pg_stat(pg_stat_name=stat_name, limit=limit)

    objects = []
    for r in pg_stat_activity:
        _ = dict()
        # translate to dict[str, str]
        for k, v in r.items():
            key = str(k)
            if v is None:
                _[key] = None
            elif isinstance(v, (bool, int, float)):
                _[key] = v
            else:
                _[key] = str(v)
        objects.append(_)
    return objects
