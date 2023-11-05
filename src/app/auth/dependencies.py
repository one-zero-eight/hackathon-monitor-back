__all__ = ["verify_bot_token", "verify_webapp", "verify_request"]

from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import ValidationError

from src.app.auth.telegram import telegram_webapp_check_authorization, TelegramWidgetData
from src.exceptions import NoCredentialsException, IncorrectCredentialsException
from src.repositories.tokens import TokenRepository
from src.schemas.tokens import VerificationResult

bearer_scheme = HTTPBearer(
    scheme_name="Bearer",
    description="Your JSON Web Token (JWT)",
    bearerFormat="JWT",
    auto_error=False,  # We'll handle error manually
)


async def get_access_token(
    bearer: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Optional[str]:
    # Prefer header to cookie
    if bearer:
        return bearer.credentials


async def verify_request(
    bearer: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> VerificationResult:
    """
    Check one of the following:
    - Bearer token from header with BOT_TOKEN
    - Bearer token from header with webapp data
    :raises NoCredentialsException: if token is not provided
    :raises IncorrectCredentialsException: if token is invalid
    """

    if not bearer:
        raise NoCredentialsException()

    bot_verification_result = TokenRepository.verify_bot_token(bearer.credentials)

    if bot_verification_result.success:
        return bot_verification_result

    try:
        telegram_data = TelegramWidgetData.parse_from_string(bearer.credentials)
    except ValidationError:
        raise IncorrectCredentialsException()

    webapp_verification_result = telegram_webapp_check_authorization(telegram_data)

    if webapp_verification_result.success:
        return webapp_verification_result

    raise IncorrectCredentialsException()


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
    bearer: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> bool:
    """
    Verify telegram data

    https://core.telegram.org/widgets/login#checking-authorization
    :raises IncorrectCredentialsException: if hash is invalid
    """

    if not bearer:
        raise NoCredentialsException()

    telegram_data = TelegramWidgetData.parse_from_string(bearer.credentials)

    if not telegram_webapp_check_authorization(telegram_data):
        raise IncorrectCredentialsException()

    return True
