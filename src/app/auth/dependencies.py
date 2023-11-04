__all__ = ["get_current_user_id", "verify_bot_token", "verify_webapp"]

from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, APIKeyCookie

from src.app.auth.telegram import telegram_check_authorization, TelegramWidgetData
from src.config import settings
from src.exceptions import NoCredentialsException, IncorrectCredentialsException
from src.repositories.tokens import TokenRepository

bearer_scheme = HTTPBearer(
    scheme_name="Bearer",
    description="Your JSON Web Token (JWT)",
    bearerFormat="JWT",
    auto_error=False,  # We'll handle error manually
)

cookie_scheme = APIKeyCookie(
    scheme_name="Cookie",
    description="Your JSON Web Token (JWT) stored as 'token' cookie",
    name=settings.COOKIE.NAME,  # Cookie name
    auto_error=False,  # We'll handle error manually
)


async def get_access_token(
    bearer: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    cookie: str = Depends(cookie_scheme),
) -> Optional[str]:
    # Prefer header to cookie
    if bearer and bearer.credentials:
        return bearer.credentials
    elif cookie:
        return cookie


async def verify_bot_token(
    token: Optional[str] = Depends(get_access_token),
) -> bool:
    """
    :raises NoCredentialsException: if token is not provided
    :raises IncorrectCredentialsException: if token is invalid
    :param token: JWT token from header or cookie
    :return: True if token is valid
    """
    if not token:
        raise NoCredentialsException()

    if not TokenRepository.verify_bot_token(token):
        raise IncorrectCredentialsException()

    return True


def verify_webapp(
    telegram_data: TelegramWidgetData,
) -> bool:
    """
    Verify telegram data

    https://core.telegram.org/widgets/login#checking-authorization
    :raises IncorrectCredentialsException: if hash is invalid
    """
    if not telegram_check_authorization(telegram_data):
        raise IncorrectCredentialsException()

    return True


async def get_current_user_id(
    token: Optional[str] = Depends(get_access_token),
) -> int:
    """
    :raises NoCredentialsException: if token is not provided
    :param token: JWT token from header or cookie
    :return: user id
    """

    if not token:
        raise NoCredentialsException()

    token_data = await TokenRepository.verify_user_token(token)
    return token_data.user_id
