__all__ = ["TokenRepository"]

from hmac import compare_digest

from src.config import settings
from src.repositories.tokens.abc import AbstractTokenRepository
from src.schemas.tokens import VerificationResult


class TokenRepository(AbstractTokenRepository):
    @classmethod
    def verify_bot_token(cls, auth_token: str) -> VerificationResult:
        split_by_colon = auth_token.split(":")
        if len(split_by_colon) == 3:
            user_id, bot_token, _ = split_by_colon
            user_id = int(user_id)
            bot_token += _
        else:
            user_id = None
            bot_token = auth_token

        success = compare_digest(bot_token, settings.BOT_TOKEN.get_secret_value())

        return VerificationResult(success=success, user_id=user_id)
