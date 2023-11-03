from typing import Annotated

from fastapi import BackgroundTasks

from src.app.dependencies import DEPENDS_CURRENT_USER_ID, DEPENDS_BOT
from src.app.dependencies import DEPENDS_SMTP_REPOSITORY, DEPENDS_USER_REPOSITORY
from src.app.users import router
from src.exceptions import (
    IncorrectCredentialsException,
    NoCredentialsException,
)
from src.repositories.smtp.abc import AbstractSMTPRepository
from src.repositories.users import AbstractUserRepository
from src.schemas.users import ViewUser


@router.get(
    "/me",
    responses={
        200: {"description": "Current user info"},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def get_me(
    user_id: Annotated[int, DEPENDS_CURRENT_USER_ID],
    user_repository: Annotated[AbstractUserRepository, DEPENDS_USER_REPOSITORY],
) -> ViewUser:
    """
    Get current user info if authenticated
    """
    user = await user_repository.read(user_id)
    user: ViewUser
    return user


@router.get(
    "/{user_id}",
    responses={
        200: {"description": "User info"},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def get_user(
    user_id: int,
    _verify_bot: Annotated[bool, DEPENDS_BOT],
    user_repository: Annotated[AbstractUserRepository, DEPENDS_USER_REPOSITORY],
) -> ViewUser:
    """
    Get user info
    """
    user = await user_repository.read(user_id)
    user: ViewUser
    return user


# TODO: Add registration with Telegram


@router.get("/connect-email", tags=["Email"])
async def connect_email(
    email: str,
    user_id: int,
    background_tasks: BackgroundTasks,
    smtp_repository: Annotated[AbstractSMTPRepository, DEPENDS_SMTP_REPOSITORY],
    _verify_bot: Annotated[bool, DEPENDS_BOT],
    user_repository: Annotated[AbstractUserRepository, DEPENDS_USER_REPOSITORY],
):
    """
    Start registration via email
    """

    email_flow = await user_repository.start_connect_email(user_id, email)
    background_tasks.add_task(smtp_repository.send_connect_email, email_flow.email, email_flow.auth_code)


@router.post("/connect-email/finish", tags=["Email"])
async def finish_connect_email(
    email: str,
    auth_code: str,
    user_repository: Annotated[AbstractUserRepository, DEPENDS_USER_REPOSITORY],
):
    """
    Finish registration via email
    """
    await user_repository.finish_connect_email(email=email, auth_code=auth_code)
