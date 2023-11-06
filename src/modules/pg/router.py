__all__ = ["router"]

from typing import Annotated

from fastapi import APIRouter

from src.api.dependencies import DEPENDS_BOT, DEPENDS_PG_STAT_REPOSITORY
from src.api.exceptions import (
    IncorrectCredentialsException,
    NoCredentialsException,
)
from src.modules.auth.schemas import VerificationResult
from src.modules.pg.repository import AbstractPgRepository

router = APIRouter(prefix="/pg", tags=["Postgres"])


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
