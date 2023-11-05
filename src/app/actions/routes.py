from types import NoneType
from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, create_model

from src.app.actions import router
from src.app.dependencies import DEPENDS_PG_STAT_REPOSITORY, DEPENDS_VERIFIED_REQUEST
from src.config import settings, Target
from src.exceptions import (
    ActionNotFoundException,
    IncorrectCredentialsException,
    NoCredentialsException,
    ArgumentRequiredException,
)
from src.repositories.pg import AbstractPgRepository
from src.schemas.tokens import VerificationResult
from src.storages.monitoring.config import settings as monitoring_settings, Action


async def _execute_action(pg_repository: AbstractPgRepository, action_alias: str, target: Target, **arguments):
    action = monitoring_settings.actions.get(action_alias)
    # ensure all required arguments are provided
    for argument_name, argument in action.arguments.items():
        if argument.required and argument_name not in arguments:
            raise ArgumentRequiredException(argument_name)

    for step in action.steps:
        if step.type == Action.Step.Type.sql:
            await pg_repository.execute_sql(step.query, binds=arguments, target=target)
        elif step.type == Action.Step.Type.ssh:
            await pg_repository.execute_ssh(step.query, binds=arguments, target=target)


# generate routes for each action
for action_alias, action in monitoring_settings.actions.items():
    _arguments = {
        argument_name: (argument.type, argument.field_info()) for argument_name, argument in action.arguments.items()
    }
    # for type hints
    _Arguments: type[BaseModel] = create_model(f"Arguments_{action_alias}", **_arguments)

    def wrapper(binded_action_alias: str):
        # for function closure (to pass action_alias)
        async def execute_action(
            _verification: Annotated[VerificationResult, DEPENDS_VERIFIED_REQUEST],
            pg_repository: Annotated[AbstractPgRepository, DEPENDS_PG_STAT_REPOSITORY],
            arguments: _Arguments,
            target_alias: str = Query(...),
        ):
            arguments: BaseModel
            target: Target = settings.TARGETS[target_alias]
            return await _execute_action(
                pg_repository, binded_action_alias, **arguments.model_dump(exclude_none=True), target=target
            )

        return execute_action

    router.add_api_route(
        f"/execute/{action_alias}",
        wrapper(action_alias),
        methods=["POST"],
        responses={
            200: {"description": "Execute action by alias with arguments"},
            **IncorrectCredentialsException.responses,
            **NoCredentialsException.responses,
        },
        name=f"Execute Action {action_alias}",
        response_model=NoneType,
    )


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
    _verification: Annotated[VerificationResult, DEPENDS_VERIFIED_REQUEST],
) -> list[ActionWithAlias]:
    return [
        ActionWithAlias(**action.dict(), alias=action_alias)
        for action_alias, action in monitoring_settings.actions.items()
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
    _verification: Annotated[VerificationResult, DEPENDS_VERIFIED_REQUEST],
    action_alias: str,
) -> ActionWithAlias:
    action: Action = monitoring_settings.actions.get(action_alias, None)

    if action is None:
        raise ActionNotFoundException(action_alias)

    return ActionWithAlias(**action.model_dump(), alias=action_alias)
