__all__ = [
    "DEPENDS",
    "DEPENDS_BOT",
    "DEPENDS_SMTP_REPOSITORY",
    "DEPENDS_STORAGE",
    "DEPENDS_USER_REPOSITORY",
    "DEPENDS_WEBAPP",
    "DEPENDS_PG_STAT_REPOSITORY",
    "DEPENDS_ALERT_REPOSITORY",
    "Dependencies",
]

from fastapi import Depends

from src.repositories.alerts.abc import AbstractAlertRepository
from src.repositories.pg.abc import AbstractPgRepository
from src.repositories.smtp.abc import AbstractSMTPRepository
from src.repositories.users.abc import AbstractUserRepository
from src.storages.sqlalchemy.storage import AbstractSQLAlchemyStorage


class Dependencies:
    _storage: "AbstractSQLAlchemyStorage"
    _user_repository: "AbstractUserRepository"
    _smtp_repository: "AbstractSMTPRepository"
    _pg_stat_repository: "AbstractPgRepository"
    _alert_repository: "AbstractAlertRepository"

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

    @classmethod
    def get_pg_stat_repository(cls) -> "AbstractPgRepository":
        return cls._pg_stat_repository

    @classmethod
    def set_pg_stat_repository(cls, pg_stat_repository: "AbstractPgRepository"):
        cls._pg_stat_repository = pg_stat_repository

    @classmethod
    def get_alert_repository(cls) -> "AbstractAlertRepository":
        return cls._alert_repository

    @classmethod
    def set_alert_repository(cls, alert_repository: "AbstractAlertRepository"):
        cls._alert_repository = alert_repository


DEPENDS = Depends(lambda: Dependencies)
"""It's a dependency injection container for FastAPI.
See `FastAPI docs <(https://fastapi.tiangolo.com/tutorial/dependencies/)>`_ for more info"""
DEPENDS_STORAGE = Depends(Dependencies.get_storage)
DEPENDS_USER_REPOSITORY = Depends(Dependencies.get_user_repository)
DEPENDS_SMTP_REPOSITORY = Depends(Dependencies.get_smtp_repository)
DEPENDS_PG_STAT_REPOSITORY = Depends(Dependencies.get_pg_stat_repository)
DEPENDS_ALERT_REPOSITORY = Depends(Dependencies.get_alert_repository)

from src.app.auth.dependencies import verify_bot_token, verify_webapp  # noqa: E402

DEPENDS_BOT = Depends(verify_bot_token)
DEPENDS_WEBAPP = Depends(verify_webapp)
