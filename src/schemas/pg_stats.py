__all__ = ["ViewPgStatActivity"]


import datetime

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


class TerminatePgBackend(BaseModel):
    pid: int


class TerminatePgBackendResult(BaseModel):
    success: bool
    detail: str = None
