__all__ = ["router"]

import datetime
from typing import Any, Annotated

from fastapi import APIRouter
from fastapi import BackgroundTasks
from pydantic import BaseModel, ConfigDict

from src.api.dependencies import DEPENDS_ALERT_REPOSITORY, DEPENDS_VERIFIED_REQUEST, DEPENDS_BOT
from src.config import settings, Target
from src.modules.alerts.repository import AbstractAlertRepository
from src.modules.alerts.schemas import AlertDB, MappedAlert
from src.modules.auth.schemas import VerificationResult

router = APIRouter(prefix="/alerts", tags=["Alerts"])


class AlertManagerRequest(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
                "receiver": "webhook-critical",
                "status": "firing",
                "alerts": [
                    {
                        "status": "firing",
                        "labels": {
                            "alertname": "high_connections",
                            "instance": "postgres_exporter:9187",
                            "job": "postgres",
                            "severity": "critical",
                        },
                        "annotations": {
                            "description": "A Prometheus target has disappeared. An exporter might be crashed.",
                            "summary": "Prometheus target missing (instance postgres_exporter:9187)",
                        },
                        "startsAt": "2023-11-04T11:40:04.807+03:00",
                        "endsAt": "0001-01-01T00:00:00Z",
                        "generatorURL": "http://ec694b615a13:9090/graph?g0.expr=up+%3D%3D+0\\u0026g0.tab=1",
                        "fingerprint": "1b0137ea1b8c08b6",
                    }
                ],
                "groupLabels": {"alertname": "PrometheusTargetMissing"},
                "commonLabels": {
                    "alertname": "PrometheusTargetMissing",
                    "instance": "postgres_exporter:9187",
                    "job": "postgres",
                    "severity": "critical",
                },
                "commonAnnotations": {
                    "description": "A Prometheus target has disappeared. An exporter might be crashed. VALUE = 0  "
                    "LABELS:"
                    "map[__name__:up instance:postgres_exporter:9187 job:postgres]",
                    "summary": "Prometheus target missing (instance postgres_exporter:9187)",
                },
                "externalURL": "http://b16f1e84e073:9093",
                "version": "4",
                "groupKey": '{}:{alertname="PrometheusTargetMissing"}',
                "truncatedAlerts": 0,
            }
        },
    )

    receiver: str
    status: str
    alerts: list[dict[str, Any]]


@router.post("/alertmanager-callback", status_code=200)
async def webhook(
    alert_repository: Annotated[AbstractAlertRepository, DEPENDS_ALERT_REPOSITORY],
    data: AlertManagerRequest,
    _verification: Annotated[VerificationResult, DEPENDS_BOT],
    background_tasks: BackgroundTasks,
):
    for alert in data.alerts:
        # get alertname
        alert_alias = alert["labels"]["alertname"]
        # get timestamp from iso
        timestamp = datetime.datetime.fromisoformat(alert["startsAt"])
        # resolve multiple targets
        try:
            target_alias = alert["labels"]["target"]
            target: Target = settings.TARGETS[target_alias]
            receivers = target.ADMINS

            # save alert
            mapped_alert = await alert_repository.create_alert(
                alert=AlertDB(
                    target_alias=target_alias,
                    alias=alert_alias,
                    timestamp=timestamp,
                    value=alert,
                )
            )
            # start mailing
            await alert_repository.start_delivery(mapped_alert.id, receivers)
            if settings.SMTP_ENABLED and mapped_alert.severity == "critical":
                from src.api.dependencies import Dependencies

                smtp_repository = Dependencies.get_smtp_repository()

                for email in target.EMAILS:
                    # send email
                    background_tasks.add_task(
                        smtp_repository.send_alert_message,
                        email=email,
                        mapped_alert=mapped_alert,
                    )

        except KeyError:
            continue


@router.get("/by-id/{alert_id}", status_code=200)
async def get_alert(
    alert_repository: Annotated[AbstractAlertRepository, DEPENDS_ALERT_REPOSITORY],
    alert_id: int,
    _verification: Annotated[VerificationResult, DEPENDS_VERIFIED_REQUEST],
) -> MappedAlert:
    return await alert_repository.get_alert(alert_id)


class GroupedDelivery(MappedAlert):
    receivers: list[int]


@router.get("/delivery", status_code=200)
async def check_delivery(
    alert_repository: Annotated[AbstractAlertRepository, DEPENDS_ALERT_REPOSITORY],
    _verificated: Annotated[VerificationResult, DEPENDS_BOT],
    age: int = 3600,
) -> list[GroupedDelivery]:
    starting = datetime.datetime.utcnow() - datetime.timedelta(seconds=age)

    deliveries = await alert_repository.check_delivery(starting)
    deliveries.sort(key=lambda x: x.alert_id)
    from itertools import groupby

    grouped = groupby(deliveries, lambda x: x.alert_id)

    grouped_delivery = []

    for alert_id, group in grouped:
        mapped_alert = await alert_repository.get_alert(alert_id)
        grouped_delivery.append(GroupedDelivery(receivers=[x.receiver_id for x in group], **mapped_alert.model_dump()))

    return grouped_delivery


class Finish(BaseModel):
    alert_id: int
    receivers: list[int]


@router.post("/finish", status_code=200)
async def finish_delivery(
    alert_repository: Annotated[AbstractAlertRepository, DEPENDS_ALERT_REPOSITORY],
    _verificated: Annotated[VerificationResult, DEPENDS_BOT],
    finish: Finish,
):
    await alert_repository.stop_delivery(finish.alert_id, finish.receivers)
