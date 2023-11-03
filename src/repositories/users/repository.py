__all__ = ["UserRepository"]

import random
from typing import Optional

from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import UserNotFound, EmailFlowNotFound, UserAlreadyHasEmail
from src.repositories.users.abc import AbstractUserRepository
from src.schemas.users import ViewUser, CreateUser, ViewEmailFlow
from src.storages.sqlalchemy.models.users import User, EmailFlow
from src.storages.sqlalchemy.storage import AbstractSQLAlchemyStorage

MIN_USER_ID = 100_000
MAX_USER_ID = 999_999


def _generate_auth_code() -> str:
    # return random 6-digit code
    return str(random.randint(100_000, 999_999))


async def _get_available_user_ids(session: AsyncSession, count: int = 1) -> list[int] | int:
    q = select(User.telegram_id)
    excluded_ids = set(await session.scalars(q))
    excluded_ids: set[int]
    available_ids = set()
    while len(available_ids) < count:
        chosen_id = random.randint(MIN_USER_ID, MAX_USER_ID)
        if chosen_id not in excluded_ids:
            available_ids.add(chosen_id)
    return list(available_ids) if count > 1 else available_ids.pop()


class UserRepository(AbstractUserRepository):
    storage: AbstractSQLAlchemyStorage

    def __init__(self, storage: AbstractSQLAlchemyStorage):
        self.storage = storage

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()

    # ------------------ CRUD ------------------ #

    async def create(self, user: CreateUser) -> ViewUser:
        async with self._create_session() as session:
            q = insert(User).values(**user.model_dump()).returning(User)
            new_user = await session.scalar(q)
            await session.commit()
            return ViewUser.model_validate(new_user)

    async def read(self, id_: int) -> Optional["ViewUser"]:
        async with self._create_session() as session:
            q = select(User).where(User.telegram_id == id_)
            user = await session.scalar(q)
            if user:
                return ViewUser.model_validate(user, from_attributes=True)

    async def read_by_email(self, email: str) -> Optional["ViewUser"]:
        async with self._create_session() as session:
            q = select(User).where(User.email == email)
            user = await session.scalar(q)
            if user:
                return ViewUser.model_validate(user, from_attributes=True)

    # ^^^^^^^^^^^^^^^^^^^ CRUD ^^^^^^^^^^^^^^^^^^^ #

    async def start_connect_email(self, user_id: int, email: str) -> "ViewEmailFlow":
        async with self._create_session() as session:
            q = select(User).where(User.telegram_id == user_id)
            _user = await session.scalar(q)
            if _user:
                if _user.email == email:
                    raise UserAlreadyHasEmail()

                q = (
                    insert(EmailFlow)
                    .values(user_id=user_id, email=email, auth_code=_generate_auth_code())
                    .returning(EmailFlow)
                )

                email_flow = await session.scalar(q)
                await session.commit()
                return ViewEmailFlow.model_validate(email_flow, from_attributes=True)
            else:
                raise UserNotFound()

    async def finish_connect_email(self, email: str, auth_code: str):
        async with self._create_session() as session:
            q = select(EmailFlow).where(EmailFlow.email == email).where(EmailFlow.auth_code == auth_code)
            email_flow = await session.scalar(q)
            if email_flow:
                q = (
                    update(User)
                    .where(User.telegram_id == email_flow.user_id)
                    .values(email=email_flow.email, email_verified=True)
                )
                await session.execute(q)
                # TODO: Check this line
                email_flow.finished = True
                await session.commit()
            else:
                raise EmailFlowNotFound()
