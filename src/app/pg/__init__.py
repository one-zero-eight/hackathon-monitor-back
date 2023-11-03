__all__ = ["router"]

from fastapi import APIRouter

router = APIRouter(prefix="/pg", tags=["Postgres"])

# Register all schemas and routes
import src.schemas.pg_stats  # noqa: E402, F401
import src.app.pg.routes  # noqa: E402, F401
