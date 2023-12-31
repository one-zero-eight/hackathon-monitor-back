__all__ = ["router"]


from typing import Annotated

from fastapi import APIRouter
from fastapi import BackgroundTasks

from src.api.dependencies import DEPENDS_BOT
from src.api.dependencies import DEPENDS_SMTP_REPOSITORY, DEPENDS_USER_REPOSITORY
from src.config import settings
from src.api.exceptions import (
    IncorrectCredentialsException,
    NoCredentialsException,
    UserAlreadyExistsException,
)
from src.modules.smtp.abc import AbstractSMTPRepository
from src.modules.users.abc import AbstractUserRepository
from src.modules.auth.schemas import VerificationResult
from src.modules.users.schemas import ViewUser, CreateUser

router = APIRouter(prefix="/users", tags=["Users"])


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
    _verification: Annotated[VerificationResult, DEPENDS_BOT],
    user_repository: Annotated[AbstractUserRepository, DEPENDS_USER_REPOSITORY],
) -> ViewUser:
    """
    Get user info
    """
    user = await user_repository.read(user_id)
    user: ViewUser
    return user


# TODO: Add registration with Telegram
@router.post(
    "/register-via-telegram",
    tags=["Telegram"],
    responses={
        200: {"description": "Start registration via Telegram"},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def register_via_telegram(
    user: CreateUser,
    user_repository: Annotated[AbstractUserRepository, DEPENDS_USER_REPOSITORY],
    _verification: Annotated[VerificationResult, DEPENDS_BOT],
):
    """
    Registration via Telegram
    """
    existing = await user_repository.read(user.telegram_id)
    if existing:
        raise UserAlreadyExistsException()
    await user_repository.create(user)


if settings.SMTP_ENABLED:

    @router.post("/connect-email", tags=["Email"])
    async def connect_email(
        email: str,
        user_id: int,
        background_tasks: BackgroundTasks,
        smtp_repository: Annotated[AbstractSMTPRepository, DEPENDS_SMTP_REPOSITORY],
        _verification: Annotated[VerificationResult, DEPENDS_BOT],
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
