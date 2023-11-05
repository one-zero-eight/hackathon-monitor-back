from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict

from src.app.dependencies import DEPENDS_BOT, DEPENDS_PG_STAT_REPOSITORY
from src.app.pg import router
from src.exceptions import (
    IncorrectCredentialsException,
    NoCredentialsException,
)
from src.repositories.pg import AbstractPgRepository
from src.schemas.pg_stats import ViewPgStatActivitySummary
from src.schemas.tokens import VerificationResult


class PgStatActivitySummaryResult(BaseModel):
    model_config = ConfigDict()

    success: bool
    detail: str = None
    process_count_by_state: Optional[ViewPgStatActivitySummary] = None


@router.get(
    "/stat-summary",
    responses={
        200: {"description": "Current database statistics summary"},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def get_statistics_summary(
    _verification: Annotated[VerificationResult, DEPENDS_BOT],
    pg_repository: Annotated[AbstractPgRepository, DEPENDS_PG_STAT_REPOSITORY],
) -> PgStatActivitySummaryResult:
    pg_stat_activity = await pg_repository.read_pg_stat_summary()

    if pg_stat_activity:
        return PgStatActivitySummaryResult(success=True, process_count_by_state=pg_stat_activity)

    return PgStatActivitySummaryResult(success=False, detail="No data found")


@router.get(
    "/targets",
    responses={
        200: {"description": "Available targets aliases"},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def targets(
    _verification: Annotated[VerificationResult, DEPENDS_BOT],
    pg_repository: Annotated[AbstractPgRepository, DEPENDS_PG_STAT_REPOSITORY],
) -> list[str]:
    return await pg_repository.fetch_targets()
