__all__ = ["TokenRepository"]

from hmac import compare_digest

from src.config import settings
from src.repositories.tokens.abc import AbstractTokenRepository


class TokenRepository(AbstractTokenRepository):

    @classmethod
    def verify_bot_token(cls, token: str) -> bool:
        return compare_digest(token, settings.BOT_TOKEN.get_secret_value())
