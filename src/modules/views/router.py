__all__ = ["router"]

from typing import Annotated, Optional, Any

from fastapi import APIRouter
from fastapi import Query

from src.api.dependencies import DEPENDS_PG_STAT_REPOSITORY, DEPENDS_VERIFIED_REQUEST
from src.config import Target, settings
from src.api.exceptions import (
    IncorrectCredentialsException,
    NoCredentialsException,
    ViewNotFoundException,
    SQLQueryError,
)
from src.modules.auth.schemas import VerificationResult
from src.modules.pg.abc import AbstractPgRepository
from src.storages.monitoring.config import settings as monitoring_settings, View
from src.api.utils import permission_check

router = APIRouter(prefix="/views", tags=["Views"])


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
    _verification: Annotated[VerificationResult, DEPENDS_VERIFIED_REQUEST],
) -> list[ViewWithAlias]:
    return [ViewWithAlias(**view.dict(), alias=view_alias) for view_alias, view in monitoring_settings.views.items()]


@router.get(
    "/{view_alias}",
    responses={
        200: {"description": "Execute action by alias"},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def get_view(
    _verification: Annotated[VerificationResult, DEPENDS_VERIFIED_REQUEST],
    view_alias: str,
) -> ViewWithAlias:
    view: View = monitoring_settings.views.get(view_alias, None)

    if view is None:
        raise ViewNotFoundException(view_alias)

    return ViewWithAlias(**view.model_dump(), alias=view_alias)


async def _execute_view(
    pg_repository: AbstractPgRepository, view_alias: str, limit: int, offset, target: Target
) -> Optional[list[dict[str, Any]]]:
    view: View = monitoring_settings.views.get(view_alias)

    rows = await pg_repository.execute_sql_select(view.sql, limit=limit, offset=offset, target=target)
    return rows


# generate routes for each action
for view_alias, view in monitoring_settings.views.items():

    def wrapper(binded_view_alias: str):
        # for function closure (to pass action_alias)
        async def execute_view(
            _verification: Annotated[VerificationResult, DEPENDS_VERIFIED_REQUEST],
            pg_repository: Annotated[AbstractPgRepository, DEPENDS_PG_STAT_REPOSITORY],
            limit: int = 20,
            offset: int = 0,
            target_alias: str = Query(...),
        ):
            target = settings.TARGETS[target_alias]
            permission_check(_verification, target)
            return await _execute_view(pg_repository, binded_view_alias, limit=limit, offset=offset, target=target)

        return execute_view

    router.add_api_route(
        f"/execute/{view_alias}",
        wrapper(view_alias),
        methods=["GET"],
        responses={
            200: {"description": "Get view by alias with arguments"},
            **IncorrectCredentialsException.responses,
            **NoCredentialsException.responses,
            **SQLQueryError.responses,
        },
        name=f"Get View {view_alias}",
        response_model=list[dict[str, Any]],
    )
