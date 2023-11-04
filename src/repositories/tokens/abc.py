__all__ = ["AbstractTokenRepository"]

from abc import ABCMeta


class AbstractTokenRepository(metaclass=ABCMeta):

    @classmethod
    def verify_bot_token(cls, token: str) -> bool:
        raise NotImplementedError()
