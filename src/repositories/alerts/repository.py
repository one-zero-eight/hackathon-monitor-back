import datetime

from sqlalchemy import insert, select, update, and_, not_
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.alerts.abc import AbstractAlertRepository
from src.schemas.alerts import AlertDB, MappedAlert, AlertDeliveryScheme
from src.storages.monitoring.config import settings as monitoring_settings
from src.storages.sqlalchemy import AbstractSQLAlchemyStorage
from src.storages.sqlalchemy.models.alerts import Alert, AlertDelivery


def map_alert(alert: AlertDB, id_: int) -> MappedAlert:
    configurated_alerts = monitoring_settings.alerts

    json_ = alert.value

    configurated = configurated_alerts.get(alert.alias)
    if configurated:
        status = json_["status"]
        description = configurated.description

        if annotations := json_.get("annotations"):
            if _description := annotations.get("description"):
                description = _description
        return MappedAlert(
            id=id_,
            status=status,
            target_alias=alert.target_alias,
            alias=alert.alias,
            title=configurated.title,
            description=description,
            severity=configurated.severity,
            value=alert.value,
            timestamp=alert.timestamp,
            suggested_actions=configurated.suggested_actions,
            related_views=configurated.related_views,
        )
    else:
        from_json = {"status": json_["status"]}

        if annotations := json_.get("annotations"):
            if title := annotations.get("title"):
                from_json["title"] = title
            if description := annotations.get("description"):
                from_json["description"] = description

        if labels := json_.get("labels"):
            if severity := labels.get("severity"):
                from_json["severity"] = severity

        return MappedAlert(
            id=id_,
            target_alias=alert.target_alias,
            alias=alert.alias,
            value=alert.value,
            timestamp=alert.timestamp,
            **from_json,
        )


class AlertRepository(AbstractAlertRepository):
    def __init__(self, storage: AbstractSQLAlchemyStorage):
        self.storage = storage

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()

    async def check_delivery(self, starting: datetime.datetime) -> list["AlertDeliveryScheme"]:
        async with self._create_session() as session:
            q = select(AlertDelivery).where(not_(AlertDelivery.delivered))
            result = await session.scalars(q)
            if result:
                deliveries = [AlertDeliveryScheme.model_validate(r, from_attributes=True) for r in result]

                alert_ids = {d.alert_id for d in deliveries}
                q = select(Alert).where(and_(Alert.id.in_(alert_ids), Alert.timestamp >= starting))
                filtered = await session.scalars(q)
                target_alerts = {r.id for r in filtered}

                return [d for d in deliveries if d.alert_id in target_alerts]

            else:
                return []

    async def create_alert(self, alert: "AlertDB") -> MappedAlert:
        async with self._create_session() as session:
            statement = insert(Alert).values(**alert.model_dump()).returning(Alert.id)
            id_ = await session.scalar(statement)
            await session.commit()
            return map_alert(alert, id_)

    async def get_alert(self, alert_id: int) -> MappedAlert:
        async with self._create_session() as session:
            q = select(Alert).where(Alert.id == alert_id)
            alert = await session.scalar(q)
            if alert:
                scheme = AlertDB.model_validate(alert, from_attributes=True)
                return map_alert(scheme, alert_id)

    async def start_delivery(self, alert_id: int, receivers: list[int]) -> list[int]:
        async with self._create_session() as session:
            q = select(AlertDelivery).where(AlertDelivery.alert_id == alert_id)
            existing = await session.scalars(q)
            if existing:
                existing_ids = {r.alert_id for r in existing}
                existing_ids &= set(receivers)
                statement = (
                    update(AlertDelivery).where(AlertDelivery.alert_id.in_(existing_ids)).values(delivered=False)
                )
                await session.execute(statement)
                await session.commit()
            else:
                existing_ids = set()

            not_existing_ids = set(receivers) - existing_ids
            if not_existing_ids:
                statement = insert(AlertDelivery).values(
                    [{"alert_id": alert_id, "receiver_id": receiver_id} for receiver_id in not_existing_ids]
                )
                await session.execute(statement)
                await session.commit()

            q = select(AlertDelivery).where(and_(AlertDelivery.alert_id == alert_id, not_(AlertDelivery.delivered)))
            to_be_delivered = await session.scalars(q)
            return [r.receiver_id for r in to_be_delivered]

    async def stop_delivery(self, alert_id: int, receivers: list[int]):
        async with self._create_session() as session:
            q = select(AlertDelivery).where(
                and_(
                    AlertDelivery.alert_id == alert_id,
                    not_(AlertDelivery.delivered),
                    AlertDelivery.receiver_id.in_(receivers),
                )
            )
            to_be_updated = await session.scalars(q)
            if to_be_updated:
                statement = (
                    update(AlertDelivery)
                    .where(AlertDelivery.id.in_([r.id for r in to_be_updated]))
                    .values(delivered=True)
                )
                await session.execute(statement)
                await session.commit()
