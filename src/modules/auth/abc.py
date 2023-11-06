__all__ = ["AbstractTokenRepository"]

from abc import ABCMeta

from src.modules.auth.schemas import VerificationResult


class AbstractTokenRepository(metaclass=ABCMeta):
    @classmethod
    def verify_bot_token(cls, token: str) -> VerificationResult:
        raise NotImplementedError()
