from typing import Annotated, Union

from src.app.actions import router
from src.app.dependencies import DEPENDS_BOT, DEPENDS_PG_STAT_REPOSITORY
from src.exceptions import IncorrectCredentialsException, NoCredentialsException, ArgumentRequiredException
from src.repositories.pg import AbstractPgRepository

from src.storages.monitoring.config import settings as monitoring_settings, Action
from src.exceptions import ActionNotFoundException


@router.post(
    "/execute/{action_alias}",
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

    # ensure all required arguments are provided
    for argument_name, argument in action.arguments.items():
        if argument.required and argument_name not in arguments:
            raise ArgumentRequiredException(argument_name)

    for step in action.steps:
        if step.type == Action.Step.Type.sql:
            await pg_repository.execute_sql(step.query, **arguments)
        elif step.type == Action.Step.Type.ssh:
            await pg_repository.execute_ssh(step.query, **arguments)


class ActionWithAlias(Action):
    alias: str


@router.get(
    "/",
    responses={
        200: {"description": "Execute action by alias"},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def get_actions(
    _bot: Annotated[bool, DEPENDS_BOT],
) -> list[ActionWithAlias]:
    return [
        ActionWithAlias(**action.dict(), alias=action_alias)
        for action_alias, action in
        monitoring_settings.actions.items()
    ]


@router.get(
    "/{action_alias}",
    responses={
        200: {"description": "Execute action by alias"},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def get_action(
    _bot: Annotated[bool, DEPENDS_BOT],
    action_alias: str,
) -> ActionWithAlias:
    action: Action = monitoring_settings.actions.get(action_alias, None)

    if action is None:
        raise ActionNotFoundException(action_alias)

    return ActionWithAlias(**action.model_dump(), alias=action_alias)
