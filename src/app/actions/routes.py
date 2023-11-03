from typing import Annotated, Union

from src.app.actions import router
from src.app.dependencies import DEPENDS_BOT, DEPENDS_PG_STAT_REPOSITORY
from src.exceptions import IncorrectCredentialsException, NoCredentialsException
from src.repositories.pg import AbstractPgRepository

from src.storages.monitoring.config import settings as monitoring_settings, Action
from src.exceptions import ActionNotFoundException


@router.post(
    "/execute-action/{action_alias}",
    responses={
        200: {"description": "Execute action by alias"},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def execute_action(
    _bot: Annotated[bool, DEPENDS_BOT],
    pg_repository: Annotated[AbstractPgRepository, DEPENDS_PG_STAT_REPOSITORY],
    action_alias: str,
    arguments: dict[str, Union[str, int, float, bool]] = None,
):
    action: Action = monitoring_settings.actions.get(action_alias, None)

    if action is None:
        raise ActionNotFoundException(action_alias)

    if arguments is None:
        arguments = dict()

    for step in action.steps:
        if step.type == Action.Step.Type.sql:
            await pg_repository.execute_sql(step.query, **arguments)
        elif step.type == Action.Step.Type.ssh:
            await pg_repository.execute_ssh(step.query, **arguments)


@router.get(
    "/actions/",
    responses={
        200: {"description": "Execute action by alias"},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def get_actions(
    _bot: Annotated[bool, DEPENDS_BOT],
) -> dict[str, Action]:
    return monitoring_settings.actions
