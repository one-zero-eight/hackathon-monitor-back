__all__ = ["ViewPgStatActivity", "ViewPgStatDatabase",
           "ViewPgStatActivitySummary", "PgStat"]

import datetime
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class ViewPgStatActivity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dataid: int | None = None
    datname: str | None = None
    pid: int | None = None
    usesysid: int | None = None
    application_name: str | None = None
    client_addr: str | None = None
    client_hostname: str | None = None
    client_port: int | None = None
    backend_start: datetime.datetime | None = None
    xact_start: datetime.datetime | None = None
    query_start: datetime.datetime | None = None
    state_change: datetime.datetime | None = None
    wait_event_type: str | None = None
    wait_event: str | None = None
    state: str | None = None
    query: str | None = None
    backend_type: str | None = None

    @field_validator("client_addr", mode="before")
    @classmethod
    def validate_ipv4(cls, val):
        return str(val)


class ViewPgStatDatabase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    datid: int | None = None
    datname: str | None = None
    numbackends: int | None = None
    xact_commit: int | None = None
    xact_rollback: int | None = None
    blks_read: int | None = None
    blks_hit: int | None = None
    tup_returned: int | None = None
    tup_fetched: int | None = None
    tup_inserted: int | None = None
    tup_updated: int | None = None
    tup_deleted: int | None = None
    conflicts: int | None = None
    temp_files: int | None = None
    temp_bytes: int | None = None
    deadlocks: int | None = None
    session_time: int | None = None
    active_time: int | None = None
    idle_in_transaction_time: int | None = None
    sessions: int | None = None
    sessions_abandoned: int | None = None
    sessions_fatal: int | None = None
    sessions_killed: int | None = None
    stats_reset: datetime.datetime | None = None


class ViewPgStatActivitySummary(BaseModel):
    active: Optional[int] = 0
    idle: Optional[int] = 0
    idle_in_transaction: Optional[int] = 0
    idle_in_transaction_aborted: Optional[int] = 0
    fastpath_function_call: Optional[int] = 0
    disabled: Optional[int] = 0
    no_state: Optional[int] = 0


class PgStat(StrEnum):
    pg_stat_activity = "activity"
    pg_stat_replication = "replication"
    pg_stat_replication_slots = "replication_slots"
    pg_stat_wal_receiver = "wal_receiver"
    pg_stat_recovery_prefetch = "recovery_prefetch"
    pg_stat_subscription = "subscription"
    pg_stat_subscription_stats = "subscription_stats"
    pg_stat_ssl = "ssl"
    pg_stat_gssapi = "gssapi"
    pg_stat_archiver = "archiver"
    pg_stat_io = "io"
    pg_stat_bgwriter = "bgwriter"
    pg_stat_wal = "wal"
    pg_stat_database = "database"
    pg_stat_database_conflicts = "database_conflicts"
    pg_stat_all_tables = "all_tables"
    pg_stat_all_indexes = "all_indexes"
    pg_statio_all_tables = "statio_all_tables"
    pg_statio_all_indexes = "statio_all_indexes"
    pg_statio_all_sequences = "statio_all_sequences"
    pg_stat_user_functions = "user_functions"
    pg_stat_slru = "slru"
