from typing import Annotated

from src.app.dependencies import DEPENDS_USER_REPOSITORY, DEPENDS_BOT
from src.app.pg import router
from src.exceptions import (
    IncorrectCredentialsException,
    NoCredentialsException,
)
from src.repositories.users import AbstractUserRepository


@router.get(
    "/pg-stat-activity",
    responses={
        200: {"description": "Current database statistics"},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def get_statistics(
    user_id: int,
    _verify_bot: Annotated[bool, DEPENDS_BOT],
    user_repository: Annotated[AbstractUserRepository, DEPENDS_USER_REPOSITORY],
):
    _user = await user_repository.read(user_id)
    # TODO: Add statistics


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
