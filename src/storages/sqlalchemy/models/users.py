__all__ = ["User", "EmailFlow"]

from typing import Optional

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.storages.sqlalchemy.models.__mixin__ import IdMixin
from src.storages.sqlalchemy.models.base import Base


class User(Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(nullable=True)

    telegram_id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    telegram_first_name: Mapped[str] = mapped_column(nullable=True)
    telegram_last_name: Mapped[Optional[str]] = mapped_column(nullable=True)
    telegram_username: Mapped[Optional[str]] = mapped_column(nullable=True)

    email: Mapped[Optional[str]] = mapped_column(nullable=True)
    email_verified: Mapped[bool] = mapped_column(default=False)


class EmailFlow(Base, IdMixin):
    __tablename__ = "email_flows"

    user_id: Mapped[int] = mapped_column(ForeignKey(User.telegram_id), nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)

    user: Mapped[User] = relationship(User, backref="email_flows")

    auth_code: Mapped[str] = mapped_column(nullable=False)

    finished: Mapped[bool] = mapped_column(default=False)

    # unique constraint
    __table_args__ = (UniqueConstraint("email", "auth_code", name="email_auth_code_unique_constraint"),)
