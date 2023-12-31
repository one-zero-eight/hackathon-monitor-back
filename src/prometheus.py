import logging
from pathlib import Path

import httpx
import yaml

from src.config import Target, settings
from src.storages.monitoring.config import Alert, settings as monitoring_settings


async def generate_prometheus_alert_rules(alerts: dict[str, Alert], path: Path):
    # Generate config
    rules = []
    for alias, alert in alerts.items():
        rules.append(
            {
                "alert": alias,
                "expr": alert.rule.expr,
                "for": alert.rule.for_,
                "annotations": alert.rule.annotations,
            }
        )
    rules_config = {"groups": [{"name": "db", "rules": rules}]}

    # Dump to string and check if file has changed
    rules_config = yaml.safe_dump(rules_config, sort_keys=False, allow_unicode=True)
    rules_config = "# This file is generated by the application. Do not edit it manually.\n\n" + rules_config
    if path.exists() and path.read_text() == rules_config:
        logging.info("Prometheus alert rules has not changed")
        return False

    # Write to file and reload Prometheus
    logging.warning("Prometheus alert rules has changed")
    path.write_text(rules_config)
    return True


async def generate_prometheus_scrape_configs(targets: dict[str, Target], path: Path):
    # Generate scrape configs
    scrape_static_configs = []
    for alias, target in targets.items():
        scrape_static_configs.append(
            {
                "targets": [f"{target.SSH_HOST}:9187", f"{target.SSH_HOST}:9100"],
                "labels": {
                    "target": alias,
                },
            }
        )
    scrape_configs = [
        {
            "job_name": "db",
            "static_configs": scrape_static_configs,
        }
    ]

    # Read old config to preserve other options
    if path.exists():
        old_config = yaml.safe_load(path.read_text())
    else:
        old_config = {}

    # Merge old and new configs
    new_config = {**old_config, "scrape_configs": scrape_configs}

    # Dump to string and check if file has changed
    new_config = yaml.safe_dump(new_config, sort_keys=False, allow_unicode=True)
    new_config = (
        "# The 'scrape_configs' option is generated by the application. Do not edit it manually.\n\n" + new_config
    )
    if path.exists() and path.read_text() == new_config:
        logging.info("Prometheus scrape configs has not changed")
        return False

    # Write to file and reload Prometheus
    logging.warning("Prometheus scrape configs has changed")
    path.write_text(new_config)
    return True


async def generate_prometheus_configs():
    need_reload_1 = await generate_prometheus_alert_rules(
        alerts=monitoring_settings.alerts,
        path=Path(settings.PROMETHEUS.ALERT_RULES_PATH),
    )
    need_reload_2 = await generate_prometheus_scrape_configs(
        targets=settings.TARGETS,
        path=Path(settings.PROMETHEUS.PROMETHEUS_CONFIG_PATH),
    )
    if need_reload_1 or need_reload_2:
        logging.warning("Reloading Prometheus")
        async with httpx.AsyncClient() as client:
            await client.post(settings.PROMETHEUS.URL + "/-/reload")
