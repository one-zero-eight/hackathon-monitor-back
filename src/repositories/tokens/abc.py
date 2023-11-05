__all__ = ["AbstractTokenRepository"]

from abc import ABCMeta

from src.schemas.tokens import VerificationResult


class AbstractTokenRepository(metaclass=ABCMeta):
    @classmethod
    def verify_bot_token(cls, token: str) -> VerificationResult:
        raise NotImplementedError()
