import datetime
from typing import Any, Annotated, Optional

from pydantic import BaseModel, ConfigDict

from src.app.alerts import router
from src.app.dependencies import DEPENDS_ALERT_REPOSITORY
from src.config import settings
from src.repositories.alerts import AbstractAlertRepository
from src.schemas.alerts import AlertDB, AlertDeliveryScheme, MappedAlert


class AlertManagerRequest(BaseModel):
    model_config = ConfigDict(extra="allow", json_schema_extra={"example": {
        "receiver": "webhook-critical",
        "status": "firing",
        "alerts": [
            {
                "status": "firing",
                "labels": {
                    "alertname": "high_connections",
                    "instance": "postgres_exporter:9187",
                    "job": "postgres",
                    "severity": "critical"
                },
                "annotations": {
                    "description": "A Prometheus target has disappeared. An exporter might be crashed. VALUE = 0  LABELS: map[__name__:up instance:postgres_exporter:9187 job:postgres]",
                    "summary": "Prometheus target missing (instance postgres_exporter:9187)"
                },
                "startsAt": "2023-11-04T11:40:04.807+03:00",
                "endsAt": "0001-01-01T00:00:00Z",
                "generatorURL": "http://ec694b615a13:9090/graph?g0.expr=up+%3D%3D+0\\u0026g0.tab=1",
                "fingerprint": "1b0137ea1b8c08b6"
            }
        ],
        "groupLabels": {
            "alertname": "PrometheusTargetMissing"
        },
        "commonLabels": {
            "alertname": "PrometheusTargetMissing",
            "instance": "postgres_exporter:9187",
            "job": "postgres",
            "severity": "critical"
        },
        "commonAnnotations": {
            "description": "A Prometheus target has disappeared. An exporter might be crashed. VALUE = 0  LABELS: map[__name__:up instance:postgres_exporter:9187 job:postgres]",
            "summary": "Prometheus target missing (instance postgres_exporter:9187)"
        },
        "externalURL": "http://b16f1e84e073:9093",
        "version": "4",
        "groupKey": "{}:{alertname=\"PrometheusTargetMissing\"}",
        "truncatedAlerts": 0
    }
    })

    receiver: str
    status: str
    alerts: list[dict[str, Any]]


@router.post("/alertmanager-callback", status_code=200)
async def webhook(
    alert_repository: Annotated[AbstractAlertRepository, DEPENDS_ALERT_REPOSITORY],
    data: AlertManagerRequest,
):
    receivers = settings.TARGET.RECEIVERS

    for alert in data.alerts:
        # get alertname
        alert_alias = alert["labels"]["alertname"]
        # get timestamp from iso
        timestamp = datetime.datetime.fromisoformat(alert["startsAt"])
        # jsonify alert
        # save alert
        mapped_alert = await alert_repository.create_alert(
            AlertDB(
                alias=alert_alias,
                timestamp=timestamp,
                value=alert,
            )
        )
        # start mailing
        await alert_repository.start_delivery(mapped_alert.id, receivers)


@router.get("/by-id/{alert_id}", status_code=200)
async def get_alert(
    alert_repository: Annotated[AbstractAlertRepository, DEPENDS_ALERT_REPOSITORY],
    alert_id: int,
) -> MappedAlert:
    return await alert_repository.get_alert(alert_id)


@router.get("/delivery", status_code=200)
async def check_delivery(
    alert_repository: Annotated[AbstractAlertRepository, DEPENDS_ALERT_REPOSITORY],
    age: int = 3600,
) -> list[AlertDeliveryScheme]:
    starting = datetime.datetime.utcnow() - datetime.timedelta(seconds=age)
    return await alert_repository.check_delivery(starting)


class Finish(BaseModel):
    alert_id: int
    receivers: list[int]


@router.post("/finish", status_code=200)
async def finish_delivery(
    alert_repository: Annotated[AbstractAlertRepository, DEPENDS_ALERT_REPOSITORY],
    finish: Finish,
):
    await alert_repository.stop_delivery(finish.alert_id, finish.receivers)
