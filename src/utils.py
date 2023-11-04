import logging
import re
from pathlib import Path

import httpx
import yaml
from fastapi.routing import APIRoute

from src.config import settings
from src.repositories.alerts import AlertRepository
from src.storages.monitoring.config import Alert


async def setup_repositories():
    from src.repositories.users import UserRepository
    from src.repositories.pg import PgRepository
    from src.storages.sqlalchemy import SQLAlchemyStorage
    from src.repositories.smtp import SMTPRepository
    from src.app.dependencies import Dependencies

    # ------------------- Repositories Dependencies -------------------
    storage = SQLAlchemyStorage.from_url(settings.DB_URL.get_secret_value())
    user_repository = UserRepository(storage)
    alert_repository = AlertRepository(storage)
    target_storage = SQLAlchemyStorage.from_url(settings.TARGET.DB_URL.get_secret_value())
    pg_stat = PgRepository(target_storage)

    Dependencies.set_storage(storage)
    Dependencies.set_user_repository(user_repository)
    Dependencies.set_pg_stat_repository(pg_stat)
    Dependencies.set_alert_repository(alert_repository)

    if settings.SMTP.ENABLE:
        smtp_repository = SMTPRepository()
        Dependencies.set_smtp_repository(smtp_repository)

    # await storage.create_all()


def generate_unique_operation_id(route: APIRoute) -> str:
    # Better names for operationId in OpenAPI schema.
    # It is needed because clients generate code based on these names.
    # Requires pair (tag name + function name) to be unique.
    # See fastapi.utils:generate_unique_id (default implementation).
    operation_id = f"{route.tags[0]}_{route.name}".lower()
    operation_id = re.sub(r"\W+", "_", operation_id)
    return operation_id


async def generate_prometheus_alert_rules(alerts: dict[str, Alert], path: Path, url: str):
    # Generate config
    rules = []
    for alias, alert in alerts.items():
        rules.append(
            {
                "alert": alias,
                "expr": alert.rule.expr,
                "for": alert.rule.for_,
            }
        )
    rules_config = {"groups": [{"name": "db", "rules": rules}]}

    # Dump to string and check if file has changed
    rules_config = yaml.safe_dump(rules_config, sort_keys=False)
    if path.exists() and path.read_text() == rules_config:
        logging.info("Prometheus alert rules has not changed")
        return

    # Write to file and reload Prometheus
    logging.warning("Prometheus alert rules has changed. Reloading Prometheus")
    path.write_text(rules_config)
    async with httpx.AsyncClient() as client:
        await client.post(url + "/-/reload")
