__all__ = [
    "DEPENDS",
    "DEPENDS_BOT",
    "DEPENDS_SMTP_REPOSITORY",
    "DEPENDS_STORAGE",
    "DEPENDS_USER_REPOSITORY",
    "DEPENDS_CURRENT_USER_ID",
    "Dependencies",
]

from fastapi import Depends

from src.repositories.smtp.abc import AbstractSMTPRepository
from src.repositories.users import AbstractUserRepository
from src.storages.sqlalchemy.storage import AbstractSQLAlchemyStorage


class Dependencies:
    _storage: "AbstractSQLAlchemyStorage"
    _user_repository: "AbstractUserRepository"
    _smtp_repository: "AbstractSMTPRepository"

    @classmethod
    def get_storage(cls) -> "AbstractSQLAlchemyStorage":
        return cls._storage

    @classmethod
    def set_storage(cls, storage: "AbstractSQLAlchemyStorage"):
        cls._storage = storage

    @classmethod
    def get_user_repository(cls) -> "AbstractUserRepository":
        return cls._user_repository

    @classmethod
    def set_user_repository(cls, user_repository: "AbstractUserRepository"):
        cls._user_repository = user_repository

    @classmethod
    def get_smtp_repository(cls) -> "AbstractSMTPRepository":
        return cls._smtp_repository

    @classmethod
    def set_smtp_repository(cls, smtp_repository: "AbstractSMTPRepository"):
        cls._smtp_repository = smtp_repository


DEPENDS = Depends(lambda: Dependencies)
"""It's a dependency injection container for FastAPI.
See `FastAPI docs <(https://fastapi.tiangolo.com/tutorial/dependencies/)>`_ for more info"""
DEPENDS_STORAGE = Depends(Dependencies.get_storage)
DEPENDS_USER_REPOSITORY = Depends(Dependencies.get_user_repository)
DEPENDS_SMTP_REPOSITORY = Depends(Dependencies.get_smtp_repository)

from src.app.auth.dependencies import get_current_user_id, verify_bot_token  # noqa: E402

DEPENDS_BOT = Depends(verify_bot_token)
DEPENDS_CURRENT_USER_ID = Depends(get_current_user_id)
