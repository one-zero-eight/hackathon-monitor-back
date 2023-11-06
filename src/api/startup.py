from src.config import settings


async def setup_repositories():
    from src.modules.alerts.repository import AlertRepository
    from src.modules.users.repository import UserRepository
    from src.modules.pg.repository import PgRepository
    from src.modules.smtp.repository import SMTPRepository
    from src.storages.sqlalchemy import SQLAlchemyStorage
    from src.api.dependencies import Dependencies

    # ------------------- Repositories Dependencies -------------------
    storage = SQLAlchemyStorage.from_url(settings.DB_URL.get_secret_value())
    user_repository = UserRepository(storage)
    alert_repository = AlertRepository(storage)
    # TODO: Add target repository
    target = list(settings.TARGETS.values())[0]

    target_storage = SQLAlchemyStorage.from_url(target.DB_URL.get_secret_value())
    pg_stat = PgRepository(target_storage)

    Dependencies.set_storage(storage)
    Dependencies.set_user_repository(user_repository)
    Dependencies.set_pg_stat_repository(pg_stat)
    Dependencies.set_alert_repository(alert_repository)

    if settings.SMTP_ENABLED:
        smtp_repository = SMTPRepository()
        Dependencies.set_smtp_repository(smtp_repository)

    # await storage.create_all()
