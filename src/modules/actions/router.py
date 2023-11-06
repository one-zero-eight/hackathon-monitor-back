__all__ = ["router"]

from typing import Annotated

from fastapi import APIRouter, Query
from pydantic import BaseModel, create_model

from src.api.dependencies import DEPENDS_PG_STAT_REPOSITORY, DEPENDS_VERIFIED_REQUEST
from src.config import settings, Target
from src.api.exceptions import (
    ActionNotFoundException,
    IncorrectCredentialsException,
    NoCredentialsException,
    ArgumentRequiredException,
    SQLQueryError,
    SSHQueryError,
)
from src.modules.pg.abc import AbstractPgRepository
from src.modules.auth.schemas import VerificationResult
from src.storages.monitoring.config import settings as monitoring_settings, Action
from src.api.utils import permission_check

router = APIRouter(prefix="/actions", tags=["Actions"])


class SomeResult(BaseModel):
    success: bool = True
    detail: str = ""


async def _execute_action(pg_repository: AbstractPgRepository, action_alias: str, target: Target, **arguments):
    action = monitoring_settings.actions.get(action_alias)
    # ensure all required arguments are provided
    for argument_name, argument in action.arguments.items():
        if argument.required and argument_name not in arguments:
            raise ArgumentRequiredException(argument_name)
    exceptions = []

    for step in action.steps:
        try:
            if step.type == Action.Step.Type.sql:
                await pg_repository.execute_sql(step.query, binds=arguments, target=target)
            elif step.type == Action.Step.Type.ssh:
                await pg_repository.execute_ssh(step.query, binds=arguments, target=target)
        except (SQLQueryError, SSHQueryError) as e:
            if step.required:
                return SomeResult(
                    success=False,
                    detail=f"{step.query}: {e.__class__.__name__}: {e.detail}",
                )
            exceptions.append((step, e))

    if exceptions:
        detail = []
        for step, e in exceptions:
            detail.append(f"{step.query}: {e.__class__.__name__}: {e.detail}")

        return SomeResult(
            success=True,
            detail="\n".join([f"{e.__class__.__name__}: {e.detail}" for step, e in exceptions]),
        )

    return SomeResult()


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
            arguments: _Arguments | None = None,
            target_alias: str = Query(...),
        ):
            arguments: BaseModel
            target: Target = settings.TARGETS[target_alias]
            permission_check(_verification, target)
            return await _execute_action(
                pg_repository, binded_action_alias, **arguments.model_dump(exclude_none=True), target=target
            )

        return execute_action

    router.add_api_route(
        f"/execute/{action_alias}",
        wrapper(action_alias),
        methods=["POST"],
        responses={
            200: {"description": "Execute action"},
            **IncorrectCredentialsException.responses,
            **NoCredentialsException.responses,
        },
        name=f"Execute Action {action_alias}",
        response_model=SomeResult,
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
        200: {"description": "Get action by alias"},
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
