__all__ = ["ViewUser", "CreateUser", "ViewEmailFlow"]

from typing import Optional

from pydantic import BaseModel, ConfigDict


class ViewUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: Optional[str]
    email_verified: Optional[bool]
    name: str


class CreateUser(BaseModel):
    name: str


class ViewEmailFlow(BaseModel):
    email: str
    auth_code: str
    user_id: int
