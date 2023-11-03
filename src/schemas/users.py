__all__ = ["ViewUser", "CreateUser", "ViewEmailFlow"]

from typing import Optional

from pydantic import BaseModel, ConfigDict


class ViewUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    telegram_id: int
    telegram_first_name: str
    telegram_last_name: Optional[str] = None
    telegram_username: Optional[str] = None

    email: Optional[str] = None
    email_verified: Optional[bool] = None


class CreateUser(BaseModel):
    telegram_first_name: str
    telegram_last_name: Optional[str] = None
    telegram_username: Optional[str] = None


class ViewEmailFlow(BaseModel):
    email: str
    auth_code: str
    user_id: int
