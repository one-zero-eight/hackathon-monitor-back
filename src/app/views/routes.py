from typing import Annotated, Optional, Any

from pydantic import BaseModel, create_model

from src.app.dependencies import DEPENDS_BOT, DEPENDS_PG_STAT_REPOSITORY
from src.app.views import router
from src.exceptions import IncorrectCredentialsException, NoCredentialsException, ArgumentRequiredException
from src.repositories.pg import AbstractPgRepository
from src.storages.monitoring.config import settings as monitoring_settings, View


class ViewWithAlias(View):
    alias: str


@router.get(
    "/",
    responses={
        200: {"description": "Get all views"},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def get_views(
    _bot: Annotated[bool, DEPENDS_BOT],
):
    return [ViewWithAlias(**view.dict(), alias=view_alias) for view_alias, view in monitoring_settings.views.items()]


async def _execute_view(
    pg_repository: AbstractPgRepository, view_alias: str, **arguments
) -> Optional[list[dict[str, Any]]]:
    view: View = monitoring_settings.views.get(view_alias)
    # ensure all required arguments are provided
    for argument_name, argument in view.arguments.items():
        if argument.required and argument_name not in arguments:
            raise ArgumentRequiredException(argument_name)

    rows = await pg_repository.execute_sql(view.sql, True, **arguments)

    return rows


# generate routes for each action
for view_alias, view in monitoring_settings.views.items():
    _arguments = {
        argument_name: (argument.type, argument.field_info()) for argument_name, argument in view.arguments.items()
    }
    # for type hints
    _Arguments: type[BaseModel] = create_model(f"Arguments_{view_alias}", **_arguments)

    def wrapper(binded_view_alias: str):
        # for function closure (to pass action_alias)
        async def execute_action(
            _bot: Annotated[bool, DEPENDS_BOT],
            pg_repository: Annotated[AbstractPgRepository, DEPENDS_PG_STAT_REPOSITORY],
            arguments: _Arguments,
        ):
            arguments: BaseModel
            return await _execute_view(pg_repository, binded_view_alias, **arguments.model_dump(exclude_none=True))

        return execute_action

    router.add_api_route(
        f"/execute/{view_alias}",
        wrapper(view_alias),
        methods=["POST"],
        responses={
            200: {"description": "Get view by alias with arguments"},
            **IncorrectCredentialsException.responses,
            **NoCredentialsException.responses,
        },
        name=f"Get View {view_alias}",
        response_model=list[dict[str, Any]],
    )
